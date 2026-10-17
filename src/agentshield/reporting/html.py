"""HTML report generator for AgentShield."""

from agentshield.models import Report, TestStatus


class HTMLReportGenerator:
    """Generator for HTML test reports."""

    def __init__(self, report: Report):
        """Initialize the HTML report generator.

        Args:
            report: The report to generate HTML for
        """
        self.report = report

    def generate(self) -> str:
        """Generate an HTML report.

        Returns:
            HTML string
        """
        html = self._generate_header()
        html += self._generate_summary()
        html += self._generate_test_results()
        html += self._generate_recommendations()
        html += self._generate_limitations()
        html += self._generate_footer()
        return html

    def _generate_header(self) -> str:
        """Generate the HTML header."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentShield Test Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        h2 {
            color: #555;
            margin-top: 30px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .summary-card {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }
        .summary-card .value {
            font-size: 32px;
            font-weight: bold;
        }
        .passed { color: #4CAF50; }
        .failed { color: #f44336; }
        .error { color: #ff9800; }
        .test-item {
            background: #f9f9f9;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            border-left: 4px solid #ccc;
        }
        .test-item.passed { border-left-color: #4CAF50; }
        .test-item.failed { border-left-color: #f44336; }
        .test-item.error { border-left-color: #ff9800; }
        .test-id {
            font-weight: bold;
            color: #333;
        }
        .test-status {
            float: right;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .status-passed { background: #4CAF50; color: white; }
        .status-failed { background: #f44336; color: white; }
        .status-error { background: #ff9800; color: white; }
        .recommendations, .limitations {
            background: #fff3cd;
            padding: 15px;
            border-radius: 4px;
            margin: 10px 0;
        }
        ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        li {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ AgentShield Test Report</h1>
"""

    def _generate_summary(self) -> str:
        """Generate the summary section."""
        suite = self.report.suite_result
        return f"""
        <h2>📊 Summary</h2>
        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <div class="value">{suite.total_tests}</div>
            </div>
            <div class="summary-card">
                <h3>Passed</h3>
                <div class="value passed">{suite.passed}</div>
            </div>
            <div class="summary-card">
                <h3>Failed</h3>
                <div class="value failed">{suite.failed}</div>
            </div>
            <div class="summary-card">
                <h3>Errors</h3>
                <div class="value error">{suite.errors}</div>
            </div>
            <div class="summary-card">
                <h3>Duration</h3>
                <div class="value">{suite.total_duration_seconds:.2f}s</div>
            </div>
        </div>
"""

    def _generate_test_results(self) -> str:
        """Generate the test results section."""
        html = "<h2>🧪 Test Results</h2>\n"

        all_results = self.report.suite_result.reliability_results + self.report.suite_result.security_results
        for result in all_results:
            status_class = result.status.value
            status_label = result.status.value.upper()

            html += f"""
        <div class="test-item {status_class}">
            <span class="test-id">{result.test_id}</span>
            <span class="test-status status-{status_class}">{status_label}</span>
            <p>Duration: {result.duration_seconds:.3f}s</p>
"""

            if result.status == TestStatus.FAILED and result.failure_reason:
                html += f"            <p><strong>Failure:</strong> {result.failure_reason}</p>\n"
            elif result.status == TestStatus.ERROR and result.error_message:
                html += f"            <p><strong>Error:</strong> {result.error_message}</p>\n"

            html += "        </div>\n"

        return html

    def _generate_recommendations(self) -> str:
        """Generate the recommendations section."""
        if not self.report.remediation_recommendations:
            return ""

        html = "<h2>💡 Remediation Recommendations</h2>\n"
        html += '<div class="recommendations">\n'
        html += "    <ul>\n"
        for rec in self.report.remediation_recommendations:
            html += f"        <li>{rec}</li>\n"
        html += "    </ul>\n"
        html += "</div>\n"
        return html

    def _generate_limitations(self) -> str:
        """Generate the limitations section."""
        html = "<h2>⚠️ Limitations</h2>\n"
        html += '<div class="limitations">\n'
        html += "    <ul>\n"
        for limit in self.report.limitations:
            html += f"        <li>{limit}</li>\n"
        html += "    </ul>\n"
        html += "</div>\n"
        return html

    def _generate_footer(self) -> str:
        """Generate the HTML footer."""
        return """    </div>
</body>
</html>"""
