"""Pro-level integration tests for multi-adapter scenarios."""

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
def test_runtime_with_http_inbound_and_http_client_outbound() -> None:
    """Test runtime with HTTP inbound and HTTP client outbound adapters."""
    import sys
    from types import ModuleType

    # Create test handler that uses HTTP client
    test_module = ModuleType("test_handlers")

    def proxy_handler(envelope: Envelope) -> Envelope:
        # This handler would use the HTTP client adapter
        # For test purposes, we'll just return a response
        return Envelope.success({"proxied": True, "method": envelope.method})

    test_module.proxy = proxy_handler
    sys.modules["test_handlers"] = test_module

    # Find free ports
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        inbound_port = s.getsockname()[1]

    config = {
        "service": {"name": "proxy-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": inbound_port,
                "base_path": "/api",
                "routes": [
                    {
                        "path": "/proxy",
                        "method": "GET",
                        "handler": "test_handlers:proxy",
                    }
                ],
            }
        },
        "outbound": {
            "http_client": {
                "enabled": True,
                "base_url": "https://api.example.com",
                "timeout": 30,
            }
        },
    }

    validate_config(config)
    runtime = Runtime(config)

    try:
        runtime.start()
        time.sleep(0.5)

        # Verify both adapters are running
        assert len(runtime.inbound_adapters) == 1
        assert len(runtime.outbound_adapters) == 1
        assert runtime.inbound_adapters[0].is_running() is True
        assert runtime.outbound_adapters[0].is_connected() is True

        # Test inbound endpoint
        url = f"http://localhost:{inbound_port}/api/proxy"
        req = Request(url)
        with urlopen(req, timeout=10) as response:
            assert response.getcode() == 200
            data = json.loads(response.read().decode())
            assert data["proxied"] is True

    finally:
        runtime.stop()
        if "test_handlers" in sys.modules:
            del sys.modules["test_handlers"]


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_runtime_observability_integration() -> None:
    """Test runtime with observability enabled."""
    import sys
    from types import ModuleType

    test_module = ModuleType("test_handlers")

    def test_handler(request: dict) -> dict:
        return {"status": "ok"}

    test_module.test = test_handler
    sys.modules["test_handlers"] = test_module

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "observable-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "routes": [
                    {
                        "path": "/test",
                        "method": "GET",
                        "handler": "test_handlers:test",
                    }
                ],
            }
        },
    }

    runtime = Runtime(config)

    try:
        runtime.start()
        time.sleep(0.2)

        # Check metrics
        metrics = runtime._metrics.get_all_metrics()
        assert "runtime_adapter_starts_total" in str(metrics)
        assert runtime._active_adapters_gauge.get() > 0

        # Check traces
        spans = runtime._tracer.get_spans()
        assert len(spans) > 0
        assert any(span.name == "runtime.start" for span in spans)

    finally:
        runtime.stop()
        if "test_handlers" in sys.modules:
            del sys.modules["test_handlers"]


def test_runtime_error_recovery() -> None:
    """Test runtime error recovery and observability."""
    config = {
        "service": {"name": "error-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": 0,  # Will be set to free port
                "routes": [],
            }
        },
    }

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config["inbound"]["http"]["port"] = free_port
    runtime = Runtime(config)

    try:
        runtime.start()
        time.sleep(0.1)

        # Simulate adapter error
        initial_error_count = runtime._adapter_error_counter.get()

        # Stop adapter manually to simulate error
        runtime.inbound_adapters[0].stop()

        # Error counter should not have increased (stop is graceful)
        assert runtime._adapter_error_counter.get() == initial_error_count

        # Restart adapter
        runtime.inbound_adapters[0].start()
        assert runtime.inbound_adapters[0].is_running() is True

    finally:
        runtime.stop()

