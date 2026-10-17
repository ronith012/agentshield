"""Test runner for AgentShield.

This module implements the test execution engine that orchestrates test cases,
enforces policies, collects results, and handles timeouts.
"""

import signal
import time
from contextlib import contextmanager
from typing import Any

from agentshield.adapters import AgentAdapter
from agentshield.models import (
    AgentTestCase as TestCase,
)
from agentshield.models import (
    AgentTestResult as TestResult,
)
from agentshield.models import (
    AgentTestSuiteResult as TestSuiteResult,
)
from agentshield.models import (
    ExecutionTrace,
    PolicyConfig,
    TestCategory,
    TestStatus,
)
from agentshield.policies import PolicyEngine, PolicyViolationError


class TestTimeoutError(Exception):
    """Raised when a test exceeds its timeout."""

    pass


class TestRunner:
    """Engine for running tests against agents.

    The test runner:
    - Orchestrates test execution
    - Enforces execution limits (steps, duration, tool calls)
    - Captures execution traces and metrics
    - Distinguishes between test failures and execution errors
    - Records test configuration, outcomes, metadata, and evidence
    """

    def __init__(self, policy: PolicyConfig):
        """Initialize the test runner with a policy configuration.

        Args:
            policy: The policy configuration to enforce during tests
        """
        self.policy = policy
        self.policy_engine = PolicyEngine(policy)

    def run_test(
        self, test_case: TestCase, agent: AgentAdapter, tools: dict[str, Any], num_trials: int = 1
    ) -> TestResult:
        """Run a single test case against an agent.

        For nondeterministic agents, run multiple trials and aggregate results.

        Args:
            test_case: The test case to execute
            agent: The agent to test
            tools: Dictionary of available tools
            num_trials: Number of trials to run for nondeterministic agents (k-trial approach)

        Returns:
            TestResult containing the outcome of the test
        """
        if num_trials > 1:
            return self._run_k_trial_test(test_case, agent, tools, num_trials)
        else:
            return self._run_single_test(test_case, agent, tools)

    def _run_single_test(
        self, test_case: TestCase, agent: AgentAdapter, tools: dict[str, Any]
    ) -> TestResult:
        """Run a single test case against an agent.

        Args:
            test_case: The test case to execute
            agent: The agent to test
            tools: Dictionary of available tools

        Returns:
            TestResult containing the outcome of the test
        """
        start_time = time.time()

        try:
            # Run with timeout
            execution_trace = self._run_with_timeout(
                test_case, agent, tools, test_case.timeout_seconds
            )

            # Evaluate assertions
            passed = self._evaluate_assertions(test_case, execution_trace)

            if passed:
                status = TestStatus.PASSED
                failure_reason = None
            else:
                status = TestStatus.FAILED
                failure_reason = "Assertions failed"

            duration = time.time() - start_time

            return TestResult(
                test_id=test_case.id,
                status=status,
                execution_trace=execution_trace,
                failure_reason=failure_reason,
                duration_seconds=duration,
                evidence={
                    "tool_calls": len(execution_trace.tool_calls),
                    "steps_taken": execution_trace.steps_taken,
                    "final_output": execution_trace.final_output,
                },
            )

        except TestTimeoutError:
            duration = time.time() - start_time
            return TestResult(
                test_id=test_case.id,
                status=TestStatus.ERROR,
                execution_trace=ExecutionTrace(error="Test timeout"),
                error_message=f"Test exceeded timeout of {test_case.timeout_seconds}s",
                duration_seconds=duration,
            )

        except PolicyViolationError as e:
            duration = time.time() - start_time
            return TestResult(
                test_id=test_case.id,
                status=TestStatus.FAILED,
                execution_trace=ExecutionTrace(error=str(e)),
                failure_reason=f"Policy violation: {str(e)}",
                duration_seconds=duration,
                evidence={"policy_violation": str(e)},
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_id=test_case.id,
                status=TestStatus.ERROR,
                execution_trace=ExecutionTrace(error=str(e)),
                error_message=f"Execution error: {str(e)}",
                duration_seconds=duration,
            )

    def _run_k_trial_test(
        self, test_case: TestCase, agent: AgentAdapter, tools: dict[str, Any], k: int
    ) -> TestResult:
        """Run a test case multiple times and aggregate results (k-trial approach).

        For nondeterministic agents, run the test k times and determine the final status
        based on majority voting or consistency checks.

        Args:
            test_case: The test case to execute
            agent: The agent to test
            tools: Dictionary of available tools
            k: Number of trials to run

        Returns:
            TestResult containing the aggregated outcome
        """
        results = []
        total_duration = 0.0

        for i in range(k):
            result = self._run_single_test(test_case, agent, tools)
            results.append(result)
            total_duration += result.duration_seconds

        # Aggregate results
        passed_count = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed_count = sum(1 for r in results if r.status == TestStatus.FAILED)
        error_count = sum(1 for r in results if r.status == TestStatus.ERROR)

        # Determine final status
        if passed_count == k:
            # All trials passed
            final_status = TestStatus.PASSED
            final_trace = results[0].execution_trace
            failure_reason = None
            error_message = None
        elif error_count == k:
            # All trials had errors
            final_status = TestStatus.ERROR
            final_trace = results[0].execution_trace
            failure_reason = None
            error_message = f"All {k} trials encountered errors"
        elif failed_count == k:
            # All trials failed
            final_status = TestStatus.FAILED
            final_trace = results[0].execution_trace
            failure_reason = f"All {k} trials failed"
            error_message = None
        elif passed_count >= k / 2:
            # Majority passed
            final_status = TestStatus.PASSED
            final_trace = results[0].execution_trace
            failure_reason = None
            error_message = None
        else:
            # Inconsistent results
            final_status = TestStatus.FAILED
            final_trace = results[0].execution_trace
            failure_reason = f"Inconsistent results across {k} trials: {passed_count} passed, {failed_count} failed, {error_count} errors"
            error_message = None

        return TestResult(
            test_id=test_case.id,
            status=final_status,
            execution_trace=final_trace,
            failure_reason=failure_reason,
            error_message=error_message,
            duration_seconds=total_duration / k,
            evidence={
                "k_trials": k,
                "passed_count": passed_count,
                "failed_count": failed_count,
                "error_count": error_count,
                "individual_results": [r.status.value for r in results],
            },
        )

    def _run_with_timeout(
        self,
        test_case: TestCase,
        agent: AgentAdapter,
        tools: dict[str, Any],
        timeout_seconds: float,
    ) -> ExecutionTrace:
        """Run a test with a timeout.

        Args:
            test_case: The test case to execute
            agent: The agent to test
            tools: Dictionary of available tools
            timeout_seconds: Maximum execution time

        Returns:
            ExecutionTrace from the agent execution

        Raises:
            TestTimeoutError: If the test exceeds the timeout
        """

        def timeout_handler(signum, frame):
            raise TestTimeoutError("Test execution timed out")

        # Set signal handler for timeout (Unix only)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout_seconds))

            trace = agent.execute(test_case.input, tools, self.policy)

            signal.alarm(0)  # Cancel alarm
            return trace

        except (ValueError, AttributeError):
            # Signal not available (e.g., Windows), use alternative approach
            # For now, just run without signal-based timeout
            return agent.execute(test_case.input, tools, self.policy)

    def _evaluate_assertions(self, test_case: TestCase, trace: ExecutionTrace) -> bool:
        """Evaluate test assertions against the execution trace.

        Args:
            test_case: The test case with assertions
            trace: The execution trace to evaluate against

        Returns:
            True if all assertions pass, False otherwise
        """
        passed_count = 0
        for assertion in test_case.assertions:
            if self._evaluate_single_assertion(assertion, trace):
                passed_count += 1

        # All assertions must pass for MVP
        return passed_count == len(test_case.assertions)

    def _evaluate_single_assertion(self, assertion: str, trace: ExecutionTrace) -> bool:
        """Evaluate a single assertion.

        Args:
            assertion: The assertion string
            trace: The execution trace

        Returns:
            True if the assertion passes, False otherwise
        """
        # Simple assertion evaluation for MVP
        # In a full implementation, this would support more complex assertion types

        # Check if output contains expected text
        if "contains" in assertion.lower():
            expected = assertion.split("contains")[-1].strip().strip("'\"")
            if trace.final_output and expected in trace.final_output:
                return True

        # Check if tool was called
        if "tool call" in assertion.lower():
            tool_name = assertion.split("tool call")[-1].strip().strip("'\"")
            for tool_call in trace.tool_calls:
                if tool_call.name == tool_name:
                    return True

        # Check if no error occurred
        if "no error" in assertion.lower():
            return trace.error is None

        # Default: simple string matching
        if trace.final_output and assertion in trace.final_output:
            return True

        return False

    def run_test_suite(
        self,
        test_cases: list[TestCase],
        agent: AgentAdapter,
        tools: dict[str, Any],
        category_filter: TestCategory | None = None,
        num_trials: int = 1,
    ) -> TestSuiteResult:
        """Run a suite of test cases against an agent.

        Args:
            test_cases: List of test cases to run
            agent: The agent to test
            tools: Dictionary of available tools
            category_filter: Optional filter to run only specific category
            num_trials: Number of trials for nondeterministic agents

        Returns:
            TestSuiteResult containing aggregated results
        """
        start_time = time.time()

        # Filter by category if specified
        if category_filter:
            test_cases = [tc for tc in test_cases if tc.category == category_filter]

        results = []
        passed = 0
        failed = 0
        errors = 0
        skipped = 0

        for test_case in test_cases:
            result = self.run_test(test_case, agent, tools, num_trials)
            results.append(result)

            if result.status == TestStatus.PASSED:
                passed += 1
            elif result.status == TestStatus.FAILED:
                failed += 1
            elif result.status == TestStatus.ERROR:
                errors += 1
            elif result.status == TestStatus.SKIPPED:
                skipped += 1

        total_duration = time.time() - start_time

        # Separate results by category
        reliability_results = [
            r
            for r in results
            if any(
                tc.category == TestCategory.RELIABILITY for tc in test_cases if tc.id == r.test_id
            )
        ]
        security_results = [
            r
            for r in results
            if any(tc.category == TestCategory.SECURITY for tc in test_cases if tc.id == r.test_id)
        ]

        return TestSuiteResult(
            total_tests=len(test_cases),
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            reliability_results=reliability_results,
            security_results=security_results,
            total_duration_seconds=total_duration,
        )


