# Getting Started with AgentShield

This guide will help you get started with AgentShield quickly.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Installation

### Option 1: Install from Source

```bash
git clone https://github.com/username/agentshield.git
cd agentshield
pip install -e ".[dev]"
```

### Option 2: Install from PyPI (after release)

```bash
pip install agentshield
```

## Your First Test

### Step 1: Initialize a Project

```bash
agentshield init my-first-agent
cd my-first-agent
```

This creates the following structure:

```
my-first-agent/
├── agent.py              # Your agent implementation
├── policy.yaml           # Policy configuration
├── agentshield.config.yaml # Project configuration
└── tests/                # Custom tests directory
```

### Step 2: Implement a Simple Agent

Edit `agent.py`:

```python
from agentshield.adapters import AgentAdapter
from agentshield.models import ExecutionTrace, PolicyConfig

class SimpleAgent(AgentAdapter):
    def execute(self, input: str, tools: dict, policy: PolicyConfig) -> ExecutionTrace:
        # Simple implementation that echoes the input
        trace = ExecutionTrace(
            steps_taken=1,
            duration_seconds=0.1,
            final_output=f"Echo: {input}",
        )
        return trace
    
    def get_name(self) -> str:
        return "simple_agent"
```

### Step 3: Configure Policy

Edit `policy.yaml`:

```yaml
allowed_tools:
  - read_tool
  - write_tool
prohibited_tools:
  - delete_database
  - execute_shell
max_steps: 10
max_duration_seconds: 30.0
max_tool_calls: 5
sensitive_values_to_redact:
  - sk-12345
  - password123
```

### Step 4: Run Tests

```bash
agentshield test --agent ./agent.py --verbose
```

You should see output like:

```
Running 18 tests against simple_agent...
Category: all
Policy: max_steps=10, max_duration=30.0s

==================================================
Test Results
==================================================
Total: 18
Passed: X
Failed: Y
Errors: Z
Skipped: 0
Duration: 0.XXs
```

### Step 5: Generate a Report

```bash
agentshield report --input results.json --output report.md
```

View the report:

```bash
cat report.md
```

## Using the Demo Agent

AgentShield includes a demonstration agent that shows various testable behaviors:

```bash
cd examples
python3 -c "
from demo_agent import create_demo_agent
from mock_tools import get_mock_tools
from demo_policy import get_demo_policy

agent = create_demo_agent('compliant')
tools = get_mock_tools()
policy = get_demo_policy()

trace = agent.execute('calculate 2 + 2', tools, policy)
print(trace.final_output)
"
```

## Running Specific Tests

### Run Only Reliability Tests

```bash
agentshield test --agent ./agent.py --category reliability
```

### Run Only Security Tests

```bash
agentshield test --agent ./agent.py --category security
```

### Run a Specific Test

```bash
agentshield test --agent ./agent.py --test-id REL-001
```

## Listing Available Tests

```bash
agentshield list-tests
```

Filter by category:

```bash
agentshield list-tests --category security
```

Filter by tag:

```bash
agentshield list-tests --tag prompt-injection
```

## Understanding Test Results

### Status Types

- **PASSED**: Test assertions were satisfied
- **FAILED**: Test assertions were not satisfied
- **ERROR**: Test encountered an execution error
- **SKIPPED**: Test was skipped (not currently used)

### Failure vs. Error

- **Failure**: The agent executed but did not meet expectations (e.g., returned wrong output)
- **Error**: The agent encountered an exception or could not execute (e.g., crashed)

## Next Steps

1. **Customize Your Agent**: Implement your actual agent logic in `agent.py`
2. **Adjust Policy**: Tune the policy configuration in `policy.yaml`
3. **Add Custom Tests**: Create custom test cases in the `tests/` directory
4. **Integrate with CI**: Add AgentShield to your CI/CD pipeline
5. **Read the Docs**: Check out [architecture.md](architecture.md) and [security.md](security.md)

## Troubleshooting

### Import Errors

If you get import errors, make sure you installed AgentShield in development mode:

```bash
pip install -e .
```

### Policy Violations

If tests fail due to policy violations, check your `policy.yaml` configuration and adjust allowlists/denylists.

### Timeout Errors

If tests timeout, increase the timeout in the test case or adjust the `max_duration_seconds` in your policy.

## Getting Help

- Check the [documentation](docs/)
- Review [examples/](examples/)
- Open an issue on [GitHub](https://github.com/username/agentshield/issues)
