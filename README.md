# HexSwitch

Hexagonal runtime switchboard for config-driven microservices.

## Description

HexSwitch is a runtime system designed to orchestrate microservices using a hexagonal architecture pattern. It provides a configuration-driven approach to wiring together inbound and outbound adapters, enabling flexible and maintainable service communication.

**Note**: This repository is currently in its foundational scaffold phase. The project structure, tooling, and CI/CD pipelines are established, but no runtime behavior is implemented yet.

## Installation

Install HexSwitch in development mode:

```bash
pip install -e ".[dev]"
```

This installs the package and all development dependencies (linting, testing, type checking).

## Running Tests

Run the test suite:

```bash
pytest
```

Run with coverage report:

```bash
pytest --cov=src/hexswitch --cov-report=html
```

## Running the CLI

After installation, you can run HexSwitch from the command line:

```bash
hexswitch --version
hexswitch --help
```

Or run it as a Python module:

```bash
python -m hexswitch.app
```

For development, you can also use the wrapper script:

```bash
bin/hexswitch-dev.sh --version
```

## Project Structure

- `src/hexswitch/` - Python package (skeleton)
- `tests/` - Test suite (unit and integration tests)
- `docs/` - Project documentation
- `docker/` - Dockerfiles and related scripts
- `infra/` - Infrastructure and deployment configuration
- `bin/` - Helper scripts

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and workflow.

## Documentation

- [Architecture Overview](docs/architecture_overview.md) - High-level architecture description
- [Branch Protection Rules](docs/branch_protection.md) - GitHub branch protection guidelines
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to the project

