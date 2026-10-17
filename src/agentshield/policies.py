"""Policy enforcement engine for AgentShield.

This module implements policy validation and enforcement for agent execution.
It enforces tool permissions, execution limits, and sensitive data redaction.
Prohibited tool calls are blocked BEFORE the underlying tool executes.
"""

import re
from typing import Any

from agentshield.models import ExecutionTrace, PolicyConfig


class PolicyViolationError(Exception):
    """Raised when a policy violation is detected."""

    pass


class PolicyEngine:
    """Engine for enforcing agent policies.

    The policy engine validates and enforces constraints at multiple points:
    - Pre-execution: Validates input and initializes counters
    - During execution: Intercepts tool calls before execution
    - Post-execution: Validates outputs and redacts sensitive data

    IMPORTANT: Prohibited tool calls are blocked BEFORE the underlying tool executes.
    """

    def __init__(self, policy: PolicyConfig):
        """Initialize the policy engine with a policy configuration.

        Args:
            policy: The policy configuration to enforce
        """
        self.policy = policy
        self._step_count = 0
        self._tool_call_count = 0
        self._start_time = None

    def validate_tool_call(self, tool_name: str, tool_args: dict[str, Any]) -> bool:
        """Validate a tool call against policy constraints.

        This method is called BEFORE the tool executes. If the tool call
        violates policy, it will be blocked.

        Args:
            tool_name: The name of the tool being called
            tool_args: The arguments to the tool

        Returns:
            True if the tool call is allowed, False otherwise

        Raises:
            PolicyViolationError: If the tool call violates policy
        """
        # Check denylist (prohibited tools)
        if tool_name in self.policy.prohibited_tools:
            raise PolicyViolationError(f"Tool '{tool_name}' is prohibited by policy")

        # Check allowlist (if specified)
        if self.policy.allowed_tools is not None:
            if tool_name not in self.policy.allowed_tools:
                raise PolicyViolationError(f"Tool '{tool_name}' is not in the allowed tools list")

        return True

    def validate_execution_limits(self, steps_taken: int, duration_seconds: float) -> bool:
        """Validate that execution limits have not been exceeded.

        Args:
            steps_taken: Number of steps taken so far
            duration_seconds: Duration of execution so far

        Returns:
            True if within limits, False otherwise

        Raises:
            PolicyViolationError: If execution limits are exceeded
        """
        # Check step limit
        if self.policy.max_steps is not None:
            if steps_taken > self.policy.max_steps:
                raise PolicyViolationError(
                    f"Step limit exceeded: {steps_taken} > {self.policy.max_steps}"
                )

        # Check duration limit
        if self.policy.max_duration_seconds is not None:
            if duration_seconds > self.policy.max_duration_seconds:
                raise PolicyViolationError(
                    f"Duration limit exceeded: {duration_seconds:.2f}s > {self.policy.max_duration_seconds}s"
                )

        return True

    def validate_tool_call_limit(self, tool_call_count: int) -> bool:
        """Validate that tool call limit has not been exceeded.

        Args:
            tool_call_count: Number of tool calls made so far

        Returns:
            True if within limit, False otherwise

        Raises:
            PolicyViolationError: If tool call limit is exceeded
        """
        if self.policy.max_tool_calls is not None:
            if tool_call_count > self.policy.max_tool_calls:
                raise PolicyViolationError(
                    f"Tool call limit exceeded: {tool_call_count} > {self.policy.max_tool_calls}"
                )

        return True

    def redact_sensitive_values(self, text: str) -> str:
        """Redact sensitive values from text.

        Args:
            text: The text to redact

        Returns:
            Text with sensitive values replaced with [REDACTED]
        """
        if not text:
            return text

        redacted = text

        # Redact configured sensitive values
        for sensitive_value in self.policy.sensitive_values_to_redact:
            if sensitive_value in redacted:
                redacted = redacted.replace(sensitive_value, "[REDACTED]")

        # Redact common patterns
        # API keys
        redacted = re.sub(r"sk-[a-zA-Z0-9]{20,}", "[REDACTED]", redacted)
        redacted = re.sub(r"pk-[a-zA-Z0-9]{20,}", "[REDACTED]", redacted)

        # Passwords
        redacted = re.sub(
            r'password["\s]*[:=]["\s]*[^\s"\']+',
            "password=[REDACTED]",
            redacted,
            flags=re.IGNORECASE,
        )

        # Tokens
        redacted = re.sub(
            r'token["\s]*[:=]["\s]*[^\s"\']+', "token=[REDACTED]", redacted, flags=re.IGNORECASE
        )

        return redacted

    def redact_trace(self, trace: ExecutionTrace) -> ExecutionTrace:
        """Redact sensitive values from an execution trace.

        Args:
            trace: The execution trace to redact

        Returns:
            A new trace with sensitive values redacted
        """
        # Redact final output
        if trace.final_output:
            trace.final_output = self.redact_sensitive_values(trace.final_output)

        # Redact tool call arguments and results
        for tool_call in trace.tool_calls:
            # Redact arguments
            for key, value in tool_call.arguments.items():
                if isinstance(value, str):
                    tool_call.arguments[key] = self.redact_sensitive_values(value)

            # Redact result
            if tool_call.result and isinstance(tool_call.result, str):
                tool_call.result = self.redact_sensitive_values(tool_call.result)

        # Redact error message
        if trace.error:
            trace.error = self.redact_sensitive_values(trace.error)

        return trace

    def start_execution(self):
        """Mark the start of execution for duration tracking."""
        import time

        self._start_time = time.time()

    def get_duration_seconds(self) -> float:
        """Get the duration of execution so far.

        Returns:
            Duration in seconds
        """
        import time

        if self._start_time is None:
            return 0.0
        return time.time() - self._start_time

    def increment_step_count(self):
        """Increment the step counter."""
        self._step_count += 1

    def increment_tool_call_count(self):
        """Increment the tool call counter."""
        self._tool_call_count += 1

    def get_step_count(self) -> int:
        """Get the current step count."""
        return self._step_count

    def get_tool_call_count(self) -> int:
        """Get the current tool call count."""
        return self._tool_call_count

    def reset_counters(self):
        """Reset execution counters."""
        self._step_count = 0
        self._tool_call_count = 0
        self._start_time = None


def validate_policy(policy: PolicyConfig) -> list[str]:
    """Validate a policy configuration.

    Args:
        policy: The policy configuration to validate

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check that allowlist and denylist don't overlap
    if policy.allowed_tools and policy.prohibited_tools:
        overlap = set(policy.allowed_tools) & set(policy.prohibited_tools)
        if overlap:
            errors.append(f"Tools in both allowlist and denylist: {overlap}")

    # Check that limits are positive
    if policy.max_steps is not None and policy.max_steps <= 0:
        errors.append("max_steps must be positive")

    if policy.max_duration_seconds is not None and policy.max_duration_seconds <= 0:
        errors.append("max_duration_seconds must be positive")

    if policy.max_tool_calls is not None and policy.max_tool_calls <= 0:
        errors.append("max_tool_calls must be positive")

    return errors
