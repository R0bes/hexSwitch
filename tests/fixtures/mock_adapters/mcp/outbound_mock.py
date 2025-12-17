"""Mock MCP client outbound adapter implementation."""

from typing import Any

from hexswitch.adapters.base import OutboundAdapter
from hexswitch.shared.envelope import Envelope
from tests.fixtures.mock_adapters.http.outbound_mock import MockHttpAdapterClient


class MockMcpAdapterClient(OutboundAdapter):
    """Mock implementation of McpAdapterClient for testing and visualization."""

    def __init__(self, name: str, config: dict[str, Any]):
        """Initialize mock MCP client adapter.

        Args:
            name: Adapter name.
            config: Adapter configuration dictionary.
        """
        self.name = name
        self.config = config
        self._connected = False
        self.server_url = config.get("server_url", "https://mcp.example.com")

        # Create internal mock HTTP client adapter
        http_config = {
            "base_url": self.server_url,
            "timeout": config.get("timeout", 30),
            "headers": {
                "Content-Type": "application/json",
                **config.get("headers", {}),
            },
        }
        self._http_client = MockHttpAdapterClient(f"{name}_http", http_config)
        self._request_id = 0

    def connect(self) -> None:
        """Connect the mock MCP client adapter."""
        if self._connected:
            return

        self._http_client.connect()
        self._connected = True

    def disconnect(self) -> None:
        """Disconnect the mock MCP client adapter."""
        if not self._connected:
            return

        self._http_client.disconnect()
        self._connected = False

    def _get_next_request_id(self) -> int:
        """Get next request ID.

        Returns:
            Next request ID.
        """
        self._request_id += 1
        return self._request_id

    def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        """Call a mock MCP tool.

        Args:
            tool_name: Name of the tool to call.
            arguments: Tool arguments.

        Returns:
            Mock tool result.
        """
        return {"output": f"Mock result for {tool_name}", "arguments": arguments or {}}

    def list_tools(self) -> list[dict[str, Any]]:
        """List available mock MCP tools.

        Returns:
            List of mock tools.
        """
        return [{"name": "mock_tool", "description": "Mock tool for testing"}]

    def list_resources(self) -> list[dict[str, Any]]:
        """List available mock MCP resources.

        Returns:
            List of mock resources.
        """
        return [{"uri": "mock://resource", "name": "Mock Resource"}]

    def get_resource(self, uri: str) -> dict[str, Any]:
        """Get a mock MCP resource.

        Args:
            uri: Resource URI.

        Returns:
            Mock resource data.
        """
        return {"uri": uri, "content": "Mock resource content"}

    def from_envelope(self, envelope: Envelope) -> Any:
        """Convert Envelope request to external format."""
        return {"jsonrpc": "2.0", "method": "call", "params": envelope.data}

    def to_envelope(self, *args: Any, **kwargs: Any) -> Envelope:
        """Convert external response to Envelope."""
        return Envelope(port="", data=kwargs.get("result", {}), metadata={})

