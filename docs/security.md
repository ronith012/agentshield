# AgentShield Security Documentation

## Threat Model

### Assumptions

AgentShield assumes the following threat model:

1. **Attacker Goals**: An attacker may attempt to:
   - Cause the agent to execute unauthorized actions
   - Expose sensitive information
   - Bypass policy constraints
   - Cause resource exhaustion
   - Inject malicious instructions

2. **Attack Vectors**: Attacks may come through:
   - Direct user input
   - Retrieved content (RAG, tool outputs, files)
   - Tool parameters
   - Configuration files
   - Environment variables

3. **Capabilities**: The agent may have access to:
   - External tools (APIs, databases, file systems)
   - Multiple execution steps
   - Memory/context
   - Decision-making authority

### Security Controls

AgentShield implements the following security controls:

#### 1. Tool Permission Enforcement

- **Allowlist**: Only tools in the allowlist can be called
- **Denylist**: Tools in the denylist are explicitly prohibited
- **Pre-execution Validation**: Tool calls are validated BEFORE execution
- **No Bypass**: Agents cannot bypass policy through indirect means

#### 2. Execution Limits

- **Step Limit**: Maximum number of execution steps
- **Duration Limit**: Maximum execution time in seconds
- **Tool Call Limit**: Maximum number of tool calls
- **Enforcement**: Limits are enforced during execution, not just checked afterward

#### 3. Sensitive Data Protection

- **Redaction**: Configured sensitive values are redacted from outputs
- **Pattern Matching**: Common patterns (API keys, passwords, tokens) are redacted
- **Report Sanitization**: Reports are sanitized before export
- **No Logging**: Sensitive data is not logged

#### 4. Input Validation

- **Size Limits**: Oversized inputs are rejected or truncated
- **Format Validation**: Malformed inputs are handled gracefully
- **Encoding Normalization**: Encoded inputs are not automatically decoded

#### 5. Safe Execution

- **Mock Tools**: Default tools are mock implementations
- **No Arbitrary Commands**: Framework does not execute agent-generated shell commands
- **Isolation**: Tests run in isolated environments
- **No External Calls**: Tests do not make real API calls by default

## Limitations

### What AgentShield Does NOT Protect Against

1. **Zero-Day Vulnerabilities**: Unknown attack patterns
2. **Social Engineering**: Attacks outside the technical scope
3. **Infrastructure Attacks**: Compromised execution environments
4. **Supply Chain Attacks**: Malicious dependencies
5. **Side-Channel Attacks**: Information leakage through timing, etc.

### What AgentShield Does NOT Guarantee

1. **Complete Security**: Passing all tests does not mean the agent is secure
2. **Real-World Behavior**: Mock agent behavior may differ from real LLMs
3. **Policy Bypass**: Agents that bypass the framework are not protected
4. **External Systems**: Framework does not protect against external system compromises

## Security Testing Approach

### Test Philosophy

AgentShield follows these principles for security testing:

1. **Synthetic Data Only**: No real credentials or sensitive data in tests
2. **Mock Tools**: Tools are mock implementations, not real operations
3. **Controlled Environment**: Tests run in isolated environments
4. **Reproducible Results**: Tests are deterministic and reproducible
5. **Clear Limitations**: Security limitations are documented

### Test Categories

#### Prompt Injection Tests

- Direct override attempts
- Indirect injection via tool outputs
- Roleplay/jailbreak attempts
- Encoding evasion

#### Tool Permission Tests

- Denylist enforcement
- Allowlist enforcement
- Unauthorized action blocking

#### Input Boundary Tests

- Oversized inputs
- Malformed inputs
- Unexpected formats

#### Sensitive Data Tests

- Exposure in outputs
- Exposure in reports
- Redaction verification

#### Execution Limit Tests

- Step limit enforcement
- Duration limit enforcement
- Tool call budget enforcement

## Best Practices

### For Users

1. **Review Test Results**: Carefully review all test failures and errors
2. **Understand Limitations**: Read and understand the security limitations
3. **Use Multiple Approaches**: Combine AgentShield with other security measures
4. **Update Regularly**: Keep the framework and test suites updated
5. **Report Issues**: Report any security vulnerabilities found

### For Developers

1. **Validate Inputs**: Always validate and sanitize inputs
2. **Principle of Least Privilege**: Grant minimum necessary permissions
3. **Defense in Depth**: Implement multiple security layers
4. **Fail Securely**: Default to secure behavior on errors
5. **Auditability**: Log security-relevant events (without sensitive data)

## Security Disclosure

If you discover a security vulnerability in AgentShield, please:

1. Do not create a public issue
2. Send details to the maintainers privately
3. Allow time for the issue to be addressed
4. Follow responsible disclosure practices

## References

AgentShield is informed by the following security resources:

- [OWASP GenAI Security Project](https://genai.owasp.org/)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OWASP Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)
- [Agent Security Regression Harness](https://github.com/OWASP/Agent-Security-Regression-Harness)
