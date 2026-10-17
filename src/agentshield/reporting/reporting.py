"""Report generation for AgentShield.

This module implements report generation including JSON export,
failure explanations, evidence collection, and remediation recommendations.
"""

import json
from datetime import datetime

from agentshield.models import (
    AgentTestResult as TestResult,
)
from agentshield.models import (
    AgentTestSuiteResult as TestSuiteResult,
)
from agentshield.models import (
    PolicyConfig,
    Report,
    TestStatus,
)


class ReportGenerator:
    """Generator for test reports.

    The report generator:
    - Creates structured reports from test results
    - Includes failure explanations and evidence
    - Provides remediation recommendations
    - Documents evaluation limitations
    - Exports reports in JSON format
    """

    def __init__(self, policy: PolicyConfig):
        """Initialize the report generator with a policy configuration.

        Args:
            policy: The policy configuration used during testing
        """
        self.policy = policy

    def generate_report(self, suite_result: TestSuiteResult) -> Report:
        """Generate a comprehensive test report.

        Args:
            suite_result: The test suite results to report on

        Returns:
            A Report object with comprehensive information
        """
        # Generate remediation recommendations
        recommendations = self._generate_remediation_recommendations(suite_result)

        # Document limitations
        limitations = self._generate_limitations()

        # Create report
        report = Report(
            suite_result=suite_result,
            policy_config=self.policy,
            remediation_recommendations=recommendations,
            limitations=limitations,
            metadata={
                "generated_at": datetime.utcnow().isoformat(),
                "agentshield_version": "0.1.0",
            },
        )

        return report

    def _generate_remediation_recommendations(self, suite_result: TestSuiteResult) -> list[str]:
        """Generate remediation recommendations based on test results.

        Args:
            suite_result: The test suite results

        Returns:
            List of remediation recommendations
        """
        recommendations = []

        # Analyze failed tests
        all_results = suite_result.reliability_results + suite_result.security_results

        for result in all_results:
            if result.status == TestStatus.FAILED:
                recommendation = self._get_recommendation_for_failure(result)
                if recommendation:
                    recommendations.append(recommendation)

        # Add general recommendations if many failures
        failure_rate = (
            suite_result.failed / suite_result.total_tests if suite_result.total_tests > 0 else 0
        )
        if failure_rate > 0.5:
            recommendations.append(
                "High failure rate detected. Review agent implementation and policy configuration."
            )

        return recommendations

    def _get_recommendation_for_failure(self, result: TestResult) -> str:
        """Get a specific recommendation for a test failure.

        Args:
            result: The failed test result

        Returns:
            A remediation recommendation
        """
        # Map test IDs to recommendations
        recommendations_map = {
            "REL-001": "Improve instruction following logic in agent",
            "REL-002": "Add structured output validation to agent",
            "REL-003": "Add input validation and sanitization",
            "REL-004": "Add graceful handling for missing tools",
            "REL-005": "Implement error recovery mechanisms",
            "REL-006": "Review and adjust step limit policy",
            "REL-007": "Review and adjust duration limit policy",
            "REL-008": "Ensure errors are reported rather than silently ignored",
            "SEC-001": "Strengthen system prompt against direct override attempts",
            "SEC-002": "Sanitize and validate tool outputs before use",
            "SEC-003": "Implement persona/jailbreak detection and prevention",
            "SEC-004": "Review tool denylist configuration",
            "SEC-005": "Review tool allowlist configuration",
            "SEC-006": "Add input size limits and validation",
            "SEC-007": "Implement sensitive data redaction in agent outputs",
            "SEC-008": "Review and strengthen action authorization",
            "SEC-009": "Add encoding detection and normalization",
            "SEC-010": "Review and adjust tool call budget policy",
        }

        return recommendations_map.get(result.test_id, f"Review test {result.test_id} failure")

    def _generate_limitations(self) -> list[str]:
        """Generate a list of evaluation limitations.

        Returns:
            List of limitation descriptions
        """
        return [
            "Tests use mock agent and synthetic data only",
            "Results may not reflect behavior with real LLM providers",
            "Passing all tests does not guarantee agent security",
            "Test suite is finite and cannot cover all possible scenarios",
            "Framework does not test against real external systems",
            "Policy enforcement only applies within framework execution context",
            "Agents that bypass the framework are not protected",
            "Real-world agent behavior may differ from mock agent",
            "Security tests are for regression testing, not a security guarantee",
        ]

    def export_json(self, report: Report, filepath: str) -> None:
        """Export report to JSON file.

        Args:
            report: The report to export
            filepath: The file path to write to
        """
        # Convert to JSON-serializable dict
        report_dict = report.model_dump(mode="json")

        # Write to file
        with open(filepath, "w") as f:
            json.dump(report_dict, f, indent=2)

    def export_json_string(self, report: Report) -> str:
        """Export report to JSON string.

        Args:
            report: The report to export

        Returns:
            JSON string representation of the report
        """
        report_dict = report.model_dump(mode="json")
        return json.dumps(report_dict, indent=2)

    def generate_summary(self, report: Report) -> str:
        """Generate a human-readable summary of the report.

        Args:
            report: The report to summarize

        Returns:
            A human-readable summary string
        """
        lines = [
            "AgentShield Test Report Summary",
            "=" * 40,
            "",
            f"Total Tests: {report.suite_result.total_tests}",
            f"Passed: {report.suite_result.passed}",
            f"Failed: {report.suite_result.failed}",
            f"Errors: {report.suite_result.errors}",
            f"Skipped: {report.suite_result.skipped}",
            f"Duration: {report.suite_result.total_duration_seconds:.2f}s",
            "",
            "Remediation Recommendations:",
            "-" * 40,
        ]

        if report.remediation_recommendations:
            for i, rec in enumerate(report.remediation_recommendations, 1):
                lines.append(f"{i}. {rec}")
        else:
            lines.append("No recommendations (all tests passed or errors only)")

        lines.extend(
            [
                "",
                "Limitations:",
                "-" * 40,
            ]
        )

        for limitation in report.limitations:
            lines.append(f"- {limitation}")

        return "\n".join(lines)


def get_failure_explanation(result: TestResult) -> str:
    """Get a detailed explanation for a test failure.

    Args:
        result: The test result to explain

    Returns:
        A detailed explanation string
    """
    if result.status == TestStatus.PASSED:
        return "Test passed successfully"

    if result.status == TestStatus.ERROR:
        return f"Test encountered an execution error: {result.error_message}"

    if result.status == TestStatus.FAILED:
        explanation = f"Test failed: {result.failure_reason}"

        # Add evidence if available
        if result.evidence:
            evidence_str = ", ".join(f"{k}={v}" for k, v in result.evidence.items())
            explanation += f" (Evidence: {evidence_str})"

        return explanation

    if result.status == TestStatus.SKIPPED:
        return "Test was skipped"

    return "Unknown test status"
