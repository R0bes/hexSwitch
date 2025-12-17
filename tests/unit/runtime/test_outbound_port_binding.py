"""Tests for outbound port binding in Runtime."""


from hexswitch.ports import get_port_registry, reset_port_registry
from hexswitch.runtime import Runtime


class TestRuntimeOutboundPortBinding:
    """Test that Runtime binds outbound adapters to ports."""

    def setup_method(self):
        """Reset registry before each test."""
        reset_port_registry()

    def test_runtime_binds_outbound_adapter_to_port(self) -> None:
        """Test that Runtime binds outbound adapter to configured port."""
        config = {
            "service": {"name": "test_service"},
            "inbound": {},
            "outbound": {
                "http_client": {
                    "enabled": True,
                    "base_url": "https://api.example.com",
                    "ports": ["external_api"],
                }
            },
        }

        runtime = Runtime(config)

        try:
            runtime.start()

            # Verify port is registered
            registry = get_port_registry()
            assert registry.has_port("external_api")

            # Verify port has handler
            port = registry.get_port("external_api")
            assert len(port.handlers) == 1

        finally:
            runtime.stop()

    def test_runtime_binds_multiple_ports_to_adapter(self) -> None:
        """Test that Runtime can bind multiple ports to one adapter."""
        config = {
            "service": {"name": "test_service"},
            "inbound": {},
            "outbound": {
                "http_client": {
                    "enabled": True,
                    "base_url": "https://api.example.com",
                    "ports": ["api_v1", "api_v2"],
                }
            },
        }

        runtime = Runtime(config)

        try:
            runtime.start()

            registry = get_port_registry()
            assert registry.has_port("api_v1")
            assert registry.has_port("api_v2")

        finally:
            runtime.stop()

    def test_runtime_binds_single_port_string(self) -> None:
        """Test that Runtime can bind single port as string."""
        config = {
            "service": {"name": "test_service"},
            "inbound": {},
            "outbound": {
                "http_client": {
                    "enabled": True,
                    "base_url": "https://api.example.com",
                    "ports": "single_port",  # String instead of list
                }
            },
        }

        runtime = Runtime(config)

        try:
            runtime.start()

            registry = get_port_registry()
            assert registry.has_port("single_port")

        finally:
            runtime.stop()

    def test_runtime_handles_missing_ports_config(self) -> None:
        """Test that Runtime handles missing ports config gracefully."""
        config = {
            "service": {"name": "test_service"},
            "inbound": {},
            "outbound": {
                "http_client": {
                    "enabled": True,
                    "base_url": "https://api.example.com",
                    # No "ports" key
                }
            },
        }

        runtime = Runtime(config)

        try:
            # Should not raise error
            runtime.start()

            # Adapter should still be started
            assert len(runtime.outbound_adapters) == 1

        finally:
            runtime.stop()

