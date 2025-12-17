"""Unit tests for port registry."""

import pytest

from hexswitch.shared.envelope import Envelope
from hexswitch.ports import PortRegistry, get_port_registry, PortNotFoundError


def test_port_registry_register():
    """Test port registration."""
    registry = PortRegistry()

    def handler(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok"})

    registry.register_handler("test_port", handler)
    assert registry.has_port("test_port")
    
    port = registry.get_port("test_port")
    assert len(port.handlers) == 1
    assert port.handlers[0] == handler


def test_port_registry_multiple_handlers():
    """Test multiple handlers can bind to the same port."""
    registry = PortRegistry()

    def handler1(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok"})

    def handler2(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok2"})

    registry.register_handler("test_port", handler1)
    registry.register_handler("test_port", handler2)  # Should not raise error
    
    port = registry.get_port("test_port")
    assert len(port.handlers) == 2
    assert handler1 in port.handlers
    assert handler2 in port.handlers


def test_port_registry_get_missing():
    """Test getting non-existent port raises error."""
    registry = PortRegistry()
    with pytest.raises(PortNotFoundError):
        registry.get_port("missing_port")


def test_port_registry_list_ports():
    """Test listing all ports."""
    registry = PortRegistry()

    def handler1(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok"})

    def handler2(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok2"})

    registry.register_handler("port1", handler1)
    registry.register_handler("port2", handler2)

    ports = registry.list_ports()
    assert len(ports) == 2
    assert "port1" in ports
    assert "port2" in ports


def test_port_registry_route():
    """Test routing envelope through port."""
    registry = PortRegistry()

    def handler(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok"})

    registry.register_handler("test_port", handler)
    
    envelope = Envelope(path="/test")
    results = registry.route("test_port", envelope)
    
    assert len(results) == 1
    assert results[0].status_code == 200
    assert results[0].data == {"result": "ok"}


def test_get_port_registry_singleton():
    """Test global port registry is singleton."""
    registry1 = get_port_registry()
    registry2 = get_port_registry()
    assert registry1 is registry2

