"""Mock WebSocket client outbound adapter implementation."""

from typing import Any

from hexswitch.adapters.base import OutboundAdapter
from hexswitch.shared.envelope import Envelope


class MockWebSocketAdapterClient(OutboundAdapter):
    """Mock implementation of WebSocketAdapterClient for testing and visualization."""

    def __init__(self, name: str, config: dict[str, Any]):
        """Initialize mock WebSocket client adapter.

        Args:
            name: Adapter name.
            config: Adapter configuration dictionary.
        """
        self.name = name
        self.config = config
        self._connected = False
        self.url = config.get("url", "")
        self.timeout = config.get("timeout", 30)
        self.reconnect = config.get("reconnect", True)
        self.reconnect_interval = config.get("reconnect_interval", 5)

    def connect(self) -> None:
        """Connect the mock WebSocket client adapter."""
        self._connected = True

    def disconnect(self) -> None:
        """Disconnect the mock WebSocket client adapter."""
        self._connected = False

    def from_envelope(self, envelope: Envelope) -> Any:
        """Convert Envelope request to external format."""
        return {"type": "message", "data": envelope.data}

    def to_envelope(self, *args: Any, **kwargs: Any) -> Envelope:
        """Convert external response to Envelope."""
        return Envelope(port="", data=kwargs.get("data", {}), metadata={})

