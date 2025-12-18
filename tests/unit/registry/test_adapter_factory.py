"""Unit tests for AdapterFactory."""

import pytest

from hexswitch.adapters.exceptions import AdapterError
from hexswitch.registry.factory import AdapterFactory


def test_adapter_factory_creates_adapter():
    """Test that factory creates adapter from import path."""
    # Test creating HTTP inbound adapter
    impl_path = "hexswitch.adapters.http:FastApiHttpAdapterServer"
    cfg = {
        "name": "http",
        "port": 8000,
        "base_path": "/api",
        "routes": [],
    }

    adapter = AdapterFactory.create(impl_path, cfg)

    # Verify adapter was created
    assert adapter is not None
    assert adapter.name == "http"
    assert adapter.config == cfg


def test_adapter_factory_creates_outbound_adapter():
    """Test that factory creates outbound adapter from import path."""
    # Test creating HTTP outbound adapter
    impl_path = "hexswitch.adapters.http:HttpAdapterClient"
    cfg = {
        "name": "http_client",
        "base_url": "https://api.example.com",
        "timeout": 30,
    }

    adapter = AdapterFactory.create(impl_path, cfg)

    # Verify adapter was created
    assert adapter is not None
    assert adapter.name == "http_client"
    assert adapter.config == cfg


def test_adapter_factory_invalid_path():
    """Test factory error handling for invalid paths."""
    # Test invalid format (no colon)
    with pytest.raises(AdapterError, match="Invalid adapter path format"):
        AdapterFactory.create("invalid.path", {})

    # Test invalid format (empty module path)
    with pytest.raises(AdapterError, match="Module path and class name must not be empty"):
        AdapterFactory.create(":ClassName", {})

    # Test invalid format (empty class name)
    with pytest.raises(AdapterError, match="Module path and class name must not be empty"):
        AdapterFactory.create("module.path:", {})

    # Test non-existent module
    with pytest.raises(AdapterError, match="Failed to import module"):
        AdapterFactory.create("nonexistent.module:ClassName", {})

    # Test non-existent class
    with pytest.raises(AdapterError, match="does not have class"):
        AdapterFactory.create("hexswitch.adapters.http:NonExistentClass", {})


def test_adapter_factory_invalid_class_type():
    """Test factory error handling for invalid class types."""
    # Test class that is not an adapter
    with pytest.raises(AdapterError, match="is not an adapter"):
        AdapterFactory.create("hexswitch.shared.envelope:Envelope", {})


def test_adapter_factory_config_passed_correctly():
    """Test that configuration is correctly passed to adapter."""
    impl_path = "hexswitch.adapters.http:FastApiHttpAdapterServer"
    cfg = {
        "name": "test_http",
        "port": 9000,
        "base_path": "/test",
        "routes": [
            {
                "path": "/test",
                "method": "GET",
                "handler": "test:handler",
            }
        ],
    }

    adapter = AdapterFactory.create(impl_path, cfg)

    # Verify config was passed correctly
    assert adapter.config == cfg
    assert adapter.config["port"] == 9000
    assert adapter.config["base_path"] == "/test"


def test_adapter_factory_name_inference():
    """Test that factory infers adapter name from class name if not provided."""
    impl_path = "hexswitch.adapters.http:FastApiHttpAdapterServer"
    cfg = {
        "port": 8000,
        "routes": [],
    }

    adapter = AdapterFactory.create(impl_path, cfg)

    # Verify name was inferred (should be "http" from class name)
    assert adapter.name is not None
    assert len(adapter.name) > 0

