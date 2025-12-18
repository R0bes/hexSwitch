"""Unit tests for runtime orchestration."""

import pytest

from hexswitch.runtime import Runtime
from hexswitch.shared.config.config import build_execution_plan


def test_build_execution_plan_minimal() -> None:
    """Test building execution plan from minimal config."""
    config = {"service": {"name": "test-service"}}
    plan = build_execution_plan(config)

    assert plan["service"] == "test-service"
    assert plan["inbound_adapters"] == []
    assert plan["outbound_adapters"] == []


def test_build_execution_plan_with_adapters() -> None:
    """Test building execution plan with enabled adapters."""
    config = {
        "service": {"name": "test-service"},
        "inbound": {
            "http": {"enabled": True, "base_path": "/api"},
            "grpc": {"enabled": False},
        },
        "outbound": {
            "postgres": {"enabled": True, "dsn": "postgresql://localhost/db"},
            "redis": {"enabled": False},
        },
    }

    plan = build_execution_plan(config)

    assert plan["service"] == "test-service"
    assert len(plan["inbound_adapters"]) == 1
    assert plan["inbound_adapters"][0]["name"] == "http"
    assert len(plan["outbound_adapters"]) == 1
    assert plan["outbound_adapters"][0]["name"] == "postgres"


def test_build_execution_plan_no_enabled_adapters() -> None:
    """Test building execution plan when no adapters are enabled."""
    config = {
        "service": {"name": "test-service"},
        "inbound": {"http": {"enabled": False}},
        "outbound": {"postgres": {"enabled": False}},
    }

    plan = build_execution_plan(config)

    assert plan["service"] == "test-service"
    assert plan["inbound_adapters"] == []
    assert plan["outbound_adapters"] == []


def test_build_execution_plan_missing_service_name() -> None:
    """Test building execution plan when service name is missing."""
    config = {"service": {}}
    plan = build_execution_plan(config)

    assert plan["service"] == "unknown"


def test_build_execution_plan_verbose_output() -> None:
    """Test that execution plan contains expected information."""
    config = {
        "service": {"name": "test-service"},
        "inbound": {
            "http": {"enabled": True, "base_path": "/api"},
        },
        "outbound": {
            "postgres": {"enabled": True, "dsn": "postgresql://localhost/db"},
        },
    }

    plan = build_execution_plan(config)

    assert plan["service"] == "test-service"
    assert len(plan["inbound_adapters"]) == 1
    assert plan["inbound_adapters"][0]["name"] == "http"
    assert len(plan["outbound_adapters"]) == 1
    assert plan["outbound_adapters"][0]["name"] == "postgres"


@pytest.mark.timeout(10)
def test_runtime_minimal_config() -> None:
    """Test Runtime with minimal configuration."""
    config = {"service": {"name": "test-service"}}
    runtime = Runtime(config)

    try:
        runtime.start()
        # Runtime should start successfully
        assert len(runtime.inbound_adapters) == 0
        assert len(runtime.outbound_adapters) == 0
    finally:
        runtime.stop()


@pytest.mark.timeout(15)
def test_runtime_with_http_adapter() -> None:
    """Test Runtime with HTTP adapter."""
    import socket
    import time

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

    try:
        runtime.start()
        time.sleep(0.1)  # Give adapter time to start
        # Runtime should start successfully with HTTP adapter
        assert len(runtime.inbound_adapters) == 1
        assert runtime.inbound_adapters[0].name == "http"
    finally:
        runtime.stop()

