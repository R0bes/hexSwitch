"""Unit tests for AdapterRegistry."""

import threading
import time

from hexswitch.adapters.base import InboundAdapter, OutboundAdapter
from hexswitch.registry.adapters import ADAPTER_METADATA, AdapterRegistry


class MockInboundAdapter(InboundAdapter):
    """Mock inbound adapter for testing."""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def is_running(self) -> bool:
        return True


class MockOutboundAdapter(OutboundAdapter):
    """Mock outbound adapter for testing."""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def is_connected(self) -> bool:
        return True

    def request(self, envelope):
        return envelope


def test_adapter_registry_stores_and_retrieves():
    """Test registry storage and retrieval."""
    registry = AdapterRegistry()

    # Create mock adapters
    inbound_adapter = MockInboundAdapter("http", {"port": 8000})
    outbound_adapter = MockOutboundAdapter("http_client", {"base_url": "https://api.example.com"})

    # Register adapters
    metadata_inbound = {"direction": "inbound", "protocol": "http"}
    metadata_outbound = {"direction": "outbound", "protocol": "http"}

    registry.register("http", inbound_adapter, metadata_inbound)
    registry.register("http_client", outbound_adapter, metadata_outbound)

    # Retrieve adapters
    retrieved_inbound = registry.get("http")
    retrieved_outbound = registry.get("http_client")

    assert retrieved_inbound is inbound_adapter
    assert retrieved_outbound is outbound_adapter

    # Retrieve metadata
    retrieved_metadata_inbound = registry.get_metadata("http")
    retrieved_metadata_outbound = registry.get_metadata("http_client")

    assert retrieved_metadata_inbound == metadata_inbound
    assert retrieved_metadata_outbound == metadata_outbound


def test_adapter_registry_list_inbound():
    """Test listing inbound adapters."""
    registry = AdapterRegistry()

    # Register adapters
    inbound_adapter = MockInboundAdapter("http", {})
    outbound_adapter = MockOutboundAdapter("http_client", {})

    registry.register("http", inbound_adapter, {"direction": "inbound", "protocol": "http"})
    registry.register("http_client", outbound_adapter, {"direction": "outbound", "protocol": "http"})
    registry.register("grpc", MockInboundAdapter("grpc", {}), {"direction": "both", "protocol": "grpc"})

    # List inbound adapters
    inbound_list = registry.list_inbound()

    assert "http" in inbound_list
    assert "grpc" in inbound_list  # "both" includes inbound
    assert "http_client" not in inbound_list


def test_adapter_registry_list_outbound():
    """Test listing outbound adapters."""
    registry = AdapterRegistry()

    # Register adapters
    inbound_adapter = MockInboundAdapter("http", {})
    outbound_adapter = MockOutboundAdapter("http_client", {})

    registry.register("http", inbound_adapter, {"direction": "inbound", "protocol": "http"})
    registry.register("http_client", outbound_adapter, {"direction": "outbound", "protocol": "http"})
    registry.register("grpc", MockOutboundAdapter("grpc_client", {}), {"direction": "both", "protocol": "grpc"})

    # List outbound adapters
    outbound_list = registry.list_outbound()

    assert "http_client" in outbound_list
    assert "grpc" in outbound_list  # "both" includes outbound
    assert "http" not in outbound_list


def test_adapter_registry_list_all():
    """Test listing all adapters."""
    registry = AdapterRegistry()

    # Register multiple adapters
    registry.register("http", MockInboundAdapter("http", {}), {"direction": "inbound"})
    registry.register("http_client", MockOutboundAdapter("http_client", {}), {"direction": "outbound"})
    registry.register("grpc", MockInboundAdapter("grpc", {}), {"direction": "both"})

    # List all adapters
    all_adapters = registry.list_all()

    assert len(all_adapters) == 3
    assert "http" in all_adapters
    assert "http_client" in all_adapters
    assert "grpc" in all_adapters


def test_adapter_registry_remove():
    """Test removing adapters from registry."""
    registry = AdapterRegistry()

    # Register adapter
    adapter = MockInboundAdapter("http", {})
    registry.register("http", adapter, {"direction": "inbound"})

    # Verify it's registered
    assert registry.get("http") is adapter

    # Remove adapter
    registry.remove("http")

    # Verify it's removed
    assert registry.get("http") is None
    assert registry.get_metadata("http") is None


def test_adapter_registry_clear():
    """Test clearing all adapters from registry."""
    registry = AdapterRegistry()

    # Register multiple adapters
    registry.register("http", MockInboundAdapter("http", {}), {"direction": "inbound"})
    registry.register("http_client", MockOutboundAdapter("http_client", {}), {"direction": "outbound"})

    # Clear registry
    registry.clear()

    # Verify all adapters are removed
    assert len(registry.list_all()) == 0
    assert registry.get("http") is None
    assert registry.get("http_client") is None


def test_adapter_registry_thread_safety():
    """Test that registry is thread-safe."""
    registry = AdapterRegistry()
    results = []

    def register_adapters():
        for i in range(10):
            adapter = MockInboundAdapter(f"adapter_{i}", {})
            registry.register(f"adapter_{i}", adapter, {"direction": "inbound", "index": i})
            time.sleep(0.001)  # Small delay to increase chance of race conditions

    def read_adapters():
        for i in range(10):
            adapter = registry.get(f"adapter_{i}")
            if adapter:
                results.append(adapter.name)
            time.sleep(0.001)

    # Create multiple threads
    threads = []
    for _ in range(5):
        t = threading.Thread(target=register_adapters)
        threads.append(t)
        t.start()

    for _ in range(5):
        t = threading.Thread(target=read_adapters)
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # Verify no errors occurred (thread-safety)
    # All adapters should be registered
    assert len(registry.list_all()) == 10


def test_adapter_registry_get_nonexistent():
    """Test getting non-existent adapter returns None."""
    registry = AdapterRegistry()

    # Try to get non-existent adapter
    adapter = registry.get("nonexistent")
    metadata = registry.get_metadata("nonexistent")

    assert adapter is None
    assert metadata is None


def test_adapter_metadata_completeness():
    """Test that ADAPTER_METADATA contains all required adapters."""
    # Verify all adapters have metadata
    required_adapters = ["http", "grpc", "websocket", "nats", "mcp"]

    for adapter_name in required_adapters:
        assert adapter_name in ADAPTER_METADATA, f"Adapter '{adapter_name}' missing from metadata"

        metadata = ADAPTER_METADATA[adapter_name]
        assert "inbound" in metadata, f"Adapter '{adapter_name}' missing inbound path"
        assert "outbound" in metadata, f"Adapter '{adapter_name}' missing outbound path"
        assert "direction" in metadata, f"Adapter '{adapter_name}' missing direction"
        assert "protocol" in metadata, f"Adapter '{adapter_name}' missing protocol"

        # Verify import paths are valid format
        assert ":" in metadata["inbound"], f"Invalid inbound path for '{adapter_name}'"
        assert ":" in metadata["outbound"], f"Invalid outbound path for '{adapter_name}'"

