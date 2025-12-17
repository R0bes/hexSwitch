"""Integration test for hello_world example."""

import pytest
import sys
from pathlib import Path

examples_dir = Path(__file__).parent.parent.parent / "examples"
sys.path.insert(0, str(examples_dir / "hello_world"))


def test_hello_world_handlers_import():
    """Test that hello_world handlers can be imported."""
    from handlers import hello_handler, echo_handler
    
    assert hello_handler is not None
    assert echo_handler is not None


def test_hello_handler_response():
    """Test hello_handler produces correct response."""
    from handlers import hello_handler
    from hexswitch.shared.envelope import Envelope
    
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
    from hexswitch.shared.envelope import Envelope
    
    envelope = Envelope(
        path="/echo",
        body={"test": "data", "number": 42}
    )
    response = echo_handler(envelope)
    
    assert response.status_code == 200
    assert response.data["echo"] == {"test": "data", "number": 42}

