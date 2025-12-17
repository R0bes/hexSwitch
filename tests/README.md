# Test Structure

This directory contains all tests for HexSwitch, organized by test type and functional area.

## Directory Structure

```
tests/
├── unit/              # Unit tests (organized by functional area)
│   ├── adapters/      # Adapter tests (inbound & outbound)
│   ├── handlers/      # Handler system tests
│   ├── core/          # hexswitch_core business logic tests
│   ├── cli/           # CLI command tests
│   ├── config/        # Configuration system tests
│   ├── runtime/       # Runtime orchestration tests
│   ├── templates/     # Template engine tests
│   └── observability/ # Observability tests
│
├── integration/       # Integration tests
│   └── fixtures/      # Integration test fixtures
│
└── fixtures/          # Shared test fixtures
    └── mock_adapters/  # Mock adapter implementations
```

## Test Organization

### Unit Tests (`tests/unit/`)

Unit tests are organized by functional area to improve maintainability and discoverability:

- **`adapters/`** - All adapter tests (HTTP, gRPC, WebSocket, MCP, etc.)
  - **`base/`** - Shared test utilities and base classes
  - **`test_inbound_adapters.py`** - Parametrized tests for all inbound adapters
  - **`test_outbound_adapters.py`** - Parametrized tests for all outbound adapters
  - **`[adapter_name]/`** - Adapter-specific tests (e.g., `http/`, `grpc/`, `websocket/`)
- **`handlers/`** - Handler loading, port system, helpers
- **`core/`** - Business logic and port implementations
- **`cli/`** - CLI commands and templates
- **`config/`** - Configuration loading and validation
- **`runtime/`** - Runtime orchestration and lifecycle
- **`templates/`** - Template engine and edge cases
- **`observability/`** - Metrics and tracing

### Integration Tests (`tests/integration/`)

Integration tests verify end-to-end functionality:

- `test_e2e_complete.py` - Complete end-to-end scenarios
- `test_multi_adapter.py` - Multi-adapter scenarios
- `test_runtime_execution.py` - Runtime execution with various adapters
- `test_observability_stress.py` - Observability under load

## Running Tests

### All Tests
```bash
pytest
```

### Unit Tests Only
```bash
pytest tests/unit
```

### Integration Tests Only
```bash
pytest tests/integration
```

### Specific Area
```bash
pytest tests/unit/adapters
pytest tests/unit/handlers
pytest tests/unit/core
```

### Specific Test File
```bash
pytest tests/unit/adapters/test_inbound_adapters.py
pytest tests/unit/adapters/test_outbound_adapters.py
pytest tests/unit/adapters/http/test_http_specific.py
```

### With Coverage
```bash
pytest --cov=src/hexswitch --cov-report=html
```

## Test Naming Convention

- Test files: `test_<module_name>.py`
- Test functions: `test_<functionality>`
- Test classes: `Test<ClassName>`

## Adding New Tests

When adding new tests:

1. Place unit tests in the appropriate subdirectory under `tests/unit/`
2. Place integration tests in `tests/integration/`
3. Follow the existing naming conventions
4. Use fixtures from `tests/fixtures/` when appropriate
5. Update this README if adding new test categories




