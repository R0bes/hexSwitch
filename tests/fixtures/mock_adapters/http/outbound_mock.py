"""Mock HTTP client outbound adapter implementation."""

from typing import Any
from unittest.mock import Mock

from hexswitch.adapters.base import OutboundAdapter
from hexswitch.shared.envelope import Envelope


class MockHttpAdapterClient(OutboundAdapter):
    """Mock implementation of HttpAdapterClient for testing and visualization."""

    def __init__(self, name: str, config: dict[str, Any]):
        """Initialize mock HTTP client adapter.

        Args:
            name: Adapter name.
            config: Adapter configuration dictionary.
        """
        self.name = name
        self.config = config
        self._connected = False
        self.base_url = config.get("base_url", "")
        self.timeout = config.get("timeout", 30)
        self.headers = config.get("headers", {})
        self.session: Mock | None = None

    def connect(self) -> None:
        """Connect the mock HTTP client adapter."""
        if self._connected:
            return

        # Create a mock session
        self.session = Mock()
        self.session.headers = self.headers.copy()
        self._connected = True

    def disconnect(self) -> None:
        """Disconnect the mock HTTP client adapter."""
        if not self._connected:
            return

        self.session = None
        self._connected = False

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> Mock:
        """Make mock HTTP request.

        Args:
            method: HTTP method.
            path: Request path.
            params: Query parameters.
            json_data: JSON body data.
            headers: Additional headers.
            timeout: Request timeout.

        Returns:
            Mock response object.
        """
        if not self._connected or not self.session:
            raise RuntimeError(f"Mock HTTP client adapter '{self.name}' is not connected")

        # Create a mock response
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok", "method": method, "path": path}
        mock_response.raise_for_status = Mock()
        return mock_response

    def from_envelope(self, envelope: Envelope) -> Any:
        """Convert Envelope request to external format."""
        return {"method": "POST", "url": self.base_url, "json": envelope.data}

    def to_envelope(self, *args: Any, **kwargs: Any) -> Envelope:
        """Convert external response to Envelope."""
        return Envelope(port="", data=kwargs.get("data", {}), metadata={})

