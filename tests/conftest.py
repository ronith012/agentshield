"""Pytest configuration and fixtures for AgentShield tests."""

import pytest
from agentshield.models import (
    PolicyConfig,
    ExecutionTrace,
    TestStatus,
    TestCategory,
)


@pytest.fixture
def sample_policy_config():
    """A sample policy configuration for testing."""
    return PolicyConfig(
        allowed_tools=["read_tool", "write_tool", "calculate_tool"],
        prohibited_tools=["delete_database", "execute_shell"],
        max_steps=10,
        max_duration_seconds=30.0,
        max_tool_calls=5,
        sensitive_values_to_redact=["sk-12345", "password123"],
    )


@pytest.fixture
def sample_execution_trace():
    """A sample execution trace for testing."""
    from agentshield.models import ToolCall
    from datetime import datetime
    
    return ExecutionTrace(
        tool_calls=[
            ToolCall(
                name="read_tool",
                arguments={"path": "/tmp/file.txt"},
                result="file content",
                timestamp=datetime.utcnow(),
            )
        ],
        steps_taken=1,
        duration_seconds=0.5,
        final_output="Operation completed successfully",
    )


@pytest.fixture
def mock_tools():
    """Mock tools for testing."""
    def read_tool(path: str) -> str:
        return f"Content of {path}"
    
    def write_tool(path: str, content: str) -> str:
        return f"Wrote to {path}"
    
    def calculate_tool(a: int, b: int) -> int:
        return a + b
    
    return {
        "read_tool": read_tool,
        "write_tool": write_tool,
        "calculate_tool": calculate_tool,
    }
