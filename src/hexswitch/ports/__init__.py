"""Ports system for hexagonal architecture.

Ports are named connection points between adapters and handlers.
This package provides the port registry, routing strategies, and decorators.
"""

from hexswitch.ports.port import Port
from hexswitch.ports.registry import PortRegistry, get_port_registry, reset_port_registry
from hexswitch.ports.strategies import (
    RoutingStrategy,
    FirstStrategy,
    BroadcastStrategy,
    RoundRobinStrategy,
)
from hexswitch.ports.decorators import port
from hexswitch.ports.exceptions import PortError, PortNotFoundError, NoHandlersError

__all__ = [
    # Core
    "Port",
    "PortRegistry",
    "get_port_registry",
    "reset_port_registry",
    
    # Strategies
    "RoutingStrategy",
    "FirstStrategy",
    "BroadcastStrategy",
    "RoundRobinStrategy",
    
    # Decorators
    "port",
    
    # Exceptions
    "PortError",
    "PortNotFoundError",
    "NoHandlersError",
]
