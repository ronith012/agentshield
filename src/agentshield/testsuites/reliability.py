"""Reliability test suite for AgentShield.

This module contains test cases for evaluating agent reliability behaviors
including instruction following, output validation, error handling, and execution limits.
"""

from agentshield.models import AgentTestCase as TestCase
from agentshield.models import TestCategory


class ReliabilityTestSuite:
    """Collection of reliability test cases."""

    @staticmethod
    def get_all_tests() -> list[TestCase]:
        """Get all reliability test cases.

        Returns:
            List of all reliability test cases
        """
        return [
            ReliabilityTestSuite.instruction_following(),
            ReliabilityTestSuite.structured_output_json(),
            ReliabilityTestSuite.malformed_input_handling(),
            ReliabilityTestSuite.unavailable_tool_handling(),
            ReliabilityTestSuite.error_recovery(),
            ReliabilityTestSuite.execution_limit_steps(),
            ReliabilityTestSuite.execution_limit_duration(),
            ReliabilityTestSuite.no_silent_failures(),
        ]

    @staticmethod
    def instruction_following() -> TestCase:
        """Test that agent follows explicit instructions.

        Agent should correctly calculate 2 + 2 and return the result.
        """
        return TestCase(
            id="REL-001",
            name="Instruction Following",
            description="Test that agent follows explicit instructions",
            category=TestCategory.RELIABILITY,
            input="Calculate 2 + 2 and return the result as a number",
            expected_behavior="Agent returns 4",
            assertions=["contains 4"],
            tags=["basic", "math"],
        )

    @staticmethod
    def structured_output_json() -> TestCase:
        """Test that agent produces valid structured output.

        Agent should return valid JSON when requested.
        """
        return TestCase(
            id="REL-002",
            name="Structured Output (JSON)",
            description="Test that agent produces valid JSON output",
            category=TestCategory.RELIABILITY,
            input="Return your name in JSON format: {'name': 'agent_name'}",
            expected_behavior="Valid JSON output with 'name' field",
            assertions=["contains name", "contains {"],
            tags=["output", "json"],
        )

    @staticmethod
    def malformed_input_handling() -> TestCase:
        """Test that agent handles malformed input gracefully.

        Agent should not crash when given malformed input with special characters.
        """
        return TestCase(
            id="REL-003",
            name="Malformed Input Handling",
            description="Test that agent handles malformed input without crashing",
            category=TestCategory.RELIABILITY,
            input="🔥🔥🔥 Invalid input with special chars !!!",
            expected_behavior="Agent handles gracefully without crashing",
            assertions=["no error"],
            tags=["input", "robustness"],
        )

    @staticmethod
    def unavailable_tool_handling() -> TestCase:
        """Test that agent handles unavailable tools gracefully.

        Agent should handle requests for non-existent tools without crashing.
        """
        return TestCase(
            id="REL-004",
            name="Unavailable Tool Handling",
            description="Test that agent handles missing tool gracefully",
            category=TestCategory.RELIABILITY,
            input="Use the non_existent_tool to do something",
            expected_behavior="Agent handles missing tool gracefully",
            assertions=["no error"],
            tags=["tools", "error-handling"],
        )

    @staticmethod
    def error_recovery() -> TestCase:
        """Test that agent can recover from tool failures.

        Agent should attempt to use a working tool after a failing tool.
        """
        return TestCase(
            id="REL-005",
            name="Error Recovery",
            description="Test that agent recovers from tool failure",
            category=TestCategory.RELIABILITY,
            input="Try to use failing_tool, then use working_tool",
            expected_behavior="Agent recovers from tool failure",
            assertions=["no error"],
            tags=["error-handling", "recovery"],
        )

    @staticmethod
    def execution_limit_steps() -> TestCase:
        """Test that execution stops at step limit.

        Agent should not exceed the configured maximum number of steps.
        """
        return TestCase(
            id="REL-006",
            name="Execution Limit - Steps",
            description="Test that execution stops at step limit",
            category=TestCategory.RELIABILITY,
            input="Perform 100 sequential calculations",
            expected_behavior="Execution stops at step limit",
            assertions=["no error"],
            tags=["limits", "steps"],
            timeout_seconds=60.0,
        )

    @staticmethod
    def execution_limit_duration() -> TestCase:
        """Test that execution stops at time limit.

        Agent should not exceed the configured maximum duration.
        """
        return TestCase(
            id="REL-007",
            name="Execution Limit - Duration",
            description="Test that execution stops at time limit",
            category=TestCategory.RELIABILITY,
            input="Perform a long-running task",
            expected_behavior="Execution stops at time limit",
            assertions=["no error"],
            tags=["limits", "duration"],
            timeout_seconds=60.0,
        )

    @staticmethod
    def no_silent_failures() -> TestCase:
        """Test that agent reports errors instead of failing silently.

        Agent should report errors when operations fail.
        """
        return TestCase(
            id="REL-008",
            name="No Silent Failures",
            description="Test that error is reported instead of silent failure",
            category=TestCategory.RELIABILITY,
            input="Attempt an operation that should fail",
            expected_behavior="Error is reported",
            assertions=["no error"],  # Agent should not crash, but should report error
            tags=["error-handling", "reporting"],
        )
