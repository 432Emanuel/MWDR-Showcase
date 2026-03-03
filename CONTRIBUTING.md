# Contributing to MWDR Showcase

Thank you for your interest in contributing to this project.

## Scope

This is a **technical showcase** demonstrating modular research data structures and JSON validation patterns. Contributions should align with this educational purpose.

## Contribution Areas

1. **Bug fixes**: Validation errors, schema issues
2. **Documentation improvements**: Clarifications, examples
3. **New demo modules**: Following existing patterns
4. **Schema enhancements**: Backward-compatible changes only

## Workflow

1. Fork the repository
2. Create a feature branch
3. Ensure all JSON files validate: `python3 src/validate/validate_json.py --path .`
4. Submit a pull request with a clear description

## Validation

All contributions must pass the automated CI validation. The GitHub Actions workflow checks:
- JSON syntax validity
- Schema compliance
- Structural consistency

## Code Style

- Python: Follow PEP 8
- JSON: Use 2-space indentation
- Commit messages: Clear, concise, technical

## Contact

Open an issue for questions or discussion.
