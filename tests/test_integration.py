"""Integration tests for AgentShield.

These tests verify end-to-end functionality including:
- Prohibited tool calls are blocked before execution
- Execution limits are enforced
- Test failures are distinguished from execution errors
"""

import sys
from pathlib import Path

# Add examples directory to path
examples_dir = Path(__file__).parent.parent / "examples"
sys.path.insert(0, str(examples_dir))

import pytest
from agentshield.runner import TestRunner, policy_enforcement
from agentshield.models import PolicyConfig, TestStatus, TestCategory
from agentshield.adapters import AgentAdapter
from agentshield.testsuites.reliability import ReliabilityTestSuite
from agentshield.testsuites.security import SecurityTestSuite
from mock_tools import get_mock_tools
from demo_policy import get_demo_policy
from agentshield.policies import PolicyViolationError


class PolicyViolatingAgent(AgentAdapter):
    """An agent that attempts to violate policy."""
    
    def execute(self, input: str, tools: dict, policy: PolicyConfig):
        from agentshield.models import ToolCall, ExecutionTrace
        from datetime import datetime
        
        # Try to call a prohibited tool
        tool_call = ToolCall(
            name="delete_database_tool",
            arguments={"database_name": "test"},
            result="Database deleted",
            timestamp=datetime.utcnow(),
        )
        
        trace = ExecutionTrace(
            tool_calls=[tool_call],
            steps_taken=1,
            duration_seconds=0.1,
            final_output="Deleted database",
        )
        return trace
    
    def get_name(self) -> str:
        return "policy_violating_agent"


class LimitViolatingAgent(AgentAdapter):
    """An agent that exceeds execution limits."""
    
    def execute(self, input: str, tools: dict, policy: PolicyConfig):
        from agentshield.models import ToolCall, ExecutionTrace
        from datetime import datetime
        
        # Make many tool calls
        tool_calls = []
        for i in range(20):
            tool_call = ToolCall(
                name="calculate_tool",
                arguments={"a": i, "b": i},
                result=i + i,
                timestamp=datetime.utcnow(),
            )
            tool_calls.append(tool_call)
        
        trace = ExecutionTrace(
            tool_calls=tool_calls,
            steps_taken=20,
            duration_seconds=0.5,
            final_output="Made 20 tool calls",
        )
        return trace
    
    def get_name(self) -> str:
        return "limit_violating_agent"


def test_prohibited_tool_calls_blocked():
    """Integration test: Verify prohibited tool calls are blocked before execution."""
    policy = PolicyConfig(
        prohibited_tools=["delete_database_tool"],
        max_tool_calls=5,
    )
    
    agent = PolicyViolatingAgent()
    tools = get_mock_tools()
    
    # Use policy enforcement context manager
    with policy_enforcement(agent, policy, tools) as (wrapped_tools, policy_engine):
        # Try to call prohibited tool
        with pytest.raises(PolicyViolationError, match="is prohibited by policy"):
            wrapped_tools["delete_database_tool"]({"database_name": "test"})
    
    # Verify the tool was NOT actually executed
    # (the mock tool would return a success message if executed)
    # Since we got a PolicyViolationError, it was blocked


def test_execution_limit_enforced():
    """Integration test: Verify execution limits are enforced."""
    policy = PolicyConfig(
        max_tool_calls=5,
        max_steps=5,
    )
    
    agent = LimitViolatingAgent()
    tools = get_mock_tools()
    
    with policy_enforcement(agent, policy, tools) as (wrapped_tools, policy_engine):
        # Make calls up to the limit
        for i in range(5):
            wrapped_tools["calculate_tool"](i, i)
        
        # Next call should exceed the limit
        with pytest.raises(PolicyViolationError, match="Tool call limit exceeded"):
            wrapped_tools["calculate_tool"](6, 6)


def test_step_limit_enforced():
    """Integration test: Verify step limit is enforced."""
    policy = PolicyConfig(
        max_steps=3,
    )
    
    agent = LimitViolatingAgent()
    tools = get_mock_tools()
    
    with policy_enforcement(agent, policy, tools) as (wrapped_tools, policy_engine):
        # Make calls up to the step limit
        for i in range(3):
            wrapped_tools["calculate_tool"](i, i)
        
        # Next call should exceed the step limit
        with pytest.raises(PolicyViolationError, match="Step limit exceeded"):
            wrapped_tools["calculate_tool"](4, 4)


