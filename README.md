# AgentShield

An open-source framework for testing the reliability and security of AI agents before deployment.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-94%20passing-green.svg)](tests/)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-8A2BE2.svg)](https://github.com/astral-sh/ruff)

## Overview

AgentShield provides a structured way to test AI agent behaviors and produce actionable reports. It helps developers identify reliability issues and security vulnerabilities before deploying agents to production.

### Key Features

- **Deterministic Testing**: Test agents without requiring paid AI APIs using mock tools and synthetic data
- **Policy Enforcement**: Enforce tool permissions, execution limits, and sensitive data redaction
- **Reliability Testing**: Test instruction following, output validation, error handling, and execution limits
- **Security Testing**: Test prompt injection, tool permissions, input boundaries, and sensitive data handling
- **Structured Reporting**: Generate JSON reports with failure explanations, evidence, and remediation recommendations
- **CLI Interface**: Simple command-line interface for running tests and generating reports
- **Extensible**: Easy to add custom agents and test cases

### What AgentShield Does

- Executes reproducible tests against supported agent interfaces
- Observes agent behavior and evaluates it against defined expectations
- Enforces policy constraints (tool permissions, execution limits)
- Produces structured reports with pass/fail/error outcomes
- Distinguishes between test failures and execution errors
- Documents the limitations of its findings

### What AgentShield Does NOT Do

- Claim that an agent is completely secure because it passed tests
- Execute arbitrary shell commands during security tests
- Perform unauthorized testing against external systems
- Send real credentials to test cases
- Provide a silver bullet for agent security

## Installation

### From Source

```bash
git clone https://github.com/username/agentshield.git
cd agentshield
pip install -e ".[dev]"
```

### From PyPI (after release)

```bash
pip install agentshield
```

## Quick Start (5 Minutes)

### Step 1: Install AgentShield

```bash
pip install agentshield
```

### Step 2: Run a Quick Test

```bash
# Initialize a new project
agentshield init my-agent
cd my-agent

# Run tests against the default agent
agentshield test --agent ./agent.py --verbose

# Generate a report
agentshield report
```

That's it! You've just run your first agent reliability and security tests.

## Detailed Setup

### 1. Initialize a Project

```bash
agentshield init my-agent-project
cd my-agent-project
```

This creates:
- `agent.py` - Stub agent implementation
- `policy.yaml` - Policy configuration
- `agentshield.config.yaml` - Project configuration

### 2. Implement Your Agent

Edit `agent.py` to implement your agent:

```python
from agentshield.adapters import AgentAdapter
from agentshield.models import ExecutionTrace, PolicyConfig

class MyAgent(AgentAdapter):
    def execute(self, input: str, tools: dict, policy: PolicyConfig) -> ExecutionTrace:
        # Implement your agent logic here
        trace = ExecutionTrace(
            steps_taken=1,
            duration_seconds=0.1,
            final_output=f"Processed: {input}",
        )
        return trace
    
    def get_name(self) -> str:
        return "my_agent"
```

### 3. Configure Policy

Edit `policy.yaml` to set constraints:

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

### 4. Run Tests

```bash
agentshield test --agent ./agent.py --verbose
```

### 5. Generate Report

```bash
agentshield report --input results.json --output report.md
```

## CLI Commands

### `agentshield init`

Initialize a new AgentShield project.

```bash
agentshield init [PATH] [--agent-type TYPE]
```

### `agentshield test`

Run the test suite against an agent.

```bash
agentshield test [--agent PATH] [--policy PATH] [--output PATH] [--category CAT] [--test-id ID] [--verbose]
```

### `agentshield report`

Generate a human-readable report from test results.

```bash
agentshield report [--input PATH] [--output PATH] [--format FORMAT]
```

### `agentshield list-tests`

List available test cases.

```bash
agentshield list-tests [--category CAT] [--tag TAG]
```

## Test Suites

### Reliability Tests (8 tests)

- **REL-001**: Instruction Following
- **REL-002**: Structured Output (JSON)
- **REL-003**: Malformed Input Handling
- **REL-004**: Unavailable Tool Handling
- **REL-005**: Error Recovery
- **REL-006**: Execution Limit - Steps
- **REL-007**: Execution Limit - Duration
- **REL-008**: No Silent Failures

### Security Tests (10 tests)

- **SEC-001**: Direct Prompt Override
- **SEC-002**: Indirect Injection via Tool Output
- **SEC-003**: Roleplay Injection (DAN-style)
- **SEC-004**: Tool Permission - Denylist
- **SEC-005**: Tool Permission - Allowlist
- **SEC-006**: Oversized Input
- **SEC-007**: Sensitive Data Exposure
- **SEC-008**: Unauthorized Action
- **SEC-009**: Encoding Evasion (Base64)
- **SEC-010**: Execution Budget Enforcement

## Architecture

AgentShield consists of the following components:

- **Agent Adapter Interface**: Abstract base class for agent implementations
- **Test Runner**: Orchestrates test execution and enforces policies
- **Policy Engine**: Enforces tool permissions and execution limits
- **Reliability Test Suite**: Tests for agent reliability behaviors
- **Security Test Suite**: Tests for agent security behaviors
- **Report Generator**: Creates structured reports with recommendations
- **CLI Interface**: Command-line interface for all operations

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Security

AgentShield is designed with security in mind:

- Uses synthetic data and mock tools by default
- Blocks prohibited tool calls BEFORE execution
- Redacts sensitive values from outputs and reports
- Enforces execution limits (steps, duration, tool calls)
- Does not execute arbitrary generated commands
- Clearly documents the limitations of security tests

See [docs/security.md](docs/security.md) for the threat model and security considerations.

## Limitations

- Tests use mock agent and synthetic data only
- Results may not reflect behavior with real LLM providers
- Passing all tests does not guarantee agent security
- Test suite is finite and cannot cover all possible scenarios
- Framework does not test against real external systems
- Policy enforcement only applies within framework execution context
- Agents that bypass the framework are not protected

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

AgentShield is inspired by research on AI agent reliability and security, including:
- OWASP GenAI Security Project
- ReliabilityBench
- AgentInspect
- OWASP Agent Security Regression Harness
