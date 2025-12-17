<div align="center">
  <img src="assets/logo.png" alt="HexSwitch Logo" width="200" />
</div>

# HexSwitch

Hexagonal runtime switchboard for config-driven microservices.

## Description

HexSwitch is a runtime system designed to orchestrate microservices using a hexagonal architecture pattern. It provides a configuration-driven approach to wiring together inbound and outbound adapters, enabling flexible and maintainable service communication.

**Status**: Core runtime functionality is implemented, including adapter framework, HTTP inbound adapter, and runtime orchestration. The system can now run microservices with config-driven adapter wiring.

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

Run only unit tests:

```bash
pytest tests/unit/
```

Run only integration tests:

```bash
pytest tests/integration/
```

Run Docker integration tests:

```bash
pytest tests/integration/test_docker.py -m docker
```

Run multi-container integration tests:

```bash
pytest tests/integration/test_multi_container.py -v
```

Or use the test scripts:

```bash
# Linux/Mac
./scripts/test-docker.sh

# Windows PowerShell
.\scripts\test-docker.ps1
```

### Multi-Container Testing

Test interactions between multiple HexSwitch instances:

```bash
# Start multi-container setup
docker compose -f docker-compose.multi-test.yml up -d

# Run tests
pytest tests/integration/test_multi_container.py -v

# Stop and cleanup
docker compose -f docker-compose.multi-test.yml down -v
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
```

**Create configuration from template:**
```bash
hexswitch init --template hex-config.http-only
hexswitch init --list-templates  # List available templates
```

## Configuration Templates

HexSwitch supports Jinja2 templates for configuration files. Templates allow you to use environment variables and dynamic values in your configuration.

**Template files** must have a `.j2` extension (e.g., `hex-config.yaml.j2`). The `load_config()` function automatically detects and renders templates before parsing YAML.

**Available templates:**
- `hex-config.yaml.j2` - Full configuration with all adapters
- `hex-config.http-only.yaml.j2` - Minimal HTTP-only configuration
- `hex-config.with-mcp.yaml.j2` - Configuration with MCP client adapter

**Example template usage:**
```yaml
service:
  name: {{ env.SERVICE_NAME | default("example-service") }}
  runtime: python

inbound:
  http:
    enabled: {{ env.ENABLE_HTTP | default(true) }}
    port: {{ env.HTTP_PORT | default(8000) | int }}
    base_path: {{ env.BASE_PATH | default("/api") }}
```

**Environment variables** are available via `env.VAR_NAME` in templates. Use Jinja2 filters like `default()`, `int()`, `bool()` for type conversion.
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

**Run runtime:**
```bash
hexswitch run
# Starts the runtime with all enabled adapters
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

# 4. Run runtime
hexswitch run
```

Or run it as a Python module:

```bash
python -m hexswitch.app version
python -m hexswitch.app init
python -m hexswitch.app validate
python -m hexswitch.app run --dry-run
```

## Project Structure

- `src/hexswitch/` - Python package (core runtime, adapters, handlers)
- `tests/` - Test suite (unit and integration tests)
- `docs/` - Project documentation

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and workflow.

## Docker

Build and test the Docker image:

```bash
# Build Docker image
docker build -t hexswitch:latest .

# Test Docker image
docker run --rm hexswitch:latest hexswitch version
```

For more details, see [Development Guide](docs/development_guide.md).

## Documentation

- [Development Guide](docs/development_guide.md) - Installation, testing, and Docker build instructions
- [Architecture Overview](docs/architecture_overview.md) - High-level architecture description
- [Branch Protection Rules](docs/branch_protection.md) - GitHub branch protection guidelines
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to the project

