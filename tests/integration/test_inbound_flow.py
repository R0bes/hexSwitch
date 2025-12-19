"""Integration tests for inbound flow: HTTP Inbound → Handler → HTTP Response."""

import json
import socket
import time
from urllib.request import Request, urlopen

import pytest

from hexswitch.runtime import Runtime
from hexswitch.shared.config import validate_config
from hexswitch.shared.envelope import Envelope

# Timeout for integration tests that start runtime (in seconds)
RUNTIME_TEST_TIMEOUT = 20


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_http_inbound_to_handler_to_response() -> None:
    """Test complete HTTP inbound flow: Request → Handler → Response."""
    import sys
    from types import ModuleType

    # Create test handler module
    test_module = ModuleType("test_inbound_handlers")

    handler_called = False
    received_envelope = None

    def test_handler(envelope: Envelope) -> Envelope:
        nonlocal handler_called, received_envelope
        handler_called = True
        received_envelope = envelope

        # Verify envelope fields are correctly propagated
        # Note: base_path is stripped from path in envelope (base_path is only for routing)
        assert envelope.path == "/test"
        assert envelope.method == "GET"
        assert isinstance(envelope.headers, dict)
        assert isinstance(envelope.query_params, dict)

        # Return response with data
        return Envelope.success(
            {
                "status": "ok",
                "path": envelope.path,
                "method": envelope.method,
                "received": True,
            },
            status_code=200,
        )

    test_module.test = test_handler
    sys.modules["test_inbound_handlers"] = test_module

    # Find free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "inbound-test-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "base_path": "/api",
                "routes": [
                    {
                        "path": "/test",
                        "method": "GET",
                        "handler": "test_inbound_handlers:test",
                    }
                ],
            }
        },
    }

    validate_config(config)
    runtime = Runtime(config)

    try:
        runtime.start()
        # Give server time to start - wait a bit longer for thread to initialize
        time.sleep(1.0)

        # Send HTTP request
        url = f"http://localhost:{free_port}/api/test?param1=value1"
        req = Request(url)
        req.add_header("X-Test-Header", "test-value")

        with urlopen(req, timeout=10) as response:
            # Verify response
            assert response.getcode() == 200
            data = json.loads(response.read().decode())
            assert data["status"] == "ok"
            # Note: base_path is stripped from path in envelope
            assert data["path"] == "/test"
            assert data["method"] == "GET"
            assert data["received"] is True

        # Verify handler was called
        assert handler_called is True
        assert received_envelope is not None
        # Note: base_path is stripped from path in envelope
        assert received_envelope.path == "/test"
        assert received_envelope.method == "GET"

    finally:
        runtime.stop()
        if "test_inbound_handlers" in sys.modules:
            del sys.modules["test_inbound_handlers"]


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_http_inbound_post_with_body() -> None:
    """Test HTTP inbound flow with POST request and body."""
    import sys
    from types import ModuleType

    # Create test handler module
    test_module = ModuleType("test_post_handlers")

    def post_handler(envelope: Envelope) -> Envelope:
        # Verify body is correctly propagated
        assert envelope.method == "POST"
        assert envelope.body is not None
        assert isinstance(envelope.body, dict)

        # Return response with body data
        return Envelope.success(
            {
                "status": "ok",
                "received_body": envelope.body,
            },
            status_code=201,
        )

    test_module.post = post_handler
    sys.modules["test_post_handlers"] = test_module

    # Find free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "post-test-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "base_path": "/api",
                "routes": [
                    {
                        "path": "/data",
                        "method": "POST",
                        "handler": "test_post_handlers:post",
                    }
                ],
            }
        },
    }

    validate_config(config)
    runtime = Runtime(config)

    try:
        runtime.start()
        time.sleep(0.5)

        # Send POST request with body
        url = f"http://localhost:{free_port}/api/data"
        request_body = {"test": "data", "number": 42}
        req = Request(url, data=json.dumps(request_body).encode(), method="POST")
        req.add_header("Content-Type", "application/json")

        with urlopen(req, timeout=10) as response:
            assert response.getcode() == 201
            data = json.loads(response.read().decode())
            assert data["status"] == "ok"
            assert data["received_body"] == request_body

    finally:
        runtime.stop()
        if "test_post_handlers" in sys.modules:
            del sys.modules["test_post_handlers"]


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_http_inbound_error_response() -> None:
    """Test HTTP inbound flow with error response."""
    import sys
    from types import ModuleType

    # Create test handler module
    test_module = ModuleType("test_error_handlers")

    def error_handler(envelope: Envelope) -> Envelope:
        # Return error envelope
        return Envelope.error(status_code=400, error="Bad Request: Invalid input")

    test_module.error = error_handler
    sys.modules["test_error_handlers"] = test_module

    # Find free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "error-test-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "base_path": "/api",
                "routes": [
                    {
                        "path": "/error",
                        "method": "GET",
                        "handler": "test_error_handlers:error",
                    }
                ],
            }
        },
    }

    validate_config(config)
    runtime = Runtime(config)

    try:
        runtime.start()
        time.sleep(0.5)

        # Send request that will return error
        url = f"http://localhost:{free_port}/api/error"
        req = Request(url)

        with pytest.raises(Exception):  # urlopen raises HTTPError for 4xx/5xx
            urlopen(req, timeout=10)

    finally:
        runtime.stop()
        if "test_error_handlers" in sys.modules:
            del sys.modules["test_error_handlers"]

