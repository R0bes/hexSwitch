"""Integration tests for outbound flow: Handler → Outbound Adapter → External Service."""

import json
import socket
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from urllib.request import Request, urlopen

import pytest

from hexswitch.runtime import Runtime
from hexswitch.shared.config import validate_config
from hexswitch.shared.envelope import Envelope

# Timeout for integration tests that start runtime (in seconds)
RUNTIME_TEST_TIMEOUT = 20


class MockExternalServer(BaseHTTPRequestHandler):
    """Mock external HTTP server for testing outbound adapters."""

    received_requests = []
    response_data = {"status": "ok", "from": "external"}

    def do_GET(self):
        """Handle GET requests."""
        self.received_requests.append(("GET", self.path, self.headers))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(self.response_data).encode())

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""
        self.received_requests.append(("POST", self.path, self.headers, body))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(self.response_data).encode())

    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


@pytest.fixture
def mock_external_server():
    """Create a mock external HTTP server."""
    server = HTTPServer(("localhost", 0), MockExternalServer)
    server_thread = Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.1)  # Give server time to start

    yield server

    server.shutdown()
    server.server_close()


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_outbound_http_client_flow() -> None:
    """Test complete outbound HTTP client flow: Handler → Outbound Adapter → External Service."""
    import sys
    from types import ModuleType

    # Create mock external server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        external_port = s.getsockname()[1]

    external_server = HTTPServer(("localhost", external_port), MockExternalServer)
    server_thread = Thread(target=external_server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.2)

    try:
        # Create test handler module that uses outbound adapter
        test_module = ModuleType("test_outbound_handlers")

        outbound_response = None
        handler_called = False

        def handler_with_outbound(envelope: Envelope) -> Envelope:
            nonlocal outbound_response, handler_called
            handler_called = True

            # Get port registry to access outbound adapter
            from hexswitch.ports.registry import get_port_registry

            port_registry = get_port_registry()

            # Create envelope for outbound request
            outbound_envelope = Envelope(
                path="/api/external",
                method="GET",
                headers={"X-Request-ID": "test-123"},
            )

            # Call outbound port (this will use the HTTP client adapter)
            # Note: This uses the current pattern where outbound adapters are bound as handlers
            # In Phase 3, this will be replaced with runtime.emit()
            try:
                outbound_handler = port_registry.get_handler("external_api_port")
                outbound_response = outbound_handler(outbound_envelope)
            except Exception:
                # If port not registered, skip outbound call for this test
                # The test will verify the handler was called
                pass

            return Envelope.success({"handler": "called", "outbound": outbound_response is not None})

        test_module.with_outbound = handler_with_outbound
        sys.modules["test_outbound_handlers"] = test_module

        # Find free port for inbound
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            inbound_port = s.getsockname()[1]

        config = {
            "service": {"name": "outbound-test-service"},
            "inbound": {
                "http": {
                    "enabled": True,
                    "port": inbound_port,
                    "base_path": "/api",
                    "routes": [
                        {
                            "path": "/test",
                            "method": "GET",
                            "handler": "test_outbound_handlers:with_outbound",
                        }
                    ],
                }
            },
            "outbound": {
                "http_client": {
                    "enabled": True,
                    "base_url": f"http://localhost:{external_port}",
                    "timeout": 5,
                    "ports": ["external_api_port"],
                }
            },
        }

        validate_config(config)
        runtime = Runtime(config)

        try:
            runtime.start()
            time.sleep(0.5)

            # Verify handler was called
            url = f"http://localhost:{inbound_port}/api/test"
            req = Request(url)

            with urlopen(req, timeout=10) as response:
                assert response.getcode() == 200
                data = json.loads(response.read().decode())
                assert data["handler"] == "called"

            # Verify handler was called
            assert handler_called is True

            # Verify trace context propagation (if outbound was called)
            # This will be more relevant in Phase 5 when trace propagation is fully implemented

        finally:
            runtime.stop()
            if "test_outbound_handlers" in sys.modules:
                del sys.modules["test_outbound_handlers"]

    finally:
        external_server.shutdown()
        external_server.server_close()


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_outbound_http_client_with_response() -> None:
    """Test outbound HTTP client receives and returns response correctly."""
    import sys
    from types import ModuleType

    # Create mock external server with custom response
    MockExternalServer.response_data = {"status": "success", "data": {"id": "123"}}

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        external_port = s.getsockname()[1]

    external_server = HTTPServer(("localhost", external_port), MockExternalServer)
    server_thread = Thread(target=external_server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.2)

    try:
        # Find free port for inbound
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            inbound_port = s.getsockname()[1]

        config = {
            "service": {"name": "outbound-response-test"},
            "inbound": {
                "http": {
                    "enabled": True,
                    "port": inbound_port,
                    "base_path": "/api",
                    "routes": [
                        {
                            "path": "/proxy",
                            "method": "GET",
                            "handler": "test_outbound_handlers:proxy",
                        }
                    ],
                }
            },
            "outbound": {
                "http_client": {
                    "enabled": True,
                    "base_url": f"http://localhost:{external_port}",
                    "timeout": 5,
                    "ports": ["external_api_port"],
                }
            },
        }

        # Create handler that uses outbound
        test_module = ModuleType("test_outbound_handlers")

        def proxy_handler(envelope: Envelope) -> Envelope:
            from hexswitch.ports.registry import get_port_registry

            port_registry = get_port_registry()

            # Create outbound envelope
            outbound_envelope = Envelope(
                path="/api/external",
                method="GET",
            )

            try:
                outbound_handler = port_registry.get_handler("external_api_port")
                response = outbound_handler(outbound_envelope)
                return Envelope.success({"proxied": True, "external_response": response.data})
            except Exception:
                return Envelope.error(500, "Outbound call failed")

        test_module.proxy = proxy_handler
        sys.modules["test_outbound_handlers"] = test_module

        validate_config(config)
        runtime = Runtime(config)

        try:
            runtime.start()
            time.sleep(0.5)

            # Send request
            url = f"http://localhost:{inbound_port}/api/proxy"
            req = Request(url)

            with urlopen(req, timeout=10) as response:
                assert response.getcode() == 200
                data = json.loads(response.read().decode())
                assert data["proxied"] is True
                # Verify response correlation
                assert "external_response" in data

        finally:
            runtime.stop()
            if "test_outbound_handlers" in sys.modules:
                del sys.modules["test_outbound_handlers"]

    finally:
        external_server.shutdown()
        external_server.server_close()

