"""Mock gRPC client outbound adapter implementation."""

from typing import Any

from hexswitch.adapters.base import OutboundAdapter
from hexswitch.shared.envelope import Envelope


class MockGrpcAdapterClient(OutboundAdapter):
    """Mock implementation of GrpcAdapterClient for testing and visualization."""

    def __init__(self, name: str, config: dict[str, Any]):
        """Initialize mock gRPC client adapter.

        Args:
            name: Adapter name.
            config: Adapter configuration dictionary.
        """
        self.name = name
        self.config = config
        self._connected = False
        self.server_url = config.get("server_url", "")
        self.proto_path = config.get("proto_path", "")
        self.service_name = config.get("service_name", "")
        self.timeout = config.get("timeout", 30)

    def connect(self) -> None:
        """Connect the mock gRPC client adapter."""
        self._connected = True

    def disconnect(self) -> None:
        """Disconnect the mock gRPC client adapter."""
        self._connected = False

    def from_envelope(self, envelope: Envelope) -> Any:
        """Convert Envelope request to external format."""
        return {"service": self.service_name, "data": envelope.data}

    def to_envelope(self, *args: Any, **kwargs: Any) -> Envelope:
        """Convert external response to Envelope."""
        return Envelope(port="", data=kwargs.get("data", {}), metadata={})

