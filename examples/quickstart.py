"""
Quick Start Example - Run AgentShield in 5 minutes

This is the simplest possible way to use AgentShield.
"""

from agentshield.adapters import AgentAdapter
from agentshield.models import ExecutionTrace, PolicyConfig
from agentshield.runner import TestRunner
from agentshield.reporting import ReportGenerator
from agentshield.testsuites.reliability import ReliabilityTestSuite
from examples.mock_tools import get_mock_tools


class SimpleAgent(AgentAdapter):
    """A simple agent that echoes input."""

    def execute(self, input: str, tools: dict, policy: PolicyConfig) -> ExecutionTrace:
        trace = ExecutionTrace(
            steps_taken=1,
            duration_seconds=0.1,
            final_output=f"Echo: {input}",
        )
        return trace

    def get_name(self) -> str:
        return "simple_agent"


def main():
    """Run a quick test suite."""
    print("AgentShield Quick Start")
    print("=" * 50)

    # Create agent
    agent = SimpleAgent()
    print(f"Created agent: {agent.get_name()}")

    # Create policy
    policy = PolicyConfig(max_steps=10, max_duration_seconds=30.0)
    print(f"Created policy: max_steps={policy.max_steps}")

    # Get tools
    tools = get_mock_tools()
    print(f"Loaded {len(tools)} mock tools")

    # Get tests
    tests = ReliabilityTestSuite.get_all_tests()
    print(f"Loaded {len(tests)} reliability tests")

    # Run tests
    print("\nRunning tests...")
    runner = TestRunner(policy)
    suite_result = runner.run_test_suite(tests, agent, tools)

    # Print results
    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    print(f"Total: {suite_result.total_tests}")
    print(f"Passed: {suite_result.passed}")
    print(f"Failed: {suite_result.failed}")
    print(f"Errors: {suite_result.errors}")
    print(f"Duration: {suite_result.total_duration_seconds:.2f}s")

    # Generate report
    generator = ReportGenerator(policy)
    report = generator.generate_report(suite_result)
    generator.export_json(report, "quickstart-results.json")
    print(f"\nResults saved to: quickstart-results.json")


if __name__ == "__main__":
    main()
