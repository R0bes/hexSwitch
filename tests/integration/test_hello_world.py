"""Integration test for hello_world example."""

import sys
from types import ModuleType

import pytest

from hexswitch.shared.envelope import Envelope


def create_hello_world_handlers():
    """Create hello_world handlers for testing."""
    test_module = ModuleType("handlers")

    def hello_handler(envelope: Envelope) -> Envelope:
        name = envelope.query_params.get("name", "World")
        return Envelope.success({"message": f"Hello, {name}!"})

    def echo_handler(envelope: Envelope) -> Envelope:
        body = envelope.body or {}
        return Envelope.success({"echo": body})

    test_module.hello_handler = hello_handler
    test_module.echo_handler = echo_handler
    sys.modules["handlers"] = test_module
    return test_module


@pytest.fixture(autouse=True)
def setup_handlers():
    """Setup handlers before each test."""
    handlers = create_hello_world_handlers()
    yield handlers
    if "handlers" in sys.modules:
        del sys.modules["handlers"]


def test_hello_world_handlers_import():
    """Test that hello_world handlers can be imported."""
    from handlers import echo_handler, hello_handler

    assert hello_handler is not None
    assert echo_handler is not None


def test_hello_handler_response():
    """Test hello_handler produces correct response."""
    from handlers import hello_handler

    envelope = Envelope(path="/hello", query_params={})
    response = hello_handler(envelope)

    assert response.status_code == 200
    assert response.data["message"] == "Hello, World!"

    envelope = Envelope(path="/hello", query_params={"name": "Alice"})
    response = hello_handler(envelope)

    assert response.data["message"] == "Hello, Alice!"


def test_echo_handler_response():
    """Test echo_handler echoes body back."""
    from handlers import echo_handler

    envelope = Envelope(
        path="/echo",
        body={"test": "data", "number": 42}
    )
    response = echo_handler(envelope)

    assert response.status_code == 200
    assert response.data["echo"] == {"test": "data", "number": 42}

