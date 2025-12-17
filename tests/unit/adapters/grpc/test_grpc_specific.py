"""gRPC adapter specific tests."""

import sys
import time
from types import ModuleType

import pytest

from hexswitch.adapters.exceptions import AdapterStartError
from hexswitch.adapters.grpc import GrpcAdapterServer
from tests.unit.adapters.base.adapter_tester import AdapterTester
from tests.unit.adapters.base.security_test_base import SecurityTestBase


@pytest.mark.fast
def test_grpc_adapter_default_config() -> None:
    """Test gRPC adapter with default configuration."""
    config = {"enabled": True, "services": []}
    adapter = GrpcAdapterServer("grpc", config)
    assert adapter.port == 50051
    assert adapter.proto_path == ""


@pytest.mark.fast
def test_grpc_adapter_with_services(handler_module: ModuleType) -> None:
    """Test gRPC adapter with service configuration."""
    config = {
        "enabled": True,
        "port": 0,
        "services": [
            {
                "service_name": "TestService",
                "methods": [
                    {
                        "method_name": "TestMethod",
                        "handler": "test_handler_module:test_handler",
                    }
                ],
            }
        ],
    }

    free_port = AdapterTester.find_free_port()
    config["port"] = free_port
    adapter = GrpcAdapterServer("grpc", config)

    try:
        adapter.start()
        time.sleep(0.2)
        assert adapter.is_running() is True
    finally:
        adapter.stop()


@pytest.mark.fast
def test_grpc_adapter_invalid_handler() -> None:
    """Test gRPC adapter with invalid handler."""
    config = {
        "enabled": True,
        "port": 0,
        "services": [
            {
                "service_name": "TestService",
                "methods": [
                    {
                        "method_name": "TestMethod",
                        "handler": "nonexistent.module:handler",
                    }
                ],
            }
        ],
    }

    free_port = AdapterTester.find_free_port()
    config["port"] = free_port
    adapter = GrpcAdapterServer("grpc", config)

    with pytest.raises(AdapterStartError):
        adapter.start()


@pytest.mark.security
class TestGrpcAdapterSecurity(SecurityTestBase):
    """Test gRPC adapter security features."""

    def test_service_name_injection(self) -> None:
        """Test protection against service name injection."""
        config = {
            "enabled": True,
            "port": 0,
            "services": [
                {
                    "service_name": "../../../etc/passwd",
                    "methods": [
                        {
                            "method_name": "TestMethod",
                            "handler": "nonexistent:handler",
                        }
                    ],
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = GrpcAdapterServer("grpc", config)

        # Should fail to start with invalid service name
        with pytest.raises(AdapterStartError):
            adapter.start()

    def test_method_name_injection(self) -> None:
        """Test protection against method name injection."""
        def handler(request: dict) -> dict:
            return {"result": "success"}

        test_module = ModuleType("test_grpc_handler")
        test_module.handler = handler
        sys.modules["test_grpc_handler"] = test_module

        config = {
            "enabled": True,
            "port": 0,
            "services": [
                {
                    "service_name": "TestService",
                    "methods": [
                        {
                            "method_name": "; rm -rf /",
                            "handler": "test_grpc_handler:handler",
                        }
                    ],
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = GrpcAdapterServer("grpc", config)

        try:
            # Should start (method name is just a string)
            adapter.start()
            time.sleep(0.2)
            assert adapter.is_running() is True
        finally:
            adapter.stop()
            if "test_grpc_handler" in sys.modules:
                del sys.modules["test_grpc_handler"]


@pytest.mark.edge_cases
class TestGrpcAdapterEdgeCases:
    """Test gRPC adapter edge cases."""

    def test_empty_services_config(self) -> None:
        """Test adapter with empty services configuration."""
        config = {
            "enabled": True,
            "port": 0,
            "services": [],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = GrpcAdapterServer("grpc", config)

        try:
            adapter.start()
            time.sleep(0.2)
            assert adapter.is_running() is True
        finally:
            adapter.stop()

    def test_invalid_proto_path(self) -> None:
        """Test adapter with invalid proto path."""
        config = {
            "enabled": True,
            "port": 0,
            "proto_path": "/nonexistent/path",
            "services": [],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = GrpcAdapterServer("grpc", config)

        # Should fail to start with invalid proto path
        with pytest.raises(AdapterStartError):
            adapter.start()

