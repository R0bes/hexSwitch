"""Unit tests for runtime orchestration."""

import pytest

from hexswitch.runtime import (
    Runtime,
    build_execution_plan,
    print_execution_plan,
    run_runtime,
)


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


def test_print_execution_plan(caplog: pytest.LogCaptureFixture) -> None:
    """Test printing execution plan."""
    import logging

    with caplog.at_level(logging.INFO):
        plan = {
            "service": "test-service",
            "inbound_adapters": [{"name": "http", "config": {"enabled": True}}],
            "outbound_adapters": [{"name": "postgres", "config": {"enabled": True}}],
        }

        print_execution_plan(plan)

        assert "test-service" in caplog.text
        assert "http" in caplog.text
        assert "postgres" in caplog.text
        assert "Ready to start runtime" in caplog.text


def test_run_runtime_minimal_config() -> None:
    """Test run_runtime with minimal configuration."""
    config = {"service": {"name": "test-service"}}
    runtime = Runtime(config)
    runtime.start()
    runtime.request_shutdown()
    runtime.run()  # Should exit immediately due to shutdown request
    runtime.stop()


def test_run_runtime_with_http_adapter() -> None:
    """Test run_runtime with HTTP adapter."""
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
        runtime.request_shutdown()
        runtime.run()  # Should exit due to shutdown request
    finally:
        runtime.stop()


def test_run_runtime_not_implemented() -> None:
    """Test that run_runtime raises NotImplementedError."""
    config = {"service": {"name": "test-service"}}

    with pytest.raises(NotImplementedError, match="Runtime execution is not yet implemented"):
        run_runtime(config)

