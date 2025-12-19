"""Unit tests for OutboundRouteRegistry."""

import pytest

from hexswitch.routing.routes import OutboundRouteRegistry, OutboundTarget
from hexswitch.shared.envelope import Envelope


def test_outbound_route_registry_select_target():
    """Test outbound route registry target selection."""
    registry = OutboundRouteRegistry()

    # Create targets
    target1 = OutboundTarget(adapter_name="adapter1", config={}, load_balancing="first")
    target2 = OutboundTarget(adapter_name="adapter2", config={}, load_balancing="first")
    target3 = OutboundTarget(adapter_name="adapter3", config={}, load_balancing="round_robin")

    # Register route
    registry.register_route("test_port", [target1, target2])

    # Select target with "first" strategy
    envelope = Envelope(path="/test")
    selected = registry.select_target("test_port", envelope)

    assert selected == target1  # First target should be selected

    # Register route with round_robin - need to set load_balancing on targets
    target1_round = OutboundTarget(adapter_name="adapter1", config={}, load_balancing="round_robin")
    target2_round = OutboundTarget(adapter_name="adapter2", config={}, load_balancing="round_robin")
    registry.register_route("round_robin_port", [target1_round, target2_round])

    # Select multiple times (round-robin)
    selected1 = registry.select_target("round_robin_port", envelope)
    selected2 = registry.select_target("round_robin_port", envelope)
    selected3 = registry.select_target("round_robin_port", envelope)

    # Should cycle through targets
    assert selected1 == target1_round
    assert selected2 == target2_round
    assert selected3 == target1_round  # Back to first


def test_outbound_route_registry_match_route():
    """Test outbound route registry route matching."""
    registry = OutboundRouteRegistry()

    target = OutboundTarget(adapter_name="adapter1", config={}, load_balancing="first")
    registry.register_route("test_port", [target])

    # Match route
    targets = registry.match_route("test_port")

    assert targets is not None
    assert len(targets) == 1
    assert targets[0] == target

    # Non-existent route
    targets = registry.match_route("nonexistent")
    assert targets is None


def test_outbound_route_registry_list_routes():
    """Test listing all routes."""
    registry = OutboundRouteRegistry()

    target1 = OutboundTarget(adapter_name="adapter1", config={})
    target2 = OutboundTarget(adapter_name="adapter2", config={})

    registry.register_route("port1", [target1])
    registry.register_route("port2", [target2])

    routes = registry.list_routes()

    assert len(routes) == 2
    assert "port1" in routes
    assert "port2" in routes


def test_outbound_route_registry_remove_route():
    """Test removing route from registry."""
    registry = OutboundRouteRegistry()

    target = OutboundTarget(adapter_name="adapter1", config={})
    registry.register_route("test_port", [target])

    # Verify route exists
    assert registry.match_route("test_port") is not None

    # Remove route
    registry.remove_route("test_port")

    # Verify route is removed
    assert registry.match_route("test_port") is None


def test_outbound_route_registry_clear():
    """Test clearing all routes."""
    registry = OutboundRouteRegistry()

    target1 = OutboundTarget(adapter_name="adapter1", config={})
    target2 = OutboundTarget(adapter_name="adapter2", config={})

    registry.register_route("port1", [target1])
    registry.register_route("port2", [target2])

    # Clear registry
    registry.clear()

    # Verify all routes are removed
    assert len(registry.list_routes()) == 0


def test_outbound_route_registry_no_targets():
    """Test that select_target raises error when no targets."""
    registry = OutboundRouteRegistry()

    envelope = Envelope(path="/test")

    with pytest.raises(ValueError, match="No targets found for port 'nonexistent'"):
        registry.select_target("nonexistent", envelope)


def test_outbound_target_invalid_load_balancing():
    """Test that OutboundTarget validates load balancing strategy."""
    with pytest.raises(ValueError, match="Invalid load balancing strategy"):
        OutboundTarget(adapter_name="adapter1", config={}, load_balancing="invalid")


def test_outbound_target_valid_strategies():
    """Test that all valid load balancing strategies work."""
    target1 = OutboundTarget(adapter_name="adapter1", config={}, load_balancing="first")
    target2 = OutboundTarget(adapter_name="adapter2", config={}, load_balancing="round_robin")
    target3 = OutboundTarget(adapter_name="adapter3", config={}, load_balancing="failover")

    assert target1.load_balancing == "first"
    assert target2.load_balancing == "round_robin"
    assert target3.load_balancing == "failover"

