"""Unit tests for test runner."""

import pytest
from agentshield.runner import TestRunner, TestTimeoutError, policy_enforcement
from agentshield.adapters import AgentAdapter
from agentshield.models import (
    PolicyConfig,
    ExecutionTrace,
    AgentTestCase as TestCase,
    AgentTestResult as TestResult,
    TestStatus,
    TestCategory,
)
from agentshield.policies import PolicyViolationError


class SimpleAgent(AgentAdapter):
    """A simple test agent."""
    
    def execute(self, input: str, tools: dict, policy: PolicyConfig) -> ExecutionTrace:
        trace = ExecutionTrace(
            steps_taken=1,
            duration_seconds=0.1,
            final_output=f"Processed: {input}",
        )
        return trace
    
    def get_name(self) -> str:
        return "simple_agent"


class FailingAgent(AgentAdapter):
    """An agent that always fails."""
    
    def execute(self, input: str, tools: dict, policy: PolicyConfig) -> ExecutionTrace:
        raise RuntimeError("Agent execution failed")
    
    def get_name(self) -> str:
        return "failing_agent"


def test_runner_initialization():
    """Test test runner initialization."""
    policy = PolicyConfig()
    runner = TestRunner(policy)
    
    assert runner.policy == policy
    assert runner.policy_engine is not None


def test_runner_run_test_success():
    """Test running a successful test."""
    policy = PolicyConfig()
    runner = TestRunner(policy)
    agent = SimpleAgent()
    
    test_case = TestCase(
        id="TEST-001",
        name="Test",
        description="A test",
        category=TestCategory.RELIABILITY,
        input="test input",
        expected_behavior="Process input",
        assertions=["contains test"],
    )
    
    result = runner.run_test(test_case, agent, {})
    
    assert result.test_id == "TEST-001"
    assert result.status == TestStatus.PASSED
    assert result.failure_reason is None
    assert result.error_message is None
    assert result.execution_trace.final_output == "Processed: test input"


def test_runner_run_test_failure():
    """Test running a failing test."""
    policy = PolicyConfig()
    runner = TestRunner(policy)
    agent = SimpleAgent()
    
    test_case = TestCase(
        id="TEST-002",
        name="Test",
        description="A test",
        category=TestCategory.RELIABILITY,
        input="test input",
        expected_behavior="Process input",
        assertions=["contains nonexistent"],
    )
    
    result = runner.run_test(test_case, agent, {})
    
    assert result.test_id == "TEST-002"
    assert result.status == TestStatus.FAILED
    assert result.failure_reason == "Assertions failed"
    assert result.error_message is None


def test_runner_run_test_error():
    """Test running a test that encounters an execution error."""
    policy = PolicyConfig()
    runner = TestRunner(policy)
    agent = FailingAgent()
    
    test_case = TestCase(
        id="TEST-003",
        name="Test",
        description="A test",
        category=TestCategory.RELIABILITY,
        input="test input",
        expected_behavior="Process input",
        assertions=["contains test"],
    )
    
    result = runner.run_test(test_case, agent, {})
    
    assert result.test_id == "TEST-003"
    assert result.status == TestStatus.ERROR
    assert result.error_message is not None
    assert "execution error" in result.error_message.lower()


def test_runner_assertion_evaluation():
    """Test assertion evaluation logic."""
    policy = PolicyConfig()
    runner = TestRunner(policy)
    
    trace = ExecutionTrace(
        final_output="The result is 42",
        steps_taken=1,
    )
    
    test_case = TestCase(
        id="TEST-004",
        name="Test",
        description="A test",
        category=TestCategory.RELIABILITY,
        input="test",
        expected_behavior="Process",
        assertions=["contains 42"],
    )
    
    passed = runner._evaluate_assertions(test_case, trace)
    assert passed is True
    
    test_case.assertions = ["contains 99"]
    passed = runner._evaluate_assertions(test_case, trace)
    assert passed is False


def test_runner_run_test_suite():
    """Test running a test suite."""
    policy = PolicyConfig()
    runner = TestRunner(policy)
    agent = SimpleAgent()
    
    test_cases = [
        TestCase(
            id="TEST-005",
            name="Test 1",
            description="Test 1",
            category=TestCategory.RELIABILITY,
            input="test 1",
            expected_behavior="Process",
            assertions=["contains test"],
        ),
        TestCase(
            id="TEST-006",
            name="Test 2",
            description="Test 2",
            category=TestCategory.RELIABILITY,
            input="test 2",
            expected_behavior="Process",
            assertions=["contains nonexistent"],
        ),
    ]
    
    suite_result = runner.run_test_suite(test_cases, agent, {})
    
    assert suite_result.total_tests == 2
    assert suite_result.passed == 1
    assert suite_result.failed == 1
    assert suite_result.errors == 0
    assert suite_result.skipped == 0