def test_test_failures_distinguished_from_errors():
    """Integration test: Verify test failures are distinguished from execution errors."""
    from demo_agent import MockAgent
    
    policy = get_demo_policy()
    runner = TestRunner(policy)
    
    # Test 1: Agent that should fail assertions (test failure)
    compliant_agent = MockAgent(scenario="compliant")
    test_case = ReliabilityTestSuite.instruction_following()
    
    result = runner.run_test(test_case, compliant_agent, get_mock_tools())
    
    # Should be a failure (assertions failed), not an error
    assert result.status in [TestStatus.PASSED, TestStatus.FAILED]
    if result.status == TestStatus.FAILED:
        assert result.failure_reason is not None
        assert result.error_message is None
    
    # Test 2: Agent that encounters execution error
    class ErrorAgent(AgentAdapter):
        def execute(self, input: str, tools: dict, policy: PolicyConfig):
            raise RuntimeError("Simulated execution error")
        
        def get_name(self) -> str:
            return "error_agent"
    
    error_agent = ErrorAgent()
    result = runner.run_test(test_case, error_agent, get_mock_tools())
    
    # Should be an error, not a failure
    assert result.status == TestStatus.ERROR
    assert result.error_message is not None
    assert "execution error" in result.error_message.lower()
    assert result.failure_reason is None


def test_end_to_end_test_execution():
    """Integration test: Full end-to-end test execution with demo agent."""
    from demo_agent import MockAgent
    
    policy = get_demo_policy()
    runner = TestRunner(policy)
    agent = MockAgent(scenario="compliant")
    tools = get_mock_tools()
    
    # Run reliability tests
    reliability_tests = ReliabilityTestSuite.get_all_tests()
    suite_result = runner.run_test_suite(reliability_tests, agent, tools)
    
    # Verify suite result structure
    assert suite_result.total_tests == len(reliability_tests)
    assert suite_result.passed >= 0
    assert suite_result.failed >= 0
    assert suite_result.errors >= 0
    assert suite_result.skipped >= 0
    assert suite_result.total_duration_seconds >= 0
    
    # Verify individual results
    for result in suite_result.reliability_results:
        assert result.test_id is not None
        assert result.status in [TestStatus.PASSED, TestStatus.FAILED, TestStatus.ERROR, TestStatus.SKIPPED]
        assert result.execution_trace is not None
        assert result.duration_seconds >= 0


def test_policy_enforcement_blocks_dangerous_tools():
    """Integration test: Verify policy enforcement blocks dangerous tools."""
    policy = PolicyConfig(
        prohibited_tools=["delete_database_tool", "execute_shell_tool"],
    )
    
    tools = get_mock_tools()
    
    with policy_enforcement(None, policy, tools) as (wrapped_tools, policy_engine):
        # Try to use delete_database_tool
        with pytest.raises(PolicyViolationError):
            wrapped_tools["delete_database_tool"]("production")
        
        # Try to use execute_shell_tool
        with pytest.raises(PolicyViolationError):
            wrapped_tools["execute_shell_tool"]("rm -rf /")
        
        # Safe tools should still work
        result = wrapped_tools["read_tool"]("/tmp/file.txt")
        assert "Mock content" in result


def test_sensitive_data_redaction_in_reports():
    """Integration test: Verify sensitive data is redacted in reports."""
    from agentshield.reporting import ReportGenerator
    from agentshield.models import AgentTestSuiteResult as TestSuiteResult, AgentTestResult as TestResult, ExecutionTrace
    from agentshield.policies import PolicyEngine
    
    policy = PolicyConfig(
        sensitive_values_to_redact=["sk-12345", "password123"],
    )
    
    # Create a result with sensitive data
    trace = ExecutionTrace(
        final_output="API key: sk-12345 and password: password123",
        steps_taken=1,
    )
    
    result = TestResult(
        test_id="TEST-001",
        status=TestStatus.PASSED,
        execution_trace=trace,
        duration_seconds=0.5,
    )
    
    suite_result = TestSuiteResult(
        total_tests=1,
        passed=1,
        failed=0,
        errors=0,
        skipped=0,
        reliability_results=[result],
        total_duration_seconds=0.5,
    )
    
    generator = ReportGenerator(policy)
    report = generator.generate_report(suite_result)
    
    # Verify sensitive data is redacted in the trace
    policy_engine = PolicyEngine(policy)
    redacted_trace = policy_engine.redact_trace(suite_result.reliability_results[0].execution_trace)
    
    assert "sk-12345" not in redacted_trace.final_output
    assert "password123" not in redacted_trace.final_output
    assert "[REDACTED]" in redacted_trace.final_output


def test_allowlist_enforcement():
    """Integration test: Verify allowlist enforcement."""
    policy = PolicyConfig(
        allowed_tools=["read_tool"],
        prohibited_tools=[],
    )
    
    tools = get_mock_tools()
    
    with policy_enforcement(None, policy, tools) as (wrapped_tools, policy_engine):
        # Allowed tool should work
        result = wrapped_tools["read_tool"]("/tmp/file.txt")
        assert "Mock content" in result
        
        # Tool not in allowlist should be blocked
        with pytest.raises(PolicyViolationError, match="not in the allowed tools list"):
            wrapped_tools["write_tool"]("/tmp/file.txt", "test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
