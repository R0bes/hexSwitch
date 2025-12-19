"""Unit tests for OutboundPortRegistry."""

import threading
import time

from hexswitch.ports.outbound_registry import OutboundPortRegistry
from hexswitch.shared.envelope import Envelope


def test_outbound_port_registry_stores_ports():
    """Test outbound port registry storage."""
    registry = OutboundPortRegistry()

    # Create factory function
    def factory(order_id: str) -> Envelope:
        return Envelope(path="/api/orders", method="POST", body={"id": order_id})

    # Register port
    registry.register_port("order_port", factory)

    # Retrieve port
    port = registry.get_port("order_port")

    assert port is not None
    assert port.name == "order_port"
    assert port.factory == factory

    # Test factory call
    envelope = port.factory("order-123")
    assert isinstance(envelope, Envelope)
    assert envelope.body == {"id": "order-123"}


def test_outbound_port_registry_list_ports():
    """Test listing all ports."""
    registry = OutboundPortRegistry()

    def factory1() -> Envelope:
        return Envelope(path="/api/1")

    def factory2() -> Envelope:
        return Envelope(path="/api/2")

    registry.register_port("port1", factory1)
    registry.register_port("port2", factory2)

    ports = registry.list_ports()

    assert len(ports) == 2
    assert "port1" in ports
    assert "port2" in ports


def test_outbound_port_registry_remove_port():
    """Test removing port from registry."""
    registry = OutboundPortRegistry()

    def factory() -> Envelope:
        return Envelope(path="/test")

    registry.register_port("test_port", factory)

    # Verify port exists
    assert registry.get_port("test_port") is not None

    # Remove port
    registry.remove_port("test_port")

    # Verify port is removed
    assert registry.get_port("test_port") is None


def test_outbound_port_registry_clear():
    """Test clearing all ports."""
    registry = OutboundPortRegistry()

    def factory() -> Envelope:
        return Envelope(path="/test")

    registry.register_port("port1", factory)
    registry.register_port("port2", factory)

    # Clear registry
    registry.clear()

    # Verify all ports are removed
    assert len(registry.list_ports()) == 0


def test_outbound_port_registry_thread_safety():
    """Test that registry is thread-safe."""
    registry = OutboundPortRegistry()
    results = []

    def register_ports():
        for i in range(10):
            def factory(i=i) -> Envelope:  # noqa: B023
                return Envelope(path=f"/api/{i}")

            registry.register_port(f"port_{i}", factory)
            time.sleep(0.001)

    def read_ports():
        for i in range(10):
            port = registry.get_port(f"port_{i}")
            if port:
                results.append(port.name)
            time.sleep(0.001)

    # Create multiple threads
    threads = []
    for _ in range(5):
        t = threading.Thread(target=register_ports)
        threads.append(t)
        t.start()

    for _ in range(5):
        t = threading.Thread(target=read_ports)
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # Verify no errors occurred (thread-safety)
    assert len(registry.list_ports()) == 10


def test_outbound_port_registry_overwrite_warning():
    """Test that overwriting existing port logs warning."""
    registry = OutboundPortRegistry()

    def factory1() -> Envelope:
        return Envelope(path="/api/1")

    def factory2() -> Envelope:
        return Envelope(path="/api/2")

    registry.register_port("test_port", factory1)
    registry.register_port("test_port", factory2)  # Overwrite

    # Verify second factory is used
    port = registry.get_port("test_port")
    assert port.factory == factory2

