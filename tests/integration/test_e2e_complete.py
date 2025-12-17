"""Pro-level end-to-end tests for complete scenarios."""

import json
import socket
import time
from urllib.request import Request, urlopen

import pytest

from hexswitch.shared.config import load_config, validate_config
from hexswitch.shared.envelope import Envelope
from hexswitch.runtime import Runtime, run_runtime


# Timeout for E2E tests that start runtime (in seconds)
E2E_TEST_TIMEOUT = 25


@pytest.mark.timeout(E2E_TEST_TIMEOUT)
def test_complete_http_service_with_observability() -> None:
    """Test complete HTTP service with full observability."""
    import sys
    from types import ModuleType

    # Create comprehensive handler
    test_module = ModuleType("e2e_handlers")

    request_count = 0

    def api_handler(envelope: Envelope) -> Envelope:
        nonlocal request_count
        request_count += 1
        return Envelope.success({
            "status": "ok",
            "request_id": request_count,
            "method": envelope.method,
            "path": envelope.path,
        })

    test_module.api = api_handler
    sys.modules["e2e_handlers"] = test_module

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "e2e-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "base_path": "/api/v1",
                "routes": [
                    {
                        "path": "/status",
                        "method": "GET",
                        "handler": "e2e_handlers:api",
                    },
                    {
                        "path": "/data",
                        "method": "POST",
                        "handler": "e2e_handlers:api",
                    },
                ],
            }
        },
        "outbound": {
            "http_client": {
                "enabled": True,
                "base_url": "https://api.external.com",
                "timeout": 30,
            }
        },
        "logging": {"level": "INFO"},
    }

    validate_config(config)
    runtime = Runtime(config)

    try:
        runtime.start()
        time.sleep(0.3)

        # Test multiple endpoints
        base_url = f"http://localhost:{free_port}/api/v1"

        # GET request
        req = Request(f"{base_url}/status")
        with urlopen(req) as response:
            assert response.getcode() == 200
            data = json.loads(response.read().decode())
            assert data["status"] == "ok"
            assert data["method"] == "GET"

        # POST request
        req = Request(f"{base_url}/data", data=json.dumps({"test": "data"}).encode(), method="POST")
        req.add_header("Content-Type", "application/json")
        with urlopen(req) as response:
            assert response.getcode() == 200
            data = json.loads(response.read().decode())
            assert data["status"] == "ok"
            assert data["method"] == "POST"

        # Verify observability
        metrics = runtime._metrics.get_all_metrics()
        assert len(metrics["counters"]) > 0
        assert len(metrics["gauges"]) > 0

        spans = runtime._tracer.get_spans()
        assert len(spans) > 0

        # Verify adapters
        assert len(runtime.inbound_adapters) == 1
        assert len(runtime.outbound_adapters) == 1
        assert runtime.inbound_adapters[0].is_running() is True
        assert runtime.outbound_adapters[0].is_connected() is True

    finally:
        runtime.stop()
        if "e2e_handlers" in sys.modules:
            del sys.modules["e2e_handlers"]


@pytest.mark.timeout(E2E_TEST_TIMEOUT)
def test_runtime_graceful_shutdown_complete() -> None:
    """Test complete graceful shutdown scenario."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "shutdown-test"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "routes": [],
            }
        },
        "outbound": {
            "http_client": {
                "enabled": True,
                "base_url": "https://api.example.com",
            }
        },
    }

    runtime = Runtime(config)

    runtime.start()
    time.sleep(0.1)

    # Verify running
    assert len(runtime.inbound_adapters) == 1
    assert len(runtime.outbound_adapters) == 1

    # Request shutdown
    runtime.request_shutdown()

    # Run should exit quickly
    import threading

    run_thread = threading.Thread(target=runtime.run)
    run_thread.start()
    run_thread.join(timeout=2.0)

    # Verify stopped
    assert len(runtime.inbound_adapters) == 0
    assert len(runtime.outbound_adapters) == 0
    assert runtime._active_adapters_gauge.get() == 0


def test_config_validation_complete() -> None:
    """Test complete configuration validation."""
    # Valid config with all adapters
    config = {
        "service": {"name": "full-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": 8000,
                "base_path": "/api",
                "routes": [
                    {
                        "path": "/test",
                        "method": "GET",
                        "handler": "handlers:test",
                    }
                ],
            }
        },
        "outbound": {
            "http_client": {
                "enabled": True,
                "base_url": "https://api.example.com",
                "timeout": 30,
            },
            "mcp_client": {
                "enabled": False,
                "server_url": "https://mcp.example.com",
            },
        },
    }

    # Should validate successfully
    validate_config(config)

    # Invalid configs
    invalid_configs = [
        # Missing server_url for MCP
        {
            "service": {"name": "test"},
            "outbound": {"mcp_client": {"enabled": True}},
        },
        # Invalid port
        {
            "service": {"name": "test"},
            "inbound": {"http": {"enabled": True, "port": 70000}},
        },
        # Invalid handler format
        {
            "service": {"name": "test"},
            "inbound": {
                "http": {
                    "enabled": True,
                    "routes": [{"path": "/test", "method": "GET", "handler": "invalid"}],
                }
            },
        },
    ]

    for invalid_config in invalid_configs:
        with pytest.raises(Exception):  # ConfigError or ValueError
            validate_config(invalid_config)

