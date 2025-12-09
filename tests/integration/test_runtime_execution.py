"""Integration tests for runtime execution."""

import json
import socket
import time
from urllib.request import Request, urlopen

import pytest

from hexswitch.config import load_config, validate_config
from hexswitch.runtime import Runtime


def create_test_handler_module():
    """Create a test handler module for integration tests."""
    import sys
    from types import ModuleType

    test_module = ModuleType("test_http_handlers")

    def hello_handler(request: dict) -> dict:
        return {"message": "Hello from HexSwitch!", "method": request.get("method")}

    def echo_handler(request: dict) -> dict:
        body = request.get("body")
        if body:
            try:
                data = json.loads(body)
                return {"echo": data}
            except json.JSONDecodeError:
                return {"echo": body}
        return {"echo": "no body"}

    test_module.hello = hello_handler
    test_module.echo = echo_handler
    sys.modules["test_http_handlers"] = test_module
    return test_module


def test_runtime_with_http_adapter_end_to_end() -> None:
    """Test complete runtime execution with HTTP adapter."""
    # Create test handler module
    test_module = create_test_handler_module()

    # Find a free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "test-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "base_path": "/api",
                "routes": [
                    {
                        "path": "/hello",
                        "method": "GET",
                        "handler": "test_http_handlers:hello",
                    },
                    {
                        "path": "/echo",
                        "method": "POST",
                        "handler": "test_http_handlers:echo",
                    },
                ],
            }
        },
    }

    # Validate config
    validate_config(config)

    # Create and start runtime
    runtime = Runtime(config)

    try:
        runtime.start()
        time.sleep(0.3)  # Give server time to start

        # Test GET /api/hello
        url = f"http://localhost:{free_port}/api/hello"
        req = Request(url)
        with urlopen(req) as response:
            assert response.getcode() == 200
            data = json.loads(response.read().decode())
            assert data["message"] == "Hello from HexSwitch!"
            assert data["method"] == "GET"

        # Test POST /api/echo
        url = f"http://localhost:{free_port}/api/echo"
        req = Request(url, data=json.dumps({"test": "data"}).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        with urlopen(req) as response:
            assert response.getcode() == 200
            data = json.loads(response.read().decode())
            assert data["echo"] == {"test": "data"}

        # Test 404 for unknown route
        url = f"http://localhost:{free_port}/api/unknown"
        req = Request(url)
        with pytest.raises(Exception):  # urlopen raises HTTPError for 404
            urlopen(req)

    finally:
        runtime.stop()
        # Clean up test module
        import sys

        if "test_http_handlers" in sys.modules:
            del sys.modules["test_http_handlers"]


def test_runtime_graceful_shutdown() -> None:
    """Test that runtime shuts down gracefully."""
    # Find a free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "test-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "routes": [],
            }
        },
    }

    runtime = Runtime(config)

    runtime.start()
    time.sleep(0.1)
    assert runtime.inbound_adapters[0].is_running() is True

    runtime.request_shutdown()
    runtime.run()  # Should exit quickly due to shutdown request

    # Adapters should be stopped
    assert len(runtime.inbound_adapters) == 0


def test_runtime_with_config_file() -> None:
    """Test runtime with configuration loaded from file structure."""
    # This test validates that the config structure matches what would come from a file
    config_dict = {
        "service": {"name": "example-service", "runtime": "python"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": 0,  # Will be set to free port
                "base_path": "/api",
                "routes": [
                    {
                        "path": "/hello",
                        "method": "GET",
                        "handler": "test_http_handlers:hello",
                    }
                ],
            }
        },
        "logging": {"level": "INFO"},
    }

    # Find a free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config_dict["inbound"]["http"]["port"] = free_port

    # Validate config
    validate_config(config_dict)

    # Create test handler
    test_module = create_test_handler_module()

    # Create and start runtime
    runtime = Runtime(config_dict)

    try:
        runtime.start()
        time.sleep(0.2)

        # Verify adapter is running
        assert len(runtime.inbound_adapters) == 1
        assert runtime.inbound_adapters[0].name == "http"
        assert runtime.inbound_adapters[0].is_running() is True

        # Test endpoint
        url = f"http://localhost:{free_port}/api/hello"
        req = Request(url)
        with urlopen(req) as response:
            assert response.getcode() == 200

    finally:
        runtime.stop()
        import sys

        if "test_http_handlers" in sys.modules:
            del sys.modules["test_http_handlers"]

