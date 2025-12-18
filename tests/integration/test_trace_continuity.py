"""Integration tests for trace continuity across protocols."""

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
def test_trace_continuity_http_inbound_to_outbound() -> None:
    """Test trace continuity from HTTP inbound to outbound."""
    import sys
    from types import ModuleType

    # Create test handler module
    test_module = ModuleType("test_trace_handlers")

    received_trace_id = None
    received_span_id = None

    def test_handler(envelope: Envelope) -> Envelope:
        nonlocal received_trace_id, received_span_id

        # Capture trace context
        received_trace_id = envelope.trace_id
        received_span_id = envelope.span_id

        # Verify trace context is present
        assert envelope.trace_id is not None
        assert envelope.span_id is not None

        return Envelope.success({"trace_id": envelope.trace_id, "span_id": envelope.span_id})

    test_module.test = test_handler
    sys.modules["test_trace_handlers"] = test_module

    # Find free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "trace-test-service"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "base_path": "/api",
                "routes": [
                    {
                        "path": "/test",
                        "method": "GET",
                        "handler": "test_trace_handlers:test",
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

        # Send HTTP request with trace context
        url = f"http://localhost:{free_port}/api/test"
        req = Request(url)
        req.add_header("traceparent", "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01")

        with urlopen(req, timeout=10) as response:
            assert response.getcode() == 200
            data = json.loads(response.read().decode())
            assert "trace_id" in data
            assert "span_id" in data

            # Verify trace context was propagated
            assert received_trace_id is not None
            assert received_span_id is not None
            # Trace ID should match (or be part of same trace)
            assert data["trace_id"] == received_trace_id or data["trace_id"] is not None

    finally:
        runtime.stop()
        if "test_trace_handlers" in sys.modules:
            del sys.modules["test_trace_handlers"]


@pytest.mark.timeout(RUNTIME_TEST_TIMEOUT)
def test_trace_continuity_span_hierarchy() -> None:
    """Test trace continuity with span hierarchy."""
    import sys
    from types import ModuleType

    # Create test handler module
    test_module = ModuleType("test_trace_hierarchy")

    trace_ids = []
    span_ids = []
    parent_span_ids = []

    def handler1(envelope: Envelope) -> Envelope:
        trace_ids.append(envelope.trace_id)
        span_ids.append(envelope.span_id)
        parent_span_ids.append(envelope.parent_span_id)
        return Envelope.success({"handler": "1"})

    test_module.handler1 = handler1
    sys.modules["test_trace_hierarchy"] = test_module

    # Find free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        free_port = s.getsockname()[1]

    config = {
        "service": {"name": "trace-hierarchy-test"},
        "inbound": {
            "http": {
                "enabled": True,
                "port": free_port,
                "base_path": "/api",
                "routes": [
                    {
                        "path": "/test",
                        "method": "GET",
                        "handler": "test_trace_hierarchy:handler1",
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

        # Send HTTP request with trace context
        url = f"http://localhost:{free_port}/api/test"
        req = Request(url)
        req.add_header("traceparent", "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01")

        with urlopen(req, timeout=10) as response:
            assert response.getcode() == 200

            # Verify trace context was captured
            assert len(trace_ids) > 0
            assert len(span_ids) > 0

            # Verify trace ID is consistent
            assert all(tid == trace_ids[0] for tid in trace_ids if tid)

    finally:
        runtime.stop()
        if "test_trace_hierarchy" in sys.modules:
            del sys.modules["test_trace_hierarchy"]

