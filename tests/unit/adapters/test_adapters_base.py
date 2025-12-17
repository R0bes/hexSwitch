"""Unit tests for adapter interfaces."""

import pytest

from hexswitch.adapters.base import InboundAdapter, OutboundAdapter
from typing import Any

from hexswitch.shared.envelope import Envelope


class MockInboundAdapter(InboundAdapter):
    """Mock implementation of InboundAdapter for testing."""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self._running = False

    def start(self) -> None:
        """Start the test adapter."""
        self._running = True

    def stop(self) -> None:
        """Stop the test adapter."""
        self._running = False

    def to_envelope(self, *args, **kwargs) -> Envelope:
        """Convert external request to Envelope."""
        return Envelope(port="", data={}, metadata={})

    def from_envelope(self, envelope: Envelope) -> Any:
        """Convert Envelope response to external format."""
        return {"status": "ok"}


class MockOutboundAdapter(OutboundAdapter):
    """Mock implementation of OutboundAdapter for testing."""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self._connected = False

    def connect(self) -> None:
        """Connect the test adapter."""
        self._connected = True

    def disconnect(self) -> None:
        """Disconnect the test adapter."""
        self._connected = False

    def request(self, envelope: Envelope) -> Envelope:
        """Send request and get response."""
        return Envelope.success({"echo": envelope.data})

    def from_envelope(self, envelope: Envelope) -> Any:
        """Convert Envelope request to external format."""
        return {"data": envelope.data}

    def to_envelope(self, *args, **kwargs) -> Envelope:
        """Convert external response to Envelope."""
        return Envelope(port="", data={}, metadata={})


def test_inbound_adapter_initialization() -> None:
    """Test InboundAdapter initialization."""
    adapter = MockInboundAdapter("test", {"enabled": True})
    assert adapter.name == "test"
    assert adapter.config == {"enabled": True}
    assert adapter.is_running() is False


def test_inbound_adapter_lifecycle() -> None:
    """Test InboundAdapter start/stop lifecycle."""
    adapter = MockInboundAdapter("test", {})
    assert adapter.is_running() is False

    adapter.start()
    assert adapter.is_running() is True

    adapter.stop()
    assert adapter.is_running() is False


def test_outbound_adapter_initialization() -> None:
    """Test OutboundAdapter initialization."""
    adapter = MockOutboundAdapter("test", {"dsn": "test://localhost"})
    assert adapter.name == "test"
    assert adapter.config == {"dsn": "test://localhost"}
    assert adapter.is_connected() is False


def test_outbound_adapter_lifecycle() -> None:
    """Test OutboundAdapter connect/disconnect lifecycle."""
    adapter = MockOutboundAdapter("test", {})
    assert adapter.is_connected() is False

    adapter.connect()
    assert adapter.is_connected() is True

    adapter.disconnect()
    assert adapter.is_connected() is False


def test_inbound_interface_abstract() -> None:
    """Test that InboundAdapter cannot be instantiated directly."""
    with pytest.raises(TypeError):
        InboundAdapter()  # type: ignore


def test_outbound_interface_abstract() -> None:
    """Test that OutboundAdapter cannot be instantiated directly."""
    with pytest.raises(TypeError):
        OutboundAdapter()  # type: ignore


