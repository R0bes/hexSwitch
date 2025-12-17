# Unit Tests Structure

This directory contains unit tests organized by functional area:

## Directory Structure

- **`adapters/`** - Tests for all adapters (inbound and outbound)
  - `test_adapters_base.py` - Base adapter classes
  - `test_http_adapter.py` - HTTP inbound adapter
  - `test_grpc_adapter.py` - gRPC inbound adapter
  - `test_websocket_adapter.py` - WebSocket inbound adapter
  - `test_http_client_adapter.py` - HTTP client outbound adapter
  - `test_grpc_client_adapter.py` - gRPC client outbound adapter
  - `test_websocket_client_adapter.py` - WebSocket client outbound adapter
  - `test_mcp_client_adapter.py` - MCP client outbound adapter

- **`handlers/`** - Tests for handler system
  - `test_handlers_loader.py` - Handler loading functionality
  - `test_handlers_helpers.py` - Handler helper functions
  - `test_port_registry.py` - Port registry
  - `test_port_decorator.py` - Port decorator
  - `test_port_loader.py` - Port loading

- **`core/`** - Tests for hexswitch_core business logic
  - `test_hexswitch_core_services.py` - Business logic services
  - `test_hexswitch_core_ports.py` - Port implementations

- **`cli/`** - Tests for CLI commands
  - `test_cli.py` - CLI main functionality
  - `test_cli_templates.py` - CLI template commands
  - `test_version.py` - Version command

- **`config/`** - Tests for configuration system
  - `test_config.py` - Configuration loading and validation
  - `test_config_templates.py` - Configuration templates

- **`runtime/`** - Tests for runtime orchestration
  - `test_runtime.py` - Runtime core functionality
  - `test_runtime_orchestration.py` - Runtime orchestration

- **`templates/`** - Tests for template engine
  - `test_templates_engine.py` - Template engine
  - `test_templates_edge_cases.py` - Edge cases

- **`observability/`** - Tests for observability features
  - `test_observability.py` - Metrics and tracing

## Running Tests

Run all unit tests:
```bash
pytest tests/unit
```

Run tests for a specific area:
```bash
pytest tests/unit/adapters
pytest tests/unit/handlers
pytest tests/unit/core
```

Run a specific test file:
```bash
pytest tests/unit/adapters/test_http_adapter.py
```




