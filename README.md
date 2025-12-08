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

For detailed development instructions, see [Development Guide](docs/development_guide.md).

## Running the CLI

After installation, you can run HexSwitch from the command line:

### Available Commands

**Show version:**
```bash
hexswitch version
# or
hexswitch --version  # backwards compatible
```

**Create example configuration:**
```bash
hexswitch init
# Creates hex-config.yaml with example configuration
hexswitch init --force  # Overwrite existing file
```

**Validate configuration:**
```bash
hexswitch validate
# Validates hex-config.yaml (default)
hexswitch validate --config path/to/config.yaml
```

**Run runtime (dry-run mode):**
```bash
hexswitch run --dry-run
# Shows execution plan without starting runtime
```

**Run runtime (not yet implemented):**
```bash
hexswitch run
# Will start runtime once implemented
```

### Global Options

- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `--config`: Path to configuration file (default: `hex-config.yaml`)

### Example Workflow

```bash
# 1. Create example configuration
hexswitch init

# 2. Validate configuration
hexswitch validate

# 3. Preview execution plan
hexswitch run --dry-run

# 4. Run (when implemented)
hexswitch run
```

Or run it as a Python module:

```bash
python -m hexswitch.app version
python -m hexswitch.app init
python -m hexswitch.app validate
python -m hexswitch.app run --dry-run
```

For development, you can also use the wrapper script:

```bash
bin/hexswitch-dev.sh version
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

## Docker

Build and test the Docker image:

```bash
# Build Docker image
docker build -f docker/Dockerfile -t hexswitch:latest .

# Test Docker image
docker run --rm hexswitch:latest hexswitch version
```

For more details, see [Development Guide](docs/development_guide.md).

## Documentation

- [Development Guide](docs/development_guide.md) - Installation, testing, and Docker build instructions
- [Architecture Overview](docs/architecture_overview.md) - High-level architecture description
- [Branch Protection Rules](docs/branch_protection.md) - GitHub branch protection guidelines
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to the project