@contextmanager
def policy_enforcement(agent: AgentAdapter, policy: PolicyConfig, tools: dict[str, Any]):
    """Context manager for enforcing policy during agent execution.

    This intercepts tool calls and validates them against policy before execution.

    Args:
        agent: The agent to execute
        policy: The policy to enforce
        tools: Dictionary of available tools

    Yields:
        A wrapped execution context with policy enforcement
    """
    policy_engine = PolicyEngine(policy)
    policy_engine.start_execution()

    # Wrap tools to enforce policy before execution
    wrapped_tools = {}
    for tool_name, tool_func in tools.items():

        def make_wrapper(name, func, engine):
            def wrapped_tool(*args, **kwargs):
                # Validate tool call before execution
                engine.validate_tool_call(name, kwargs)
                engine.increment_tool_call_count()
                engine.validate_tool_call_limit(engine.get_tool_call_count())

                # Execute the actual tool
                result = func(*args, **kwargs)

                engine.increment_step_count()
                engine.validate_execution_limits(
                    engine.get_step_count(), engine.get_duration_seconds()
                )

                return result

            return wrapped_tool

        wrapped_tools[tool_name] = make_wrapper(tool_name, tool_func, policy_engine)

    try:
        yield wrapped_tools, policy_engine
    finally:
        policy_engine.reset_counters()
