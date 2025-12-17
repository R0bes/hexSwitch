"""Unit tests for ports system."""

import pytest

from hexswitch.ports import BroadcastStrategy, FirstStrategy, NoHandlersError, Port, PortNotFoundError, PortRegistry, RoundRobinStrategy, port, reset_port_registry
from hexswitch.shared.envelope import Envelope


class TestPort:
    """Test Port class."""

    def test_port_creation(self):
        """Test creating a port."""
        p = Port(name="test", handlers=[])
        assert p.name == "test"
        assert len(p.handlers) == 0
        assert isinstance(p.routing_strategy, FirstStrategy)

    def test_port_add_handler(self):
        """Test adding handlers to port."""
        def handler(e): return e

        p = Port(name="test")
        p.add_handler(handler)

        assert len(p.handlers) == 1
        assert p.handlers[0] == handler

    def test_port_route_no_handlers_raises(self):
        """Test routing with no handlers raises error."""
        p = Port(name="test")

        with pytest.raises(NoHandlersError):
            p.route(Envelope(path="/test"))


class TestFirstStrategy:
    """Test FirstStrategy routing."""

    def test_routes_to_first_handler_only(self):
        """Test that only first handler is called."""
        def handler1(e): return Envelope.success({"handler": 1})
        def handler2(e): return Envelope.success({"handler": 2})

        strategy = FirstStrategy()
        results = strategy.route(Envelope(path="/test"), [handler1, handler2])

        assert len(results) == 1
        assert results[0].data["handler"] == 1


class TestBroadcastStrategy:
    """Test BroadcastStrategy routing."""

    def test_routes_to_all_handlers(self):
        """Test that all handlers are called."""
        def handler1(e): return Envelope.success({"handler": 1})
        def handler2(e): return Envelope.success({"handler": 2})
        def handler3(e): return Envelope.success({"handler": 3})

        strategy = BroadcastStrategy()
        results = strategy.route(Envelope(path="/test"), [handler1, handler2, handler3])

        assert len(results) == 3
        assert results[0].data["handler"] == 1
        assert results[1].data["handler"] == 2
        assert results[2].data["handler"] == 3

    def test_collects_errors_as_envelopes(self):
        """Test that handler errors are collected as error envelopes."""
        def handler1(e): return Envelope.success({"handler": 1})
        def handler2(e): raise ValueError("Handler error")
        def handler3(e): return Envelope.success({"handler": 3})

        strategy = BroadcastStrategy()
        results = strategy.route(Envelope(path="/test"), [handler1, handler2, handler3])

        assert len(results) == 3
        assert results[0].status_code == 200
        assert results[1].status_code == 500
        assert "Handler error" in results[1].error_message
        assert results[2].status_code == 200


class TestRoundRobinStrategy:
    """Test RoundRobinStrategy routing."""

    def test_round_robin_order(self):
        """Test round-robin cycling through handlers."""
        def handler1(e): return Envelope.success({"handler": 1})
        def handler2(e): return Envelope.success({"handler": 2})
        def handler3(e): return Envelope.success({"handler": 3})

        strategy = RoundRobinStrategy()
        handlers = [handler1, handler2, handler3]

        result = strategy.route(Envelope(path="/test"), handlers)
        assert result[0].data["handler"] == 1

        result = strategy.route(Envelope(path="/test"), handlers)
        assert result[0].data["handler"] == 2

        result = strategy.route(Envelope(path="/test"), handlers)
        assert result[0].data["handler"] == 3

        result = strategy.route(Envelope(path="/test"), handlers)
        assert result[0].data["handler"] == 1


class TestPortRegistry:
    """Test PortRegistry."""

    def setup_method(self):
        """Reset registry before each test."""
        reset_port_registry()

    def test_register_handler_creates_port(self):
        """Test that registering handler creates port."""
        registry = PortRegistry()

        def handler(e): return e
        registry.register_handler("test", handler)

        assert registry.has_port("test")
        assert "test" in registry.list_ports()

    def test_register_multiple_handlers_on_port(self):
        """Test registering multiple handlers on same port."""
        registry = PortRegistry()

        def handler1(e): return e
        def handler2(e): return e

        registry.register_handler("test", handler1)
        registry.register_handler("test", handler2)

        port_obj = registry.get_port("test")
        assert len(port_obj.handlers) == 2

    def test_route_through_registry(self):
        """Test routing envelope through registry."""
        registry = PortRegistry()

        def handler(e): return Envelope.success({"result": "ok"})
        registry.register_handler("test", handler)

        results = registry.route("test", Envelope(path="/test"))

        assert len(results) == 1
        assert results[0].data["result"] == "ok"

    def test_route_nonexistent_port_raises(self):
        """Test routing to nonexistent port raises error."""
        registry = PortRegistry()

        with pytest.raises(PortNotFoundError) as exc_info:
            registry.route("nonexistent", Envelope(path="/test"))

        assert "nonexistent" in str(exc_info.value)


class TestPortDecorator:
    """Test @port decorator."""

    def setup_method(self):
        """Reset registry before each test."""
        reset_port_registry()

    def test_decorator_registers_handler(self):
        """Test that @port decorator registers handler."""
        from hexswitch.ports.registry import get_port_registry

        @port(name="test_decorator")
        def test_handler(e):
            return Envelope.success({"test": True})

        registry = get_port_registry()
        assert registry.has_port("test_decorator")

    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function name and docstring."""
        @port(name="test")
        def my_handler(e):
            """My docstring."""
            return e

        assert my_handler.__name__ == "my_handler"
        assert my_handler.__doc__ == "My docstring."

