# Changelog

All notable changes to AgentShield will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of AgentShield
- Agent adapter interface for custom agent implementations
- Test runner with policy enforcement
- Reliability test suite (8 tests)
- Security test suite (10 tests)
- Policy engine with tool permissions and execution limits
- Sensitive data redaction
- JSON report generation with remediation recommendations
- CLI interface (init, test, report, list-tests)
- Deterministic mock agent and tools
- Comprehensive documentation
- Integration tests verifying policy enforcement

### Security
- Prohibited tool calls are blocked BEFORE execution
- Execution limits (steps, duration, tool calls) are enforced
- Sensitive data redaction with configurable values and patterns
- Mock tools by default (no real system operations)

### Documentation
- README with installation and usage instructions
- Architecture documentation
- Security documentation with threat model
- Getting started guide
- Contributing guidelines
- Code of conduct
- Issue templates

## [0.1.0] - TBD

### Added
- Initial MVP release
