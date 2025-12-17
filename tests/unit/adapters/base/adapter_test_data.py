"""Adapter test data for parametrized tests."""

from typing import Any, Callable

from hexswitch.adapters.grpc import GrpcAdapterClient, GrpcAdapterServer
from hexswitch.adapters.http import HttpAdapterClient, HttpAdapterServer
from hexswitch.adapters.mcp import McpAdapterClient
from hexswitch.adapters.websocket import WebSocketAdapterClient, WebSocketAdapterServer

# Type alias for adapter test data tuple
# Format: (adapter_name, adapter_class, config_factory, expected_attrs)
InboundAdapterData = tuple[str, type, Callable[[], dict[str, Any]], dict[str, Any]]
OutboundAdapterData = tuple[str, type, Callable[[], dict[str, Any]]]

# Inbound Adapter Test Data
INBOUND_ADAPTERS: list[InboundAdapterData] = [
    (
        "http",
        HttpAdapterServer,
        lambda: {"enabled": True, "port": 0, "routes": []},
        {"port": 8000, "base_path": "", "routes": []},
    ),
    (
        "grpc",
        GrpcAdapterServer,
        lambda: {"enabled": True, "port": 0, "services": []},
        {"port": 50051, "services": []},
    ),
    (
        "websocket",
        WebSocketAdapterServer,
        lambda: {"enabled": True, "port": 0, "routes": []},
        {"port": 8080, "path": "/ws", "routes": []},
    ),
]

# Outbound Adapter Test Data
OUTBOUND_ADAPTERS: list[OutboundAdapterData] = [
    (
        "http_client",
        HttpAdapterClient,
        lambda: {"enabled": True, "base_url": "http://localhost:8000"},
    ),
    (
        "grpc_client",
        GrpcAdapterClient,
        lambda: {"enabled": True, "server_url": "localhost:50051"},
    ),
    (
        "websocket_client",
        WebSocketAdapterClient,
        lambda: {"enabled": True, "url": "ws://localhost:9000"},
    ),
    (
        "mcp_client",
        McpAdapterClient,
        lambda: {"enabled": True, "server_url": "https://mcp.example.com"},
    ),
]

