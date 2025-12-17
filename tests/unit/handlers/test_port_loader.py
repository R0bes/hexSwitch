"""Unit tests for port loader."""

import pytest

from hexswitch.ports import PortNotFoundError, get_port_registry, port, reset_port_registry
from hexswitch.shared.envelope import Envelope


def test_load_port_success():
    """Test loading registered port."""
    reset_port_registry()

    @port(name="test_load_port")
    def test_handler(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok"})

    registry = get_port_registry()
    assert registry.has_port("test_load_port")
    port_obj = registry.get_port("test_load_port")
    assert len(port_obj.handlers) == 1
    assert port_obj.handlers[0] == test_handler


def test_load_port_missing():
    """Test loading non-existent port raises error."""
    reset_port_registry()
    registry = get_port_registry()
    with pytest.raises(PortNotFoundError):
        registry.get_port("missing_port")


def test_load_port_calls_handler():
    """Test that loaded port can be called."""
    reset_port_registry()

    @port(name="test_call_port")
    def test_handler(envelope: Envelope) -> Envelope:
        value = envelope.body.get("input", "default") if envelope.body else "default"
        return Envelope.success({"value": value})

    registry = get_port_registry()
    envelope = Envelope(path="/test", body={"input": "test"})
    results = registry.route("test_call_port", envelope)

    assert len(results) == 1
    assert results[0].data == {"value": "test"}

