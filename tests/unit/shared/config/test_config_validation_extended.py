"""Extended unit tests for config validation functions."""

import pytest

from hexswitch.shared.config.config import (
    ConfigError,
    _validate_adapters,
    _validate_grpc_adapter,
    _validate_grpc_client_adapter,
    _validate_handler_reference,
    _validate_http_adapter,
    _validate_http_client_adapter,
    _validate_mcp_adapter,
    _validate_mcp_client_adapter,
    _validate_nats_adapter,
    _validate_nats_client_adapter,
    _validate_websocket_adapter,
    _validate_websocket_client_adapter,
)


class TestConfigValidationFunctions:
    """Test config validation helper functions."""

    def test_validate_http_adapter_valid(self) -> None:
        """Test validating valid HTTP adapter config."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "port": "test_port",
                }
            ],
        }
        _validate_http_adapter("http", config, "inbound")  # Should not raise

    def test_validate_http_adapter_invalid_port(self) -> None:
        """Test validating HTTP adapter with invalid port."""
        config = {
            "enabled": True,
            "port": 70000,  # Invalid port
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_invalid_route(self) -> None:
        """Test validating HTTP adapter with invalid route."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [
                {
                    "path": "/test",
                    "method": "INVALID",  # Invalid method
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_client_adapter_valid(self) -> None:
        """Test validating valid HTTP client adapter config."""
        config = {
            "enabled": True,
            "base_url": "http://localhost:8000",
            "timeout": 30.0,
        }
        _validate_http_client_adapter("http_client", config, "outbound")  # Should not raise

    def test_validate_http_client_adapter_invalid_timeout(self) -> None:
        """Test validating HTTP client adapter with invalid timeout."""
        config = {
            "enabled": True,
            "base_url": "http://localhost:8000",
            "timeout": -1,  # Invalid timeout
        }
        with pytest.raises(ConfigError):
            _validate_http_client_adapter("http_client", config, "outbound")

    def test_validate_grpc_adapter_valid(self) -> None:
        """Test validating valid gRPC adapter config."""
        config = {
            "enabled": True,
            "port": 50051,
            "services": [
                {
                    "service_name": "TestService",
                    "methods": [
                        {
                            "method_name": "TestMethod",
                            "port": "test_port",
                        }
                    ],
                }
            ],
        }
        _validate_grpc_adapter("grpc", config, "inbound")  # Should not raise

    def test_validate_grpc_adapter_invalid_port(self) -> None:
        """Test validating gRPC adapter with invalid port."""
        config = {
            "enabled": True,
            "port": 70000,  # Invalid port
        }
        with pytest.raises(ConfigError):
            _validate_grpc_adapter("grpc", config, "inbound")

    def test_validate_grpc_client_adapter_valid(self) -> None:
        """Test validating valid gRPC client adapter config."""
        config = {
            "enabled": True,
            "server_url": "localhost:50051",
            "timeout": 30.0,
        }
        _validate_grpc_client_adapter("grpc_client", config, "outbound")  # Should not raise

    def test_validate_grpc_client_adapter_invalid_timeout(self) -> None:
        """Test validating gRPC client adapter with invalid timeout."""
        config = {
            "enabled": True,
            "server_url": "localhost:50051",
            "timeout": -1,  # Invalid timeout
        }
        with pytest.raises(ConfigError):
            _validate_grpc_client_adapter("grpc_client", config, "outbound")

    def test_validate_websocket_adapter_valid(self) -> None:
        """Test validating valid WebSocket adapter config."""
        config = {
            "enabled": True,
            "port": 8080,
            "routes": [
                {
                    "path": "/ws",
                    "port": "test_port",
                }
            ],
        }
        _validate_websocket_adapter("websocket", config, "inbound")  # Should not raise

    def test_validate_websocket_adapter_invalid_port(self) -> None:
        """Test validating WebSocket adapter with invalid port."""
        config = {
            "enabled": True,
            "port": 70000,  # Invalid port
        }
        with pytest.raises(ConfigError):
            _validate_websocket_adapter("websocket", config, "inbound")

    def test_validate_websocket_client_adapter_valid(self) -> None:
        """Test validating valid WebSocket client adapter config."""
        config = {
            "enabled": True,
            "url": "ws://localhost:9000",
            "timeout": 30.0,
        }
        _validate_websocket_client_adapter("websocket_client", config, "outbound")  # Should not raise

    def test_validate_websocket_client_adapter_invalid_timeout(self) -> None:
        """Test validating WebSocket client adapter with invalid timeout."""
        config = {
            "enabled": True,
            "url": "ws://localhost:9000",
            "timeout": -1,  # Invalid timeout
        }
        with pytest.raises(ConfigError):
            _validate_websocket_client_adapter("websocket_client", config, "outbound")

    def test_validate_mcp_adapter_valid(self) -> None:
        """Test validating valid MCP adapter config."""
        config = {
            "enabled": True,
            "server_url": "https://mcp.example.com",
        }
        _validate_mcp_adapter("mcp", config, "inbound")  # Should not raise

    def test_validate_mcp_adapter_missing_url(self) -> None:
        """Test validating MCP adapter with missing URL."""
        config = {
            "enabled": True,
        }
        with pytest.raises(ConfigError):
            _validate_mcp_adapter("mcp", config, "inbound")

    def test_validate_mcp_client_adapter_valid(self) -> None:
        """Test validating valid MCP client adapter config."""
        config = {
            "enabled": True,
            "server_url": "https://mcp.example.com",
            "timeout": 30.0,
        }
        _validate_mcp_client_adapter("mcp_client", config, "outbound")  # Should not raise

    def test_validate_mcp_client_adapter_invalid_timeout(self) -> None:
        """Test validating MCP client adapter with invalid timeout."""
        config = {
            "enabled": True,
            "server_url": "https://mcp.example.com",
            "timeout": -1,  # Invalid timeout
        }
        with pytest.raises(ConfigError):
            _validate_mcp_client_adapter("mcp_client", config, "outbound")

    def test_validate_nats_adapter_valid(self) -> None:
        """Test validating valid NATS adapter config."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222"],
            "subjects": [
                {
                    "subject": "test.subject",
                    "port": "test_handler",
                }
            ],
        }
        _validate_nats_adapter("nats", config, "inbound")  # Should not raise

    def test_validate_nats_adapter_missing_servers(self) -> None:
        """Test validating NATS adapter with missing servers."""
        config = {
            "enabled": True,
            "subjects": [{"subject": "test", "port": "test_handler"}],
        }
        with pytest.raises(ConfigError):
            _validate_nats_adapter("nats", config, "inbound")

    def test_validate_nats_adapter_invalid_subject(self) -> None:
        """Test validating NATS adapter with invalid subject config."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222"],
            "subjects": [
                {
                    "subject": "test.subject",
                    # Missing both handler and port
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_nats_adapter("nats", config, "inbound")

    def test_validate_nats_client_adapter_valid(self) -> None:
        """Test validating valid NATS client adapter config."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222"],
            "timeout": 30.0,
        }
        _validate_nats_client_adapter("nats_client", config, "outbound")  # Should not raise

    def test_validate_nats_client_adapter_missing_servers(self) -> None:
        """Test validating NATS client adapter with missing servers."""
        config = {
            "enabled": True,
            "timeout": 30.0,
        }
        with pytest.raises(ConfigError):
            _validate_nats_client_adapter("nats_client", config, "outbound")

    def test_validate_nats_client_adapter_invalid_timeout(self) -> None:
        """Test validating NATS client adapter with invalid timeout."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222"],
            "timeout": -1,  # Invalid timeout
        }
        with pytest.raises(ConfigError):
            _validate_nats_client_adapter("nats_client", config, "outbound")

    def test_validate_adapters_invalid_adapter_type(self) -> None:
        """Test validating adapters with invalid adapter type."""
        adapters = {
            "unknown_adapter": {
                "enabled": True,
            }
        }
        # Should not raise for unknown adapters (just skip validation)
        _validate_adapters(adapters, "inbound")  # Should not raise

    def test_validate_adapters_not_dict(self) -> None:
        """Test validating adapters that are not dictionaries."""
        adapters = {
            "http": "not a dict",  # Invalid
        }
        with pytest.raises(ConfigError):
            _validate_adapters(adapters, "inbound")

    def test_validate_adapters_invalid_enabled_flag(self) -> None:
        """Test validating adapters with invalid enabled flag."""
        adapters = {
            "http": {
                "enabled": "true",  # Should be boolean, not string
            }
        }
        with pytest.raises(ConfigError):
            _validate_adapters(adapters, "inbound")

    def test_validate_handler_reference_missing_colon(self) -> None:
        """Test validating handler reference without colon."""
        with pytest.raises(ConfigError, match="Invalid handler format"):
            _validate_handler_reference("invalid_handler", "http", "inbound", 0)

    def test_validate_handler_reference_empty_module(self) -> None:
        """Test validating handler reference with empty module path."""
        with pytest.raises(ConfigError, match="Module path and function name must not be empty"):
            _validate_handler_reference(":function", "http", "inbound", 0)

    def test_validate_handler_reference_empty_function(self) -> None:
        """Test validating handler reference with empty function name."""
        with pytest.raises(ConfigError, match="Module path and function name must not be empty"):
            _validate_handler_reference("module:", "http", "inbound", 0)

    def test_validate_handler_reference_valid(self) -> None:
        """Test validating valid handler reference."""
        # Should not raise
        _validate_handler_reference("module.path:function_name", "http", "inbound", 0)

    def test_validate_handler_reference_without_route_index(self) -> None:
        """Test validating handler reference without route index."""
        with pytest.raises(ConfigError):
            _validate_handler_reference("invalid", "http", "inbound", None)

    def test_validate_http_adapter_invalid_base_path(self) -> None:
        """Test validating HTTP adapter with invalid base_path type."""
        config = {
            "enabled": True,
            "base_path": 123,  # Should be string
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_invalid_port_type(self) -> None:
        """Test validating HTTP adapter with invalid port type."""
        config = {
            "enabled": True,
            "port": "8000",  # Should be integer
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_port_too_low(self) -> None:
        """Test validating HTTP adapter with port too low."""
        config = {
            "enabled": True,
            "port": 0,  # Too low
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_port_too_high(self) -> None:
        """Test validating HTTP adapter with port too high."""
        config = {
            "enabled": True,
            "port": 65536,  # Too high
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_routes_not_list(self) -> None:
        """Test validating HTTP adapter with routes not a list."""
        config = {
            "enabled": True,
            "routes": "not_a_list",
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_route_not_dict(self) -> None:
        """Test validating HTTP adapter with route not a dict."""
        config = {
            "enabled": True,
            "routes": ["not_a_dict"],
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_route_missing_path(self) -> None:
        """Test validating HTTP adapter route missing path."""
        config = {
            "enabled": True,
            "routes": [
                {
                    "method": "GET",
                    "port": "test_port",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_route_path_not_string(self) -> None:
        """Test validating HTTP adapter route with path not a string."""
        config = {
            "enabled": True,
            "routes": [
                {
                    "path": 123,
                    "method": "GET",
                    "port": "test_port",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_route_missing_method(self) -> None:
        """Test validating HTTP adapter route missing method."""
        config = {
            "enabled": True,
            "routes": [
                {
                    "path": "/test",
                    "port": "test_port",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_route_method_not_string(self) -> None:
        """Test validating HTTP adapter route with method not a string."""
        config = {
            "enabled": True,
            "routes": [
                {
                    "path": "/test",
                    "method": 123,
                    "port": "test_port",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_route_invalid_method(self) -> None:
        """Test validating HTTP adapter route with invalid method."""
        config = {
            "enabled": True,
            "routes": [
                {
                    "path": "/test",
                    "method": "INVALID",
                    "port": "test_port",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_route_missing_handler_and_port(self) -> None:
        """Test validating HTTP adapter route missing both handler and port."""
        config = {
            "enabled": True,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_route_handler_not_string(self) -> None:
        """Test validating HTTP adapter route with handler not a string."""
        config = {
            "enabled": True,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "handler": 123,
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_route_port_not_string(self) -> None:
        """Test validating HTTP adapter route with port not a string."""
        config = {
            "enabled": True,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "port": 123,
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_adapter_route_port_empty(self) -> None:
        """Test validating HTTP adapter route with empty port."""
        config = {
            "enabled": True,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "port": "",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_http_adapter("http", config, "inbound")

    def test_validate_http_client_adapter_invalid_base_url_type(self) -> None:
        """Test validating HTTP client adapter with invalid base_url type."""
        config = {
            "enabled": True,
            "base_url": 123,  # Should be string
        }
        with pytest.raises(ConfigError):
            _validate_http_client_adapter("http_client", config, "outbound")

    def test_validate_http_client_adapter_invalid_timeout_type(self) -> None:
        """Test validating HTTP client adapter with invalid timeout type."""
        config = {
            "enabled": True,
            "timeout": "30",  # Should be number
        }
        with pytest.raises(ConfigError):
            _validate_http_client_adapter("http_client", config, "outbound")

    def test_validate_http_client_adapter_timeout_zero(self) -> None:
        """Test validating HTTP client adapter with timeout zero."""
        config = {
            "enabled": True,
            "timeout": 0,  # Should be positive
        }
        with pytest.raises(ConfigError):
            _validate_http_client_adapter("http_client", config, "outbound")

    def test_validate_http_client_adapter_invalid_headers_type(self) -> None:
        """Test validating HTTP client adapter with invalid headers type."""
        config = {
            "enabled": True,
            "headers": "not_a_dict",
        }
        with pytest.raises(ConfigError):
            _validate_http_client_adapter("http_client", config, "outbound")

    def test_validate_mcp_client_adapter_missing_server_url(self) -> None:
        """Test validating MCP client adapter with missing server_url."""
        config = {
            "enabled": True,
        }
        with pytest.raises(ConfigError):
            _validate_mcp_client_adapter("mcp_client", config, "outbound")

    def test_validate_mcp_client_adapter_server_url_not_string(self) -> None:
        """Test validating MCP client adapter with server_url not a string."""
        config = {
            "enabled": True,
            "server_url": 123,
        }
        with pytest.raises(ConfigError):
            _validate_mcp_client_adapter("mcp_client", config, "outbound")

    def test_validate_mcp_client_adapter_server_url_empty(self) -> None:
        """Test validating MCP client adapter with empty server_url."""
        config = {
            "enabled": True,
            "server_url": "",
        }
        with pytest.raises(ConfigError):
            _validate_mcp_client_adapter("mcp_client", config, "outbound")

    def test_validate_grpc_adapter_invalid_proto_path_type(self) -> None:
        """Test validating gRPC adapter with invalid proto_path type."""
        config = {
            "enabled": True,
            "proto_path": 123,  # Should be string
        }
        with pytest.raises(ConfigError):
            _validate_grpc_adapter("grpc", config, "inbound")

    def test_validate_grpc_adapter_services_not_list(self) -> None:
        """Test validating gRPC adapter with services not a list."""
        config = {
            "enabled": True,
            "services": "not_a_list",
        }
        with pytest.raises(ConfigError):
            _validate_grpc_adapter("grpc", config, "inbound")

    def test_validate_grpc_adapter_service_not_dict(self) -> None:
        """Test validating gRPC adapter with service not a dict."""
        config = {
            "enabled": True,
            "services": ["not_a_dict"],
        }
        with pytest.raises(ConfigError):
            _validate_grpc_adapter("grpc", config, "inbound")

    def test_validate_grpc_adapter_service_missing_service_name(self) -> None:
        """Test validating gRPC adapter service missing service_name."""
        config = {
            "enabled": True,
            "services": [
                {
                    "methods": [],
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_grpc_adapter("grpc", config, "inbound")

    def test_validate_grpc_adapter_service_service_name_not_string(self) -> None:
        """Test validating gRPC adapter service with service_name not a string."""
        config = {
            "enabled": True,
            "services": [
                {
                    "service_name": 123,
                    "methods": [],
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_grpc_adapter("grpc", config, "inbound")

    def test_validate_grpc_adapter_methods_not_list(self) -> None:
        """Test validating gRPC adapter with methods not a list."""
        config = {
            "enabled": True,
            "services": [
                {
                    "service_name": "TestService",
                    "methods": "not_a_list",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_grpc_adapter("grpc", config, "inbound")

    def test_validate_grpc_adapter_method_not_dict(self) -> None:
        """Test validating gRPC adapter with method not a dict."""
        config = {
            "enabled": True,
            "services": [
                {
                    "service_name": "TestService",
                    "methods": ["not_a_dict"],
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_grpc_adapter("grpc", config, "inbound")

    def test_validate_grpc_adapter_method_missing_method_name(self) -> None:
        """Test validating gRPC adapter method missing method_name."""
        config = {
            "enabled": True,
            "services": [
                {
                    "service_name": "TestService",
                    "methods": [
                        {
                            "port": "test_port",
                        }
                    ],
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_grpc_adapter("grpc", config, "inbound")

    def test_validate_grpc_adapter_method_method_name_not_string(self) -> None:
        """Test validating gRPC adapter method with method_name not a string."""
        config = {
            "enabled": True,
            "services": [
                {
                    "service_name": "TestService",
                    "methods": [
                        {
                            "method_name": 123,
                            "port": "test_port",
                        }
                    ],
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_grpc_adapter("grpc", config, "inbound")

    def test_validate_grpc_adapter_method_missing_handler_and_port(self) -> None:
        """Test validating gRPC adapter method missing both handler and port."""
        config = {
            "enabled": True,
            "services": [
                {
                    "service_name": "TestService",
                    "methods": [
                        {
                            "method_name": "TestMethod",
                        }
                    ],
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_grpc_adapter("grpc", config, "inbound")

    def test_validate_grpc_client_adapter_missing_server_url(self) -> None:
        """Test validating gRPC client adapter with missing server_url."""
        config = {
            "enabled": True,
        }
        with pytest.raises(ConfigError):
            _validate_grpc_client_adapter("grpc_client", config, "outbound")

    def test_validate_grpc_client_adapter_server_url_not_string(self) -> None:
        """Test validating gRPC client adapter with server_url not a string."""
        config = {
            "enabled": True,
            "server_url": 123,
        }
        with pytest.raises(ConfigError):
            _validate_grpc_client_adapter("grpc_client", config, "outbound")

    def test_validate_grpc_client_adapter_server_url_empty(self) -> None:
        """Test validating gRPC client adapter with empty server_url."""
        config = {
            "enabled": True,
            "server_url": "",
        }
        with pytest.raises(ConfigError):
            _validate_grpc_client_adapter("grpc_client", config, "outbound")

    def test_validate_grpc_client_adapter_invalid_proto_path_type(self) -> None:
        """Test validating gRPC client adapter with invalid proto_path type."""
        config = {
            "enabled": True,
            "server_url": "localhost:50051",
            "proto_path": 123,  # Should be string
        }
        with pytest.raises(ConfigError):
            _validate_grpc_client_adapter("grpc_client", config, "outbound")

    def test_validate_grpc_client_adapter_invalid_service_name_type(self) -> None:
        """Test validating gRPC client adapter with invalid service_name type."""
        config = {
            "enabled": True,
            "server_url": "localhost:50051",
            "service_name": 123,  # Should be string
        }
        with pytest.raises(ConfigError):
            _validate_grpc_client_adapter("grpc_client", config, "outbound")

    def test_validate_websocket_adapter_invalid_path_type(self) -> None:
        """Test validating WebSocket adapter with invalid path type."""
        config = {
            "enabled": True,
            "path": 123,  # Should be string
        }
        with pytest.raises(ConfigError):
            _validate_websocket_adapter("websocket", config, "inbound")

    def test_validate_websocket_client_adapter_missing_url(self) -> None:
        """Test validating WebSocket client adapter with missing url."""
        config = {
            "enabled": True,
        }
        with pytest.raises(ConfigError):
            _validate_websocket_client_adapter("websocket_client", config, "outbound")

    def test_validate_websocket_client_adapter_url_not_string(self) -> None:
        """Test validating WebSocket client adapter with url not a string."""
        config = {
            "enabled": True,
            "url": 123,
        }
        with pytest.raises(ConfigError):
            _validate_websocket_client_adapter("websocket_client", config, "outbound")

    def test_validate_websocket_client_adapter_url_empty(self) -> None:
        """Test validating WebSocket client adapter with empty url."""
        config = {
            "enabled": True,
            "url": "",
        }
        with pytest.raises(ConfigError):
            _validate_websocket_client_adapter("websocket_client", config, "outbound")

    def test_validate_websocket_client_adapter_invalid_reconnect_type(self) -> None:
        """Test validating WebSocket client adapter with invalid reconnect type."""
        config = {
            "enabled": True,
            "url": "ws://localhost:9000",
            "reconnect": "true",  # Should be boolean
        }
        with pytest.raises(ConfigError):
            _validate_websocket_client_adapter("websocket_client", config, "outbound")

    def test_validate_websocket_client_adapter_invalid_reconnect_interval_type(self) -> None:
        """Test validating WebSocket client adapter with invalid reconnect_interval type."""
        config = {
            "enabled": True,
            "url": "ws://localhost:9000",
            "reconnect_interval": "30",  # Should be number
        }
        with pytest.raises(ConfigError):
            _validate_websocket_client_adapter("websocket_client", config, "outbound")

    def test_validate_websocket_client_adapter_reconnect_interval_zero(self) -> None:
        """Test validating WebSocket client adapter with reconnect_interval zero."""
        config = {
            "enabled": True,
            "url": "ws://localhost:9000",
            "reconnect_interval": 0,  # Should be positive
        }
        with pytest.raises(ConfigError):
            _validate_websocket_client_adapter("websocket_client", config, "outbound")

    def test_validate_mcp_adapter_missing_server_url(self) -> None:
        """Test validating MCP adapter with missing server_url."""
        config = {
            "enabled": True,
        }
        with pytest.raises(ConfigError):
            _validate_mcp_adapter("mcp", config, "inbound")

    def test_validate_mcp_adapter_server_url_not_string(self) -> None:
        """Test validating MCP adapter with server_url not a string."""
        config = {
            "enabled": True,
            "server_url": 123,
        }
        with pytest.raises(ConfigError):
            _validate_mcp_adapter("mcp", config, "inbound")

    def test_validate_mcp_adapter_server_url_empty(self) -> None:
        """Test validating MCP adapter with empty server_url."""
        config = {
            "enabled": True,
            "server_url": "",
        }
        with pytest.raises(ConfigError):
            _validate_mcp_adapter("mcp", config, "inbound")

    def test_validate_mcp_adapter_methods_not_list(self) -> None:
        """Test validating MCP adapter with methods not a list."""
        config = {
            "enabled": True,
            "server_url": "https://mcp.example.com",
            "methods": "not_a_list",
        }
        with pytest.raises(ConfigError):
            _validate_mcp_adapter("mcp", config, "inbound")

    def test_validate_mcp_adapter_method_not_dict(self) -> None:
        """Test validating MCP adapter with method not a dict."""
        config = {
            "enabled": True,
            "server_url": "https://mcp.example.com",
            "methods": ["not_a_dict"],
        }
        with pytest.raises(ConfigError):
            _validate_mcp_adapter("mcp", config, "inbound")

    def test_validate_mcp_adapter_method_missing_method_name(self) -> None:
        """Test validating MCP adapter method missing method_name."""
        config = {
            "enabled": True,
            "server_url": "https://mcp.example.com",
            "methods": [
                {
                    "port": "test_port",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_mcp_adapter("mcp", config, "inbound")

    def test_validate_mcp_adapter_method_method_name_not_string(self) -> None:
        """Test validating MCP adapter method with method_name not a string."""
        config = {
            "enabled": True,
            "server_url": "https://mcp.example.com",
            "methods": [
                {
                    "method_name": 123,
                    "port": "test_port",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_mcp_adapter("mcp", config, "inbound")

    def test_validate_nats_adapter_servers_not_string_or_list(self) -> None:
        """Test validating NATS adapter with servers not string or list."""
        config = {
            "enabled": True,
            "servers": 123,  # Should be string or list
        }
        with pytest.raises(ConfigError):
            _validate_nats_adapter("nats", config, "inbound")

    def test_validate_nats_adapter_servers_list_with_non_string(self) -> None:
        """Test validating NATS adapter with servers list containing non-string."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222", 123],  # Contains non-string
        }
        with pytest.raises(ConfigError):
            _validate_nats_adapter("nats", config, "inbound")

    def test_validate_nats_adapter_subjects_not_list(self) -> None:
        """Test validating NATS adapter with subjects not a list."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222"],
            "subjects": "not_a_list",
        }
        with pytest.raises(ConfigError):
            _validate_nats_adapter("nats", config, "inbound")

    def test_validate_nats_adapter_subject_not_dict(self) -> None:
        """Test validating NATS adapter with subject not a dict."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222"],
            "subjects": ["not_a_dict"],
        }
        with pytest.raises(ConfigError):
            _validate_nats_adapter("nats", config, "inbound")

    def test_validate_nats_adapter_subject_missing_subject(self) -> None:
        """Test validating NATS adapter subject missing subject field."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222"],
            "subjects": [
                {
                    "port": "test_port",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_nats_adapter("nats", config, "inbound")

    def test_validate_nats_adapter_subject_subject_not_string(self) -> None:
        """Test validating NATS adapter subject with subject not a string."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222"],
            "subjects": [
                {
                    "subject": 123,
                    "port": "test_port",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_nats_adapter("nats", config, "inbound")

    def test_validate_nats_adapter_subject_missing_handler_and_port(self) -> None:
        """Test validating NATS adapter subject missing both handler and port."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222"],
            "subjects": [
                {
                    "subject": "test.subject",
                }
            ],
        }
        with pytest.raises(ConfigError):
            _validate_nats_adapter("nats", config, "inbound")

    def test_validate_nats_adapter_invalid_queue_group_type(self) -> None:
        """Test validating NATS adapter with invalid queue_group type."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222"],
            "queue_group": 123,  # Should be string
        }
        with pytest.raises(ConfigError):
            _validate_nats_adapter("nats", config, "inbound")

    def test_validate_nats_client_adapter_servers_not_string_or_list(self) -> None:
        """Test validating NATS client adapter with servers not string or list."""
        config = {
            "enabled": True,
            "servers": 123,  # Should be string or list
        }
        with pytest.raises(ConfigError):
            _validate_nats_client_adapter("nats_client", config, "outbound")

    def test_validate_nats_client_adapter_servers_list_with_non_string(self) -> None:
        """Test validating NATS client adapter with servers list containing non-string."""
        config = {
            "enabled": True,
            "servers": ["nats://localhost:4222", 123],  # Contains non-string
        }
        with pytest.raises(ConfigError):
            _validate_nats_client_adapter("nats_client", config, "outbound")