def test_runner_category_filter():
    """Test filtering test suite by category."""
    policy = PolicyConfig()
    runner = TestRunner(policy)
    agent = SimpleAgent()
    
    test_cases = [
        TestCase(
            id="TEST-007",
            name="Reliability Test",
            description="Test",
            category=TestCategory.RELIABILITY,
            input="test",
            expected_behavior="Process",
            assertions=["contains test"],
        ),
        TestCase(
            id="TEST-008",
            name="Security Test",
            description="Test",
            category=TestCategory.SECURITY,
            input="test",
            expected_behavior="Process",
            assertions=["contains test"],
        ),
    ]
    
    # Filter for reliability only
    suite_result = runner.run_test_suite(test_cases, agent, {}, category_filter=TestCategory.RELIABILITY)
    
    assert suite_result.total_tests == 1
    assert suite_result.passed == 1


def test_runner_evidence_collection():
    """Test that runner collects evidence in results."""
    policy = PolicyConfig()
    runner = TestRunner(policy)
    agent = SimpleAgent()
    
    test_case = TestCase(
        id="TEST-009",
        name="Test",
        description="A test",
        category=TestCategory.RELIABILITY,
        input="test input",
        expected_behavior="Process input",
        assertions=["contains test"],
    )
    
    result = runner.run_test(test_case, agent, {})
    
    assert "evidence" in result.model_dump()
    assert "tool_calls" in result.evidence
    assert "steps_taken" in result.evidence
    assert "final_output" in result.evidence


def test_policy_enforcement_context_manager():
    """Test the policy enforcement context manager."""
    policy = PolicyConfig(
        allowed_tools=["read_tool"],
        prohibited_tools=["delete_tool"],
    )
    
    agent = SimpleAgent()
    tools = {
        "read_tool": lambda x: f"Read: {x}",
        "delete_tool": lambda x: f"Deleted: {x}",
    }
    
    with policy_enforcement(agent, policy, tools) as (wrapped_tools, policy_engine):
        # Allowed tool should work
        result = wrapped_tools["read_tool"]("file.txt")
        assert result == "Read: file.txt"
        
        # Prohibited tool should raise PolicyViolationError
        with pytest.raises(PolicyViolationError, match="is prohibited by policy"):
            wrapped_tools["delete_tool"]("file.txt")


def test_policy_enforcement_tool_call_limit():
    """Test that policy enforcement enforces tool call limits."""
    policy = PolicyConfig(max_tool_calls=2)
    
    agent = SimpleAgent()
    tools = {"test_tool": lambda x: x}
    
    with policy_enforcement(agent, policy, tools) as (wrapped_tools, policy_engine):
        wrapped_tools["test_tool"]("1")
        wrapped_tools["test_tool"]("2")
        
        # Third call should exceed limit
        with pytest.raises(PolicyViolationError, match="Tool call limit exceeded"):
            wrapped_tools["test_tool"]("3")


def test_policy_enforcement_step_limit():
    """Test that policy enforcement enforces step limits."""
    policy = PolicyConfig(max_steps=2)
    
    agent = SimpleAgent()
    tools = {"test_tool": lambda x: x}
    
    with policy_enforcement(agent, policy, tools) as (wrapped_tools, policy_engine):
        # First call (step 1)
        wrapped_tools["test_tool"]("1")
        
        # Second call (step 2)
        wrapped_tools["test_tool"]("2")
        
        # Third call (step 3) should exceed limit
        with pytest.raises(PolicyViolationError, match="Step limit exceeded"):
            wrapped_tools["test_tool"]("3")


def test_runner_records_configuration():
    """Test that runner records test configuration."""
    policy = PolicyConfig(max_steps=5)
    runner = TestRunner(policy)
    agent = SimpleAgent()
    
    test_case = TestCase(
        id="TEST-010",
        name="Test",
        description="A test",
        category=TestCategory.RELIABILITY,
        input="test",
        expected_behavior="Process",
        assertions=["contains test"],
    )
    
    result = runner.run_test(test_case, agent, {})
    
    # Result should contain metadata from execution
    assert result.test_id == test_case.id
    assert result.execution_trace is not None
    assert result.duration_seconds >= 0
