"""Unit tests for adapter base classes."""

import pytest

from hexswitch.adapters.base import InboundAdapter, OutboundAdapter
from hexswitch.adapters.exceptions import AdapterStartError, AdapterStopError


class TestInboundAdapter(InboundAdapter):
    """Test implementation of InboundAdapter."""

    def start(self) -> None:
        """Start the test adapter."""
        self._running = True

    def stop(self) -> None:
        """Stop the test adapter."""
        self._running = False


class TestOutboundAdapter(OutboundAdapter):
    """Test implementation of OutboundAdapter."""

    def connect(self) -> None:
        """Connect the test adapter."""
        self._connected = True

    def disconnect(self) -> None:
        """Disconnect the test adapter."""
        self._connected = False


def test_inbound_adapter_initialization() -> None:
    """Test InboundAdapter initialization."""
    adapter = TestInboundAdapter("test", {"enabled": True})
    assert adapter.name == "test"
    assert adapter.config == {"enabled": True}
    assert adapter.is_running() is False


def test_inbound_adapter_lifecycle() -> None:
    """Test InboundAdapter start/stop lifecycle."""
    adapter = TestInboundAdapter("test", {})
    assert adapter.is_running() is False

    adapter.start()
    assert adapter.is_running() is True

    adapter.stop()
    assert adapter.is_running() is False


def test_outbound_adapter_initialization() -> None:
    """Test OutboundAdapter initialization."""
    adapter = TestOutboundAdapter("test", {"dsn": "test://localhost"})
    assert adapter.name == "test"
    assert adapter.config == {"dsn": "test://localhost"}
    assert adapter.is_connected() is False


def test_outbound_adapter_lifecycle() -> None:
    """Test OutboundAdapter connect/disconnect lifecycle."""
    adapter = TestOutboundAdapter("test", {})
    assert adapter.is_connected() is False

    adapter.connect()
    assert adapter.is_connected() is True

    adapter.disconnect()
    assert adapter.is_connected() is False


def test_inbound_adapter_abstract() -> None:
    """Test that InboundAdapter cannot be instantiated directly."""
    with pytest.raises(TypeError):
        InboundAdapter("test", {})  # type: ignore


def test_outbound_adapter_abstract() -> None:
    """Test that OutboundAdapter cannot be instantiated directly."""
    with pytest.raises(TypeError):
        OutboundAdapter("test", {})  # type: ignore

