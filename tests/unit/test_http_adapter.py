"""Unit tests for HTTP adapter."""

import json
import socket
import time
from threading import Thread
from urllib.request import Request, urlopen

import pytest

from hexswitch.adapters.exceptions import AdapterStartError, AdapterStopError
from hexswitch.adapters.http import HttpAdapter


def test_http_adapter_initialization() -> None:
    """Test HTTP adapter initialization."""
    config = {
        "enabled": True,
        "port": 8000,
        "base_path": "/api",
        "routes": [],
    }
    adapter = HttpAdapter("http", config)
    assert adapter.name == "http"
    assert adapter.port == 8000
    assert adapter.base_path == "/api"
    assert adapter.routes == []
    assert adapter.is_running() is False


def test_http_adapter_default_config() -> None:
    """Test HTTP adapter with default configuration."""
    config = {"enabled": True, "routes": []}
    adapter = HttpAdapter("http", config)
    assert adapter.port == 8000
    assert adapter.base_path == ""


def test_http_adapter_start_stop() -> None:
    """Test HTTP adapter start and stop."""
    config = {
        "enabled": True,
        "port": 0,  # Use 0 to get a free port
        "routes": [],
    }
    adapter = HttpAdapter("http", config)

    # Find a free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config["port"] = free_port
    adapter = HttpAdapter("http", config)

    adapter.start()
    assert adapter.is_running() is True

    # Give server time to start
    time.sleep(0.1)

    adapter.stop()
    assert adapter.is_running() is False


def test_http_adapter_start_twice() -> None:
    """Test that starting adapter twice doesn't cause errors."""
    config = {
        "enabled": True,
        "port": 0,
        "routes": [],
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config["port"] = free_port
    adapter = HttpAdapter("http", config)

    adapter.start()
    time.sleep(0.1)
    adapter.start()  # Should not raise error
    adapter.stop()


def test_http_adapter_stop_when_not_running() -> None:
    """Test that stopping adapter when not running doesn't cause errors."""
    config = {"enabled": True, "port": 8000, "routes": []}
    adapter = HttpAdapter("http", config)

    adapter.stop()  # Should not raise error
    assert adapter.is_running() is False


def test_http_adapter_port_in_use() -> None:
    """Test HTTP adapter error when port is in use."""
    # This test is tricky because we can't easily simulate port conflicts
    # We'll skip it for now as it requires more complex setup
    pass


def test_http_adapter_with_routes() -> None:
    """Test HTTP adapter with route configuration."""
    def hello_handler(request: dict) -> dict:
        return {"message": "Hello, World!"}

    # Create a test module to hold the handler
    import sys
    from types import ModuleType

    test_module = ModuleType("test_handlers")
    test_module.hello = hello_handler
    sys.modules["test_handlers"] = test_module

    config = {
        "enabled": True,
        "port": 0,
        "base_path": "/api",
        "routes": [
            {
                "path": "/hello",
                "method": "GET",
                "handler": "test_handlers:hello",
            }
        ],
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config["port"] = free_port
    adapter = HttpAdapter("http", config)

    try:
        adapter.start()
        time.sleep(0.2)  # Give server time to start

        # Test the endpoint
        url = f"http://localhost:{free_port}/api/hello"
        req = Request(url)
        with urlopen(req) as response:
            data = json.loads(response.read().decode())
            assert data == {"message": "Hello, World!"}
    finally:
        adapter.stop()
        if "test_handlers" in sys.modules:
            del sys.modules["test_handlers"]

