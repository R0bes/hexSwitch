"""Unit tests for port decorator."""


from hexswitch.ports import get_port_registry, port, reset_port_registry
from hexswitch.shared.envelope import Envelope


def test_port_decorator_registers():
    """Test that @port decorator registers function."""
    reset_port_registry()
    registry = get_port_registry()

    # Use unique name to avoid conflicts
    port_name = f"test_port_unique_{id(registry)}"

    @port(name=port_name)
    def test_handler(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok"})

    assert registry.has_port(port_name)
    port_obj = registry.get_port(port_name)
    assert len(port_obj.handlers) == 1
    assert port_obj.handlers[0] == test_handler
    assert hasattr(test_handler, "_port_name")
    assert test_handler._port_name == port_name


def test_port_decorator_preserves_function():
    """Test that @port decorator preserves function behavior."""
    @port(name="test_port2")
    def test_handler(envelope: Envelope) -> Envelope:
        value = envelope.body.get("value", "default") if envelope.body else "default"
        return Envelope.success({"result": value})

    envelope = Envelope(path="/test", body={"value": "test"})
    result = test_handler(envelope)
    assert result.data == {"result": "test"}


def test_port_decorator_multiple_handlers():
    """Test that multiple handlers can bind to the same port."""
    reset_port_registry()
    registry = get_port_registry()

    @port(name="shared_port")
    def handler1(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok"})

    # Second handler binding to same port should not raise error
    @port(name="shared_port")
    def handler2(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "ok2"})

    # Both handlers should be bound to the port
    port_obj = registry.get_port("shared_port")
    assert len(port_obj.handlers) == 2
    assert handler1 in port_obj.handlers
    assert handler2 in port_obj.handlers

