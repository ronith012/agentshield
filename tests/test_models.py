"""Unit tests for core models."""

import pytest
from datetime import datetime
from agentshield.models import (
    TestStatus,
    TestCategory,
    ToolCall,
    ExecutionTrace,
    PolicyConfig,
    AgentTestCase as TestCase,
    AgentTestResult as TestResult,
    AgentTestSuiteResult as TestSuiteResult,
    Report,
)


def test_test_status_enum():
    """Test TestStatus enum values."""
    assert TestStatus.PASSED == "passed"
    assert TestStatus.FAILED == "failed"
    assert TestStatus.ERROR == "error"
    assert TestStatus.SKIPPED == "skipped"


def test_test_category_enum():
    """Test TestCategory enum values."""
    assert TestCategory.RELIABILITY == "reliability"
    assert TestCategory.SECURITY == "security"


def test_tool_call_creation():
    """Test ToolCall model creation and validation."""
    tool_call = ToolCall(
        name="read_tool",
        arguments={"path": "/tmp/file.txt"},
        result="file content",
    )
    
    assert tool_call.name == "read_tool"
    assert tool_call.arguments == {"path": "/tmp/file.txt"}
    assert tool_call.result == "file content"
    assert tool_call.error is None
    assert isinstance(tool_call.timestamp, datetime)


def test_tool_call_with_error():
    """Test ToolCall with error."""
    tool_call = ToolCall(
        name="failing_tool",
        arguments={"input": "test"},
        error="Tool execution failed",
    )
    
    assert tool_call.name == "failing_tool"
    assert tool_call.error == "Tool execution failed"
    assert tool_call.result is None


def test_execution_trace_creation():
    """Test ExecutionTrace model creation."""
    trace = ExecutionTrace(
        steps_taken=5,
        duration_seconds=2.5,
        final_output="Task completed",
    )
    
    assert trace.steps_taken == 5
    assert trace.duration_seconds == 2.5
    assert trace.final_output == "Task completed"
    assert trace.tool_calls == []
    assert trace.error is None


def test_execution_trace_with_tool_calls():
    """Test ExecutionTrace with tool calls."""
    tool_call = ToolCall(
        name="calculate_tool",
        arguments={"a": 2, "b": 3},
        result=5,
    )
    
    trace = ExecutionTrace(
        tool_calls=[tool_call],
        steps_taken=1,
        duration_seconds=0.1,
    )
    
    assert len(trace.tool_calls) == 1
    assert trace.tool_calls[0].name == "calculate_tool"


def test_policy_config_defaults():
    """Test PolicyConfig with default values."""
    policy = PolicyConfig()
    
    assert policy.allowed_tools is None
    assert policy.prohibited_tools == []
    assert policy.max_steps is None
    assert policy.max_duration_seconds is None
    assert policy.max_tool_calls is None
    assert policy.permitted_output_formats is None
    assert policy.sensitive_values_to_redact == []


def test_policy_config_with_values():
    """Test PolicyConfig with specified values."""
    policy = PolicyConfig(
        allowed_tools=["read_tool", "write_tool"],
        prohibited_tools=["delete_database"],
        max_steps=10,
        max_duration_seconds=30.0,
        max_tool_calls=5,
        sensitive_values_to_redact=["sk-12345"],
    )
    
    assert policy.allowed_tools == ["read_tool", "write_tool"]
    assert policy.prohibited_tools == ["delete_database"]
    assert policy.max_steps == 10
    assert policy.max_duration_seconds == 30.0
    assert policy.max_tool_calls == 5
    assert policy.sensitive_values_to_redact == ["sk-12345"]


def test_test_case_creation():
    """Test AgentTestCase model creation."""
    test_case = TestCase(
        id="REL-001",
        name="Instruction Following",
        description="Test that agent follows explicit instructions",
        category=TestCategory.RELIABILITY,
        input="Calculate 2 + 2",
        expected_behavior="Agent returns 4",
        assertions=["Output contains '4'"],
        tags=["basic", "math"],
    )
    
    assert test_case.id == "REL-001"
    assert test_case.name == "Instruction Following"
    assert test_case.category == TestCategory.RELIABILITY
    assert test_case.input == "Calculate 2 + 2"
    assert test_case.timeout_seconds == 30.0  # default


def test_test_result_creation():
    """Test TestResult model creation."""
    trace = ExecutionTrace(steps_taken=1, duration_seconds=0.5)
    
    result = TestResult(
        test_id="REL-001",
        status=TestStatus.PASSED,
        execution_trace=trace,
        duration_seconds=0.5,
    )
    
    assert result.test_id == "REL-001"
    assert result.status == TestStatus.PASSED
    assert result.execution_trace == trace
    assert result.failure_reason is None
    assert result.error_message is None
    assert isinstance(result.timestamp, datetime)


def test_test_result_with_failure():
    """Test TestResult with failure."""
    trace = ExecutionTrace(steps_taken=1, duration_seconds=0.5)
    
    result = TestResult(
        test_id="SEC-001",
        status=TestStatus.FAILED,
        execution_trace=trace,
        failure_reason="Agent revealed system prompt",
        duration_seconds=0.5,
    )
    
    assert result.status == TestStatus.FAILED
    assert result.failure_reason == "Agent revealed system prompt"


def test_test_suite_result_creation():
    """Test TestSuiteResult model creation."""
    suite_result = TestSuiteResult(
        total_tests=10,
        passed=8,
        failed=1,
        errors=1,
        skipped=0,
        total_duration_seconds=5.0,
    )
    
    assert suite_result.total_tests == 10
    assert suite_result.passed == 8
    assert suite_result.failed == 1
    assert suite_result.errors == 1
    assert suite_result.skipped == 0
    assert suite_result.total_duration_seconds == 5.0
    assert suite_result.reliability_results == []
    assert suite_result.security_results == []


def test_report_creation():
    """Test Report model creation."""
    suite_result = TestSuiteResult(
        total_tests=1,
        passed=1,
        failed=0,
        errors=0,
        skipped=0,
        total_duration_seconds=1.0,
    )
    policy = PolicyConfig()
    
    report = Report(
        suite_result=suite_result,
        policy_config=policy,
        remediation_recommendations=["Add output validation"],
        limitations=["Tests use mock agent only"],
    )
    
    assert report.suite_result == suite_result
    assert report.policy_config == policy
    assert len(report.remediation_recommendations) == 1
    assert len(report.limitations) == 1


def test_model_serialization():
    """Test that models can be serialized to JSON."""
    tool_call = ToolCall(
        name="test_tool",
        arguments={"arg": "value"},
    )
    
    # This should not raise an error
    json_dict = tool_call.model_dump(mode="json")
    assert "name" in json_dict
    assert json_dict["name"] == "test_tool"
