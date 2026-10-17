"""Command-line interface for AgentShield."""

import sys
from pathlib import Path

import typer
import yaml

from agentshield.config import Config
from agentshield.history import TestHistory
from agentshield.models import AgentTestSuiteResult as TestSuiteResult
from agentshield.models import PolicyConfig
from agentshield.reporting import ReportGenerator
from agentshield.runner import TestRunner
from agentshield.testsuites.reliability import ReliabilityTestSuite
from agentshield.testsuites.security import SecurityTestSuite

app = typer.Typer(help="AgentShield: AI Agent Reliability and Security Testing Framework")


def load_policy_from_yaml(path: str) -> PolicyConfig:
    """Load policy configuration from a YAML file.

    Args:
        path: Path to the YAML file

    Returns:
        PolicyConfig object
    """
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return PolicyConfig(**data)


@app.command()
def init(
    path: str | None = typer.Argument(
        None, help="Directory to initialize (default: current directory)"
    ),
    agent_type: str | None = typer.Option("mock", help="Agent type to scaffold (mock, custom)"),
):
    """Initialize a new AgentShield project."""
    project_dir = Path(path) if path else Path.cwd()

    typer.echo(f"Initializing AgentShield project in: {project_dir}")

    # Create project structure
    (project_dir / "tests").mkdir(exist_ok=True)
    (project_dir / "agent.py").write_text(
        "# Your agent implementation\n"
        "from agentshield.adapters import AgentAdapter\n"
        "from agentshield.models import ExecutionTrace, PolicyConfig\n"
        "\n"
        "class MyAgent(AgentAdapter):\n"
        "    def execute(self, input: str, tools: dict, policy: PolicyConfig) -> ExecutionTrace:\n"
        "        trace = ExecutionTrace(\n"
        "            steps_taken=1,\n"
        "            duration_seconds=0.1,\n"
        '            final_output=f"Processed: {input}",\n'
        "        )\n"
        "        return trace\n"
        "    \n"
        "    def get_name(self) -> str:\n"
        '        return "my_agent"\n'
    )

    (project_dir / "policy.yaml").write_text(
        "# AgentShield Policy Configuration\n"
        "allowed_tools:\n"
        "  - read_tool\n"
        "  - write_tool\n"
        "prohibited_tools:\n"
        "  - delete_database\n"
        "  - execute_shell\n"
        "max_steps: 10\n"
        "max_duration_seconds: 30.0\n"
        "max_tool_calls: 5\n"
        "sensitive_values_to_redact:\n"
        "  - sk-12345\n"
        "  - password123\n"
    )

    (project_dir / "agentshield.config.yaml").write_text(
        "# AgentShield Project Configuration\nagent_path: ./agent.py\npolicy_path: ./policy.yaml\n"
    )

    typer.echo("✓ Created project structure")
    typer.echo("✓ Created agent.py")
    typer.echo("✓ Created policy.yaml")
    typer.echo("✓ Created agentshield.config.yaml")
    typer.echo("\nNext steps:")
    typer.echo("  1. Implement your agent in agent.py")
    typer.echo("  2. Configure policy.yaml")
    typer.echo("  3. Run: agentshield test")


