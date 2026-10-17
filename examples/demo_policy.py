"""Example policy configuration for demonstration purposes.

This file demonstrates how to configure agent constraints for testing.
The policy includes tool permissions, execution limits, and sensitive value redaction.
"""

from agentshield.models import PolicyConfig


def get_demo_policy() -> PolicyConfig:
    """Get a demonstration policy configuration.
    
    This policy demonstrates:
    - Tool allowlist (only specific tools allowed)
    - Tool denylist (dangerous tools prohibited)
    - Execution limits (steps, duration, tool calls)
    - Sensitive value redaction
    
    Returns:
        A PolicyConfig instance with demonstration constraints
    """
    return PolicyConfig(
        # Only these tools are allowed
        allowed_tools=[
            "read_tool",
            "write_tool",
            "calculate_tool",
            "info_tool",
        ],
        # These tools are explicitly prohibited
        prohibited_tools=[
            "delete_database_tool",
            "execute_shell_tool",
        ],
        # Maximum number of steps the agent can take
        max_steps=10,
        # Maximum execution time in seconds
        max_duration_seconds=30.0,
        # Maximum number of tool calls
        max_tool_calls=5,
        # Sensitive values to redact from outputs and reports
        sensitive_values_to_redact=[
            "sk-12345",
            "password123",
            "API_KEY_SECRET",
        ],
    )


def get_permissive_policy() -> PolicyConfig:
    """Get a permissive policy for testing.
    
    This policy has minimal restrictions for testing purposes.
    
    Returns:
        A PolicyConfig instance with minimal constraints
    """
    return PolicyConfig(
        # No allowlist (all tools allowed by default)
        allowed_tools=None,
        # Only prohibit dangerous tools
        prohibited_tools=[
            "delete_database_tool",
            "execute_shell_tool",
        ],
        # Generous limits
        max_steps=100,
        max_duration_seconds=300.0,
        max_tool_calls=50,
        # No sensitive values to redact
        sensitive_values_to_redact=[],
    )


def get_strict_policy() -> PolicyConfig:
    """Get a strict policy for testing.
    
    This policy has tight restrictions for testing enforcement.
    
    Returns:
        A PolicyConfig instance with strict constraints
    """
    return PolicyConfig(
        # Very restrictive allowlist
        allowed_tools=["read_tool"],
        # Prohibit all dangerous tools
        prohibited_tools=[
            "delete_database_tool",
            "execute_shell_tool",
            "write_tool",
            "calculate_tool",
        ],
        # Very tight limits
        max_steps=3,
        max_duration_seconds=5.0,
        max_tool_calls=2,
        # Redact many sensitive values
        sensitive_values_to_redact=[
            "sk-",
            "pk_",
            "password",
            "token",
            "secret",
        ],
    )
