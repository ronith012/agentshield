# Contributing to AgentShield

Thank you for your interest in contributing to AgentShield! This document provides guidelines for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- A clear description of the problem
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment information (Python version, OS, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- A clear description of the enhancement
- The motivation behind the enhancement
- How it would benefit AgentShield users
- Any alternative solutions you've considered

### Pull Requests

We welcome pull requests! Before submitting:

1. Fork the repository
2. Create a branch for your feature or fix
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation if needed
7. Submit a pull request with a clear description

## Development Setup

### Clone the Repository

```bash
git clone https://github.com/username/agentshield.git
cd agentshield
```

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Run Linting

```bash
ruff check src/
ruff format src/
```

## Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use meaningful variable and function names

### Testing

- Write tests for all new functionality
- Ensure tests are deterministic and reproducible
- Use mock data and synthetic data only
- No real credentials or sensitive data in tests
- Verify that tests pass before submitting

### Documentation

- Update README.md for user-facing changes
- Update architecture.md for structural changes
- Update security.md for security-related changes
- Add docstrings to new functions and classes
- Keep documentation in sync with code

## Project Structure

```
agentshield/
├── src/agentshield/
│   ├── __init__.py
│   ├── models.py              # Pydantic models
│   ├── runner.py             # Test runner
│   ├── adapters.py           # Agent adapter interface
│   ├── policies.py           # Policy enforcement
│   ├── reporting.py          # Report generation
│   ├── cli.py                # CLI interface
│   └── testsuites/
│       ├── __init__.py
│       ├── reliability.py   # Reliability tests
│       └── security.py       # Security tests
├── examples/
│   ├── demo_agent.py         # Demonstration agent
│   ├── demo_policy.py        # Example policy
│   └── mock_tools.py         # Mock tools
├── tests/
│   ├── test_*.py            # Unit and integration tests
│   └── conftest.py          # Pytest fixtures
├── docs/
│   ├── architecture.md       # Architecture documentation
│   ├── security.md          # Security documentation
│   └── getting-started.md  # Getting started guide
└── README.md
```

## Adding New Features

### Adding a New Test Case

1. Add the test case to the appropriate test suite (`reliability.py` or `security.py`)
2. Add a test for the test case in `tests/test_reliability.py` or `tests/test_security.py`
3. Update the documentation if needed
4. Run all tests to ensure nothing breaks

### Adding a New Agent Adapter

1. Create a new file in `examples/` or a separate package
2. Implement the `AgentAdapter` interface
3. Add tests for the adapter
4. Update documentation with usage examples

### Adding a New CLI Command

1. Add the command to `cli.py`
2. Add tests for the command in `tests/test_cli.py`
3. Update the README with command documentation
4. Update the getting-started guide if needed

## Security Considerations

- Never commit credentials or sensitive data
- Use synthetic data in tests
- Validate all inputs
- Follow security best practices
- Report security vulnerabilities privately

## Release Process

Releases are managed by the maintainers. The process typically includes:

1. Update version number in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a git tag
4. Build and publish to PyPI
5. Create a GitHub release

## License

By contributing to AgentShield, you agree that your contributions will be licensed under the Apache-2.0 License.

## Questions?

If you have questions about contributing, please:
- Open an issue on GitHub
- Contact the maintainers
- Check existing issues and discussions

Thank you for contributing to AgentShield!
