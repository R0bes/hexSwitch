"""Mock HTTP inbound adapter implementation."""

from typing import Any

from hexswitch.adapters.base import InboundAdapter
from hexswitch.shared.envelope import Envelope


class MockHttpAdapterServer(InboundAdapter):
    """Mock implementation of HttpAdapterServer for testing and visualization."""

    def __init__(self, name: str, config: dict[str, Any]):
        """Initialize mock HTTP adapter.

        Args:
            name: Adapter name.
            config: Adapter configuration dictionary.
        """
        self.name = name
        self.config = config
        self._running = False
        self.port = config.get("port", 8000)
        self.base_path = config.get("base_path", "")
        self.routes = config.get("routes", [])

    def start(self) -> None:
        """Start the mock HTTP adapter."""
        self._running = True

    def stop(self) -> None:
        """Stop the mock HTTP adapter."""
        self._running = False

    def to_envelope(self, *args: Any, **kwargs: Any) -> Envelope:
        """Convert external request to Envelope."""
        return Envelope(port="", data={}, metadata={})

    def from_envelope(self, envelope: Envelope) -> Any:
        """Convert Envelope response to external format."""
        return {"status": "ok", "data": envelope.data}

