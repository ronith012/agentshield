# AgentShield Architecture

## System Overview

AgentShield is a modular Python framework for testing AI agent reliability and security. The architecture is designed to be extensible, allowing third-party developers to add custom agents and test cases without modifying the core implementation.

## Components

### 1. Agent Adapter Interface (`adapters.py`)

The `AgentAdapter` abstract base class defines the contract that all agent implementations must follow. This interface enables:

- Pluggable agent implementations
- Normalized tool calling conventions
- Support for both mock and real LLM-based agents

```python
class AgentAdapter(ABC):
    @abstractmethod
    def execute(self, input: str, tools: Dict[str, Any], policy: PolicyConfig) -> ExecutionTrace:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
```

### 2. Test Runner (`runner.py`)

The `TestRunner` orchestrates test execution:

- Manages test lifecycle (setup, execution, teardown)
- Enforces execution limits (time, steps, tool calls)
- Captures execution traces and metrics
- Distinguishes between test failures and execution errors
- Records test configuration, outcomes, metadata, and evidence

### 3. Policy Engine (`policies.py`)

The `PolicyEngine` enforces agent constraints at multiple points:

- **Pre-execution**: Validates input and initializes counters
- **During execution**: Intercepts tool calls BEFORE execution and validates them
- **Post-execution**: Validates outputs and redacts sensitive data

**IMPORTANT**: Prohibited tool calls are blocked BEFORE the underlying tool executes.

### 4. Test Suites

#### Reliability Test Suite (`testsuites/reliability.py`)

Tests for agent reliability behaviors:
- Instruction following
- Structured output validation
- Malformed input handling
- Error recovery
- Execution limit enforcement

#### Security Test Suite (`testsuites/security.py`)

Tests for agent security behaviors:
- Prompt injection (direct, indirect, roleplay)
- Tool permissions (allowlist, denylist)
- Input boundary testing
- Sensitive data exposure
- Unauthorized actions
- Encoding evasion

### 5. Report Generator (`reporting.py`)

The `ReportGenerator` creates structured reports:

- JSON export with full test results
- Failure explanations and evidence
- Remediation recommendations
- Documentation of limitations

### 6. CLI Interface (`cli.py`)

The CLI provides commands for:
- `init`: Initialize a new project
- `test`: Run test suite
- `report`: Generate reports
- `list-tests`: List available tests

## Data Flow

```
1. Test Definition
   ↓
2. Policy Application
   ↓
3. Agent Execution (with Policy Enforcement)
   ↓
4. Result Collection
   ↓
5. Assertion Evaluation
   ↓
6. Result Aggregation
   ↓
7. Report Generation
```

## Policy Enforcement Flow

```
Tool Call Request
   ↓
Policy Engine Validation
   ↓
Is tool prohibited?
   ├─ Yes → Block (PolicyViolationError)
   └─ No → Continue
   ↓
Is tool in allowlist?
   ├─ No → Block (PolicyViolationError)
   └─ Yes → Continue
   ↓
Check tool call limit
   ├─ Exceeded → Block (PolicyViolationError)
   └─ Within limit → Continue
   ↓
Execute Tool
   ↓
Check step limit
   ├─ Exceeded → Block (PolicyViolationError)
   └─ Within limit → Continue
   ↓
Return Result
```

## Extensibility

### Custom Agents

Third-party developers can create custom agents by implementing the `AgentAdapter` interface:

```python
from agentshield.adapters import AgentAdapter

class MyCustomAgent(AgentAdapter):
    def execute(self, input: str, tools: dict, policy: PolicyConfig) -> ExecutionTrace:
        # Custom implementation
        pass
    
    def get_name(self) -> str:
        return "my_custom_agent"
```

### Custom Test Cases

Custom test cases can be added by creating `TestCase` instances:

```python
from agentshield.models import TestCase, TestCategory

custom_test = TestCase(
    id="CUSTOM-001",
    name="Custom Test",
    description="A custom test",
    category=TestCategory.RELIABILITY,
    input="test input",
    expected_behavior="expected behavior",
    assertions=["assertion"],
)
```

## Security Considerations

The architecture incorporates multiple security layers:

1. **Tool Validation**: All tool calls are validated before execution
2. **Execution Limits**: Steps, duration, and tool calls are bounded
3. **Sensitive Data Redaction**: Configured values are redacted from outputs
4. **Mock Tools**: Default tools are mock implementations, not real operations
5. **No Arbitrary Execution**: Framework does not execute agent-generated commands

## Testing Strategy

The framework itself is tested through:

- Unit tests for each component
- Integration tests for end-to-end workflows
- Verification that prohibited tools are blocked
- Verification that execution limits are enforced
- Verification that test failures are distinguished from errors

## Future Extensibility

The architecture is designed to support future enhancements:

- Real LLM provider integrations (OpenAI, Anthropic, etc.)
- Agent framework adapters (LangChain, CrewAI, etc.)
- Custom security test plugins
- Web dashboard
- CI/CD integration
- Historical test-result comparisons
