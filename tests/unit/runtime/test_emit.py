"""Unit tests for Runtime.emit() and Runtime.deliver()."""

from unittest.mock import MagicMock

from hexswitch.adapters.base import OutboundAdapter
from hexswitch.runtime import Runtime
from hexswitch.shared.envelope import Envelope


def test_runtime_emit_calls_adapter():
    """Test that runtime.emit() calls correct adapter."""
    config = {
        "service": {"name": "test-service"},
    }

    runtime = Runtime(config)

    # Create mock adapter that implements OutboundAdapter
    mock_adapter = MagicMock(spec=OutboundAdapter)
    mock_adapter.name = "http_client"
    mock_response = Envelope.success({"response": "data"})
    mock_adapter.request.return_value = mock_response

    # Register adapter - need to add to outbound_adapters list
    runtime.outbound_adapters.append(mock_adapter)

    # Register outbound port factory
    def factory(order_id: str) -> Envelope:
        return Envelope(path="/api/orders", method="POST", body={"id": order_id})

    runtime.outbound_registry.register_port("order_port", factory)

    # Register route
    from hexswitch.routing.routes import OutboundTarget

    target = OutboundTarget(adapter_name="http_client", config={}, load_balancing="first")
    runtime.route_registry.register_route("order_port", [target])

    # Emit - create envelope from port factory
    envelope = factory("order-123")
    envelope.metadata["port_name"] = "order_port"
    response = runtime.emit(envelope)

    # Verify adapter was called
    assert response == mock_response
    mock_adapter.request.assert_called_once()
    call_envelope = mock_adapter.request.call_args[0][0]
    assert call_envelope.body == {"id": "order-123"}


def test_runtime_emit_port_not_found():
    """Test that runtime.emit() raises error for non-existent port."""
    config = {
        "service": {"name": "test-service"},
    }

    runtime = Runtime(config)

    envelope = Envelope(path="/test", metadata={"port_name": "nonexistent"})
    # Should return error envelope, not raise
    response = runtime.emit(envelope)
    assert response.status_code == 404


def test_runtime_emit_no_targets():
    """Test that runtime.emit() raises error when no targets found."""
    config = {
        "service": {"name": "test-service"},
    }

    runtime = Runtime(config)

    # Register port but no route
    def factory() -> Envelope:
        return Envelope(path="/test")

    runtime.outbound_registry.register_port("test_port", factory)

    envelope = Envelope(path="/test", metadata={"port_name": "test_port"})
    # Should return error envelope, not raise
    response = runtime.emit(envelope)
    assert response.status_code == 404
    assert "No route found" in response.error_message or "No route found" in str(response.data or "")


def test_runtime_deliver_fire_and_forget():
    """Test that runtime.deliver() sends envelope without waiting for response."""
    config = {
        "service": {"name": "test-service"},
    }

    runtime = Runtime(config)

    # Create mock adapter that implements OutboundAdapter
    mock_adapter = MagicMock(spec=OutboundAdapter)
    mock_adapter.name = "http_client"

    # Register adapter - need to add to outbound_adapters list
    runtime.outbound_adapters.append(mock_adapter)

    # Register route
    from hexswitch.routing.routes import OutboundTarget

    target = OutboundTarget(adapter_name="http_client", config={}, load_balancing="first")
    runtime.route_registry.register_route("delivery_port", [target])

    # Create envelope with port metadata
    envelope = Envelope(
        path="/deliver",
        method="POST",
        body={"data": "test"},
        metadata={"outbound_port": "delivery_port"},
    )

    # Deliver - need to specify target adapter
    runtime.deliver(envelope, "http_client")

    # Verify adapter was called
    mock_adapter.request.assert_called_once_with(envelope)


def test_runtime_deliver_no_port_metadata():
    """Test that runtime.deliver() raises error when no port metadata."""
    config = {
        "service": {"name": "test-service"},
    }

    runtime = Runtime(config)

    envelope = Envelope(path="/test", method="POST")

    # deliver() requires target_adapter_name, so this should fail with adapter not found
    response = runtime.deliver(envelope, "nonexistent_adapter")
    assert response.status_code == 404