@app.command()
def test(
    agent: str | None = typer.Option(None, "--agent", help="Path to agent implementation"),
    policy: str | None = typer.Option(None, "--policy", help="Path to policy configuration"),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Path to save results JSON"
    ),
    category: str | None = typer.Option(
        None, "--category", "-c", help="Test category (reliability, security, or all)"
    ),
    test_id: str | None = typer.Option(None, "--test-id", "-t", help="Specific test ID to run"),
    trials: int = typer.Option(1, "--trials", "-n", help="Number of trials for nondeterministic agents (k-trial)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """Run the test suite against an agent."""
    # Auto-discover configuration
    config = Config.find()

    # Load agent (from config or argument)
    if agent:
        agent_path = Path(agent)
    elif config.agent_path:
        agent_path = Path(config.agent_path)
    else:
        agent_path = Path("./agent.py")

    if not agent_path.exists():
        typer.echo(f"Error: Agent file not found: {agent_path}", err=True)
        sys.exit(1)

    # Import agent module
    sys.path.insert(0, str(agent_path.parent))
    module_name = agent_path.stem
    agent_module = __import__(module_name)

    # Find agent class (assumes single AgentAdapter subclass)
    agent_class = None
    for attr_name in dir(agent_module):
        attr = getattr(agent_module, attr_name)
        if isinstance(attr, type) and attr_name != "AgentAdapter":
            try:
                from agentshield.adapters import AgentAdapter

                if issubclass(attr, AgentAdapter) and attr != AgentAdapter:
                    agent_class = attr
                    break
            except:
                pass

    if not agent_class:
        typer.echo("Error: No agent class found in agent file", err=True)
        sys.exit(1)

    agent = agent_class()

    # Load policy (from config or argument)
    if policy:
        policy_path = Path(policy)
    elif config.policy_path:
        policy_path = Path(config.policy_path)
    else:
        policy_path = None

    if policy_path and policy_path.exists():
        policy_config = load_policy_from_yaml(str(policy_path))
    else:
        policy_config = PolicyConfig()  # Use default

    # Get test cases
    if category == "reliability":
        test_cases = ReliabilityTestSuite.get_all_tests()
    elif category == "security":
        test_cases = SecurityTestSuite.get_all_tests()
    else:
        test_cases = ReliabilityTestSuite.get_all_tests() + SecurityTestSuite.get_all_tests()

    # Filter by test ID if specified
    if test_id:
        test_cases = [tc for tc in test_cases if tc.id == test_id]
        if not test_cases:
            typer.echo(f"Error: Test ID not found: {test_id}", err=True)
            sys.exit(1)

    # Get mock tools
    from examples.mock_tools import get_mock_tools

    tools = get_mock_tools()

    # Run tests
    typer.echo(f"Running {len(test_cases)} tests against {agent.get_name()}...")
    if verbose:
        typer.echo(f"Category: {category or 'all'}")
        typer.echo(
            f"Policy: max_steps={policy_config.max_steps}, max_duration={policy_config.max_duration_seconds}s"
        )
        if trials > 1:
            typer.echo(f"Trials: {trials} (k-trial for nondeterministic agents)")

    runner = TestRunner(policy_config)
    suite_result = runner.run_test_suite(test_cases, agent, tools, num_trials=trials)

    # Print results
    typer.echo("\n" + "=" * 50)
    typer.echo("Test Results")
    typer.echo("=" * 50)
    typer.echo(f"Total: {suite_result.total_tests}")
    typer.echo(f"Passed: {suite_result.passed}")
    typer.echo(f"Failed: {suite_result.failed}")
    typer.echo(f"Errors: {suite_result.errors}")
    typer.echo(f"Skipped: {suite_result.skipped}")
    typer.echo(f"Duration: {suite_result.total_duration_seconds:.2f}s")

    # Print individual results if verbose
    if verbose:
        typer.echo("\nIndividual Results:")
        for result in suite_result.reliability_results + suite_result.security_results:
            status_symbol = "✓" if result.status.value == "passed" else "✗"
            typer.echo(f"  {status_symbol} {result.test_id}: {result.status.value}")
            if result.status.value == "failed" and result.failure_reason:
                typer.echo(f"    Reason: {result.failure_reason}")
            elif result.status.value == "error" and result.error_message:
                typer.echo(f"    Error: {result.error_message}")

    # Save results
    output_path = Path(output if output else config.default_output or "results.json")
    generator = ReportGenerator(policy_config)
    report = generator.generate_report(suite_result)
    generator.export_json(report, output_path)
    typer.echo(f"\nResults saved to: {output_path}")

    # Save to history
    history = TestHistory()
    history.save_run(suite_result, agent.get_name())
    typer.echo("Results saved to history")

    # Exit with error code if failures
    if suite_result.failed > 0 or suite_result.errors > 0:
        sys.exit(1)


@app.command()
def report(
    input: str | None = typer.Option("results.json", "--input", "-i", help="Path to results JSON"),
    output: str | None = typer.Option("report.md", "--output", "-o", help="Path to save report"),
    format: str | None = typer.Option(
        "markdown", "--format", "-f", help="Report format (markdown, json, html)"
    ),
):
    """Generate a human-readable report from test results."""
    import json

    input_path = Path(input)
    if not input_path.exists():
        typer.echo(f"Error: Results file not found: {input_path}", err=True)
        sys.exit(1)

    # Load results
    with open(input_path) as f:
        results_data = json.load(f)

    # Generate report
    if format == "json":
        # Pretty-print JSON
        output_path = Path(output)
        with open(output_path, "w") as f:
            json.dump(results_data, f, indent=2)
        typer.echo(f"JSON report saved to: {output_path}")
    elif format == "html":
        # Generate HTML report
        from agentshield.reporting.html import HTMLReportGenerator

        suite_result = TestSuiteResult(**results_data["suite_result"])
        policy_config = PolicyConfig(**results_data["policy_config"])

        generator = ReportGenerator(policy_config)
        report = generator.generate_report(suite_result)
        html_generator = HTMLReportGenerator(report)
        html = html_generator.generate()

        output_path = Path(output)
        with open(output_path, "w") as f:
            f.write(html)
        typer.echo(f"HTML report saved to: {output_path}")
    else:
        # Generate markdown summary
        suite_result = TestSuiteResult(**results_data["suite_result"])
        policy_config = PolicyConfig(**results_data["policy_config"])

        generator = ReportGenerator(policy_config)
        report = generator.generate_report(suite_result)
        summary = generator.generate_summary(report)

        output_path = Path(output)
        with open(output_path, "w") as f:
            f.write(summary)

        typer.echo(f"Markdown report saved to: {output_path}")
        typer.echo("\n" + summary)


@app.command()
def list_tests(
    category: str | None = typer.Option(
        None, "--category", "-c", help="Filter by category (reliability, security)"
    ),
    tag: str | None = typer.Option(None, "--tag", "-t", help="Filter by tag"),
):
    """List available test cases."""
    reliability_tests = ReliabilityTestSuite.get_all_tests()
    security_tests = SecurityTestSuite.get_all_tests()

    if category == "reliability":
        tests = reliability_tests
    elif category == "security":
        tests = security_tests
    else:
        tests = reliability_tests + security_tests

    # Filter by tag if specified
    if tag:
        tests = [tc for tc in tests if tag in tc.tags]

    typer.echo(f"Available Tests ({len(tests)}):")
    typer.echo("=" * 80)

    for test in tests:
        typer.echo(f"\n{test.id}: {test.name}")
        typer.echo(f"  Category: {test.category.value}")
        typer.echo(f"  Description: {test.description}")
        if test.tags:
            typer.echo(f"  Tags: {', '.join(test.tags)}")


@app.command()
def history(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of recent runs to show"),
    agent: str | None = typer.Option(None, "--agent", "-a", help="Filter by agent name"),
    trends: bool = typer.Option(False, "--trends", "-t", help="Show trend analysis"),
):
    """Show test history and trends."""
    hist = TestHistory()

    if trends:
        trends_data = hist.get_trends(agent_name=agent, runs=limit)
        typer.echo("Test Trends")
        typer.echo("=" * 50)
        typer.echo(f"Total runs analyzed: {trends_data.get('total_runs', 0)}")
        typer.echo(f"Average pass rate: {trends_data.get('average_pass_rate', 0)}%")
        typer.echo(f"\nMost recent run:")
        recent = trends_data.get("most_recent", {})
        typer.echo(f"  Timestamp: {recent.get('timestamp', 'N/A')}")
        typer.echo(f"  Passed: {recent.get('passed', 0)}")
        typer.echo(f"  Failed: {recent.get('failed', 0)}")
        typer.echo(f"  Errors: {recent.get('errors', 0)}")
    else:
        runs = hist.get_recent_runs(limit)
        typer.echo(f"Recent Test Runs ({len(runs)}):")
        typer.echo("=" * 50)

        for run in runs:
            typer.echo(f"\n[{run['timestamp']}] {run['agent_name']}")
            typer.echo(f"  Total: {run['total_tests']}, Passed: {run['passed']}, Failed: {run['failed']}, Errors: {run['errors']}")
            typer.echo(f"  Duration: {run['duration_seconds']:.2f}s")


if __name__ == "__main__":
    app()
