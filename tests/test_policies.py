"""Unit tests for policy enforcement engine."""

import pytest
from agentshield.policies import PolicyEngine, PolicyViolationError, validate_policy
from agentshield.models import PolicyConfig, ExecutionTrace, ToolCall


def test_policy_engine_allowlist():
    """Test that policy engine enforces tool allowlist."""
    policy = PolicyConfig(allowed_tools=["read_tool", "write_tool"])
    engine = PolicyEngine(policy)
    
    # Allowed tool
    assert engine.validate_tool_call("read_tool", {"path": "/tmp/file"}) is True
    
    # Not in allowlist
    with pytest.raises(PolicyViolationError, match="not in the allowed tools list"):
        engine.validate_tool_call("delete_tool", {})


def test_policy_engine_denylist():
    """Test that policy engine enforces tool denylist."""
    policy = PolicyConfig(prohibited_tools=["delete_database", "execute_shell"])
    engine = PolicyEngine(policy)
    
    # Not in denylist
    assert engine.validate_tool_call("read_tool", {"path": "/tmp/file"}) is True
    
    # In denylist
    with pytest.raises(PolicyViolationError, match="is prohibited by policy"):
        engine.validate_tool_call("delete_database", {"db": "test"})


def test_policy_engine_both_lists():
    """Test policy engine with both allowlist and denylist."""
    policy = PolicyConfig(
        allowed_tools=["read_tool", "write_tool"],
        prohibited_tools=["delete_tool"]
    )
    engine = PolicyEngine(policy)
    
    # In allowlist, not in denylist
    assert engine.validate_tool_call("read_tool", {}) is True
    
    # Not in allowlist
    with pytest.raises(PolicyViolationError, match="not in the allowed tools list"):
        engine.validate_tool_call("calculate_tool", {})
    
    # In denylist
    with pytest.raises(PolicyViolationError, match="is prohibited by policy"):
        engine.validate_tool_call("delete_tool", {})


def test_policy_engine_no_lists():
    """Test policy engine with no allowlist or denylist (permissive)."""
    policy = PolicyConfig()
    engine = PolicyEngine(policy)
    
    # All tools allowed
    assert engine.validate_tool_call("any_tool", {}) is True
    assert engine.validate_tool_call("dangerous_tool", {}) is True


def test_policy_engine_step_limit():
    """Test that policy engine enforces step limit."""
    policy = PolicyConfig(max_steps=5)
    engine = PolicyEngine(policy)
    
    # Within limit
    assert engine.validate_execution_limits(3, 1.0) is True
    
    # At limit
    assert engine.validate_execution_limits(5, 1.0) is True
    
    # Exceeds limit
    with pytest.raises(PolicyViolationError, match="Step limit exceeded"):
        engine.validate_execution_limits(6, 1.0)


def test_policy_engine_duration_limit():
    """Test that policy engine enforces duration limit."""
    policy = PolicyConfig(max_duration_seconds=10.0)
    engine = PolicyEngine(policy)
    
    # Within limit
    assert engine.validate_execution_limits(1, 5.0) is True
    
    # At limit
    assert engine.validate_execution_limits(1, 10.0) is True
    
    # Exceeds limit
    with pytest.raises(PolicyViolationError, match="Duration limit exceeded"):
        engine.validate_execution_limits(1, 15.0)


def test_policy_engine_tool_call_limit():
    """Test that policy engine enforces tool call limit."""
    policy = PolicyConfig(max_tool_calls=3)
    engine = PolicyEngine(policy)
    
    # Within limit
    assert engine.validate_tool_call_limit(2) is True
    
    # At limit
    assert engine.validate_tool_call_limit(3) is True
    
    # Exceeds limit
    with pytest.raises(PolicyViolationError, match="Tool call limit exceeded"):
        engine.validate_tool_call_limit(4)


def test_policy_engine_redact_sensitive_values():
    """Test sensitive value redaction."""
    policy = PolicyConfig(sensitive_values_to_redact=["sk-12345", "password123"])
    engine = PolicyEngine(policy)
    
    text = "API key: sk-12345 and password: password123"
    redacted = engine.redact_sensitive_values(text)
    
    assert "sk-12345" not in redacted
    assert "password123" not in redacted
    assert "[REDACTED]" in redacted
    # Note: password pattern may also match "password:"


def test_policy_engine_redact_patterns():
    """Test pattern-based redaction."""
    policy = PolicyConfig()
    engine = PolicyEngine(policy)
    
    # API key pattern
    text = "Key: sk-abcdefghijklmnopqrstuvwxyz123456"
    redacted = engine.redact_sensitive_values(text)
    assert "[REDACTED]" in redacted
    assert "sk-" not in redacted or redacted.count("sk-") < text.count("sk-")
    
    # Password pattern
    text = "Config: password=secret123"
    redacted = engine.redact_sensitive_values(text)
    assert "password=[REDACTED]" in redacted
    assert "secret123" not in redacted


def test_policy_engine_redact_trace():
    """Test redaction of execution trace."""
    policy = PolicyConfig(sensitive_values_to_redact=["sk-12345"])
    engine = PolicyEngine(policy)
    
    tool_call = ToolCall(
        name="api_tool",
        arguments={"key": "sk-12345"},
        result="Success with key sk-12345",
    )
    
    trace = ExecutionTrace(
        tool_calls=[tool_call],
        final_output="Used key sk-12345",
    )
    
    redacted_trace = engine.redact_trace(trace)
    
    assert "sk-12345" not in redacted_trace.final_output
    assert "sk-12345" not in str(redacted_trace.tool_calls[0].arguments)
    assert "sk-12345" not in redacted_trace.tool_calls[0].result


def test_policy_engine_counters():
    """Test step and tool call counters."""
    policy = PolicyConfig()
    engine = PolicyEngine(policy)
    
    assert engine.get_step_count() == 0
    assert engine.get_tool_call_count() == 0
    
    engine.increment_step_count()
    engine.increment_step_count()
    assert engine.get_step_count() == 2
    
    engine.increment_tool_call_count()
    assert engine.get_tool_call_count() == 1
    
    engine.reset_counters()
    assert engine.get_step_count() == 0
    assert engine.get_tool_call_count() == 0


def test_policy_engine_duration_tracking():
    """Test duration tracking."""
    import time
    
    policy = PolicyConfig()
    engine = PolicyEngine(policy)
    
    engine.start_execution()
    time.sleep(0.1)
    duration = engine.get_duration_seconds()
    
    assert duration >= 0.1
    assert duration < 0.5  # Should be quick


def test_validate_policy():
    """Test policy configuration validation."""
    # Valid policy
    policy = PolicyConfig(
        allowed_tools=["read_tool"],
        prohibited_tools=["delete_tool"],
        max_steps=10,
    )
    errors = validate_policy(policy)
    assert len(errors) == 0
    
    # Overlapping allowlist and denylist
    policy = PolicyConfig(
        allowed_tools=["read_tool", "delete_tool"],
        prohibited_tools=["delete_tool"],
    )
    errors = validate_policy(policy)
    assert len(errors) > 0
    assert "both" in errors[0].lower() and "allowlist" in errors[0].lower()
    
    # Invalid limits
    policy = PolicyConfig(max_steps=0)
    errors = validate_policy(policy)
    assert len(errors) > 0
    
    policy = PolicyConfig(max_duration_seconds=-1.0)
    errors = validate_policy(policy)
    assert len(errors) > 0


def test_policy_violation_error():
    """Test PolicyViolationError exception."""
    error = PolicyViolationError("Test violation")
    assert str(error) == "Test violation"
    assert isinstance(error, Exception)
