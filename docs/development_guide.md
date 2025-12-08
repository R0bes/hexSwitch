# Development Guide

This guide explains how to install, test, and build HexSwitch.

## Installation

### Local Development Installation

Install HexSwitch in development mode with all dependencies:

```bash
# Install the package in editable mode with dev dependencies
pip install -e ".[dev]"

# Or if you prefer to install dependencies separately:
pip install -e .
pip install -e ".[dev]"
```

This installs:
- HexSwitch package itself
- Development tools: `ruff`, `pytest`, `pytest-cov`, `mypy`, `radon`
- Runtime dependencies: `pyyaml`

### Verify Installation

Check that the CLI is available:

```bash
hexswitch version
# Should output: HexSwitch 0.1.0
```

## Testing

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_config.py -v

# Run specific test
pytest tests/unit/test_config.py::test_load_config_valid -v
```

### Run Tests with Coverage

```bash
# Run tests with coverage report
pytest --cov=src/hexswitch --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src/hexswitch --cov-report=html

# Open coverage report (after HTML generation)
# On Linux/Mac: open htmlcov/index.html
# On Windows: start htmlcov/index.html
```

### Run Linting

```bash
# Check code with ruff
ruff check .

# Auto-fix issues where possible
ruff check . --fix

# Check specific files
ruff check src/hexswitch tests/
```

### Run Type Checking

```bash
# Run mypy type checking
mypy src/hexswitch

# Or with pytest plugin
pytest --mypy
```

### Run Complexity Check

```bash
# Check code complexity with radon
radon cc src/hexswitch

# Or with pytest plugin
pytest --radon
```

## Docker Build

### Build Docker Image

Build the Docker image locally:

```bash
# Build from docker/Dockerfile
docker build -f docker/Dockerfile -t hexswitch:latest .

# Build with specific tag
docker build -f docker/Dockerfile -t hexswitch:0.1.0 .

# Build with build arguments (if needed in future)
docker build -f docker/Dockerfile -t hexswitch:latest --build-arg PYTHON_VERSION=3.12 .
```

### Test Docker Image

After building, test the Docker image:

```bash
# Test version command
docker run --rm hexswitch:latest hexswitch version

# Test help
docker run --rm hexswitch:latest hexswitch --help

# Test init command (creates config in container)
docker run --rm hexswitch:latest hexswitch init

# Test with mounted volume for config
docker run --rm -v $(pwd):/app hexswitch:latest hexswitch validate --config /app/hex-config.yaml

# Interactive shell in container
docker run --rm -it hexswitch:latest /bin/bash
```

### Run Docker Container

```bash
# Run with default command (shows help)
docker run --rm hexswitch:latest

# Run specific command
docker run --rm hexswitch:latest hexswitch version

# Run with environment variables
docker run --rm -e LOG_LEVEL=DEBUG hexswitch:latest hexswitch version

# Run with mounted config file
docker run --rm -v $(pwd)/hex-config.yaml:/app/hex-config.yaml hexswitch:latest hexswitch validate
```

### Push to Registry (GitHub Container Registry)

If you have configured GitHub Actions or want to push manually:

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag image for registry
docker tag hexswitch:latest ghcr.io/OWNER/hexswitch:latest
docker tag hexswitch:latest ghcr.io/OWNER/hexswitch:0.1.0

# Push to registry
docker push ghcr.io/OWNER/hexswitch:latest
docker push ghcr.io/OWNER/hexswitch:0.1.0
```

## Complete Development Workflow

### 1. Setup

```bash
# Clone repository
git clone <repository-url>
cd hexSwitch

# Install dependencies
pip install -e ".[dev]"
```

### 2. Development Cycle

```bash
# Make changes to code

# Run linting
ruff check .

# Run tests
pytest -v

# Test CLI locally
hexswitch version
hexswitch init
hexswitch validate

# Test with dry-run
hexswitch run --dry-run
```

### 3. Before Committing

```bash
# Run all checks
ruff check .
pytest --cov=src/hexswitch --cov-report=term-missing
mypy src/hexswitch

# Or use pre-commit hooks (if configured)
pre-commit run --all-files
```

### 4. Build and Test Docker

```bash
# Build Docker image
docker build -f docker/Dockerfile -t hexswitch:latest .

# Test Docker image
docker run --rm hexswitch:latest hexswitch version

# Run tests in Docker (if test script exists)
docker run --rm hexswitch:latest pytest
```

## Troubleshooting

### Installation Issues

**Problem**: `pip install -e ".[dev]"` fails
- **Solution**: Ensure you have Python 3.12+ installed
- **Solution**: Try upgrading pip: `pip install --upgrade pip setuptools wheel`

**Problem**: Import errors after installation
- **Solution**: Ensure you're in a virtual environment
- **Solution**: Reinstall: `pip uninstall hexswitch && pip install -e ".[dev]"`

### Test Issues

**Problem**: Tests fail with import errors
- **Solution**: Ensure package is installed: `pip install -e .`
- **Solution**: Check PYTHONPATH: `export PYTHONPATH=$PWD/src:$PYTHONPATH`

**Problem**: Coverage too low
- **Solution**: Current threshold is 0% for scaffold phase
- **Solution**: Will be increased as implementation progresses

### Docker Issues

**Problem**: Docker build fails
- **Solution**: Check Docker is running: `docker ps`
- **Solution**: Check Dockerfile path: `docker build -f docker/Dockerfile .`

**Problem**: Container exits immediately
- **Solution**: Use interactive mode: `docker run -it hexswitch:latest /bin/bash`
- **Solution**: Check default command in Dockerfile

## CI/CD

The project includes GitHub Actions workflows:

- **CI Workflow** (`.github/workflows/ci.yaml`): Runs on push/PR
  - Linting (ruff)
  - Tests (pytest)
  - Type checking (mypy)
  - Complexity check (radon)

- **Docker Workflow** (`.github/workflows/docker.yaml`): Runs on main branch or tags
  - Builds Docker image
  - Pushes to GitHub Container Registry

To trigger manually or check status, see GitHub Actions tab in the repository.

