# Contributing

Thank you for your interest in contributing to reverberage!

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://github.com/reverberage/hub/blob/main/CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

Before creating bug reports, check existing issues. When creating a bug report:

- Use the bug report template
- Include steps to reproduce
- Describe expected vs actual behavior
- Include environment details (OS, Python version, package version)

### Suggesting Features

- Use the feature request template
- Explain the use case
- Describe how you envision it working
- Consider alignment with project goals

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add or update tests
5. Ensure all tests pass (`pytest`)
6. Ensure lint passes (`ruff check .`)
7. Ensure type check passes (`mypy .`)
8. Commit with conventional format (`feat(scope): description`)
9. Push and open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/hub.git
cd hub

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
ruff format --check .

# Type check
mypy .
```

## Coding Standards

- Follow PEP 8
- Use type hints for all function signatures
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Write tests for new functionality
- Update documentation as needed

## Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]
[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(engine): add support for batch processing`
- `fix(cli): handle missing configuration file`
- `docs(readme): update installation instructions`

## Creating a New Satellite

```bash
# Scaffold a new satellite
python scripts/scaffold-satellite.py <name>

# This creates:
# rvrb-<name>/
# ├── pyproject.toml
# ├── src/rvrb_<name>/
# │   ├── __init__.py
# │   ├── models.py
# │   ├── provider.py
# │   ├── engine.py
# │   ├── cli.py
# │   └── mcp.py
# └── tests/
```

Follow the [Satellite Protocol](Satellite-Protocol) for module structure and contracts.

## Review Process

1. At least one maintainer must review your PR
2. All CI checks must pass
3. Address review comments
4. Once approved, a maintainer will merge

## Questions?

Open an issue with the "question" label.

## License

By contributing, you agree that your contributions are licensed under Apache-2.0.
