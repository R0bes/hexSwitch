"""Test routing strategies in isolation."""

import pytest
from hexswitch.ports.strategies import (
    FirstStrategy,
    BroadcastStrategy,
    RoundRobinStrategy
)
from hexswitch.shared.envelope import Envelope


def test_first_strategy_single_handler():
    """FirstStrategy with single handler."""
    def handler(e): return Envelope.success({"id": 1})
    
    strategy = FirstStrategy()
    results = strategy.route(Envelope(path="/"), [handler])
    
    assert len(results) == 1
    assert results[0].data["id"] == 1


def test_broadcast_empty_handlers_list():
    """BroadcastStrategy with empty handlers."""
    strategy = BroadcastStrategy()
    results = strategy.route(Envelope(path="/"), [])
    
    assert results == []


def test_broadcast_all_errors():
    """BroadcastStrategy when all handlers fail."""
    def handler1(e): raise RuntimeError("Error 1")
    def handler2(e): raise ValueError("Error 2")
    
    strategy = BroadcastStrategy()
    results = strategy.route(Envelope(path="/"), [handler1, handler2])
    
    assert len(results) == 2
    assert all(r.status_code == 500 for r in results)
    assert "Error 1" in results[0].error_message
    assert "Error 2" in results[1].error_message

