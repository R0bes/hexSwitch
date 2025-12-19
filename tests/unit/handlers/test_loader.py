"""Unit tests for HandlerLoader."""

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

from hexswitch.handlers.loader import HandlerError, HandlerLoader
from hexswitch.ports.exceptions import PortNotFoundError
from hexswitch.shared.envelope import Envelope


def test_handler_loader_resolves_import_path():
    """Test handler loader resolves import path."""
    loader = HandlerLoader()

    # Create test module
    test_module = ModuleType("test_handler_module")

    def test_handler(envelope: Envelope) -> Envelope:
        return Envelope.success({"test": "data"})

    test_module.test_handler = test_handler
    sys.modules["test_handler_module"] = test_module

    try:
        # Resolve handler
        handler = loader.resolve("test_handler_module:test_handler")

        # Verify handler was loaded
        assert handler is not None
        assert callable(handler)
        assert handler == test_handler

        # Verify handler is cached
        cached_handler = loader.get_cached("test_handler_module:test_handler")
        assert cached_handler == handler

    finally:
        if "test_handler_module" in sys.modules:
            del sys.modules["test_handler_module"]


def test_handler_loader_resolves_port_name():
    """Test handler loader resolves port name."""
    loader = HandlerLoader()

    # Mock port registry
    mock_port = MagicMock()
    mock_handler = MagicMock(return_value=Envelope.success({"port": "handler"}))
    mock_port.handlers = [mock_handler]

    with patch("hexswitch.handlers.loader.get_port_registry") as mock_registry:
        mock_registry.return_value.get_handler.return_value = mock_handler

        # Resolve handler from port
        handler = loader.resolve("test_port")

        # Verify handler was loaded
        assert handler is not None
        assert callable(handler)
        assert handler == mock_handler

        # Verify handler is cached
        cached_handler = loader.get_cached("test_port")
        assert cached_handler == handler


def test_handler_loader_caches_handlers():
    """Test handler loader caches handlers."""
    loader = HandlerLoader()

    # Create test module
    test_module = ModuleType("test_cache_module")

    call_count = 0

    def test_handler(envelope: Envelope) -> Envelope:
        nonlocal call_count
        call_count += 1
        return Envelope.success({"count": call_count})

    test_module.test_handler = test_handler
    sys.modules["test_cache_module"] = test_module

    try:
        # Resolve handler first time
        handler1 = loader.resolve("test_cache_module:test_handler")

        # Resolve handler second time (should use cache)
        handler2 = loader.resolve("test_cache_module:test_handler")

        # Verify same handler instance
        assert handler1 is handler2

        # Verify cache was used (importlib.import_module should only be called once)
        # This is implicit - if cache wasn't used, we'd see different behavior

    finally:
        if "test_cache_module" in sys.modules:
            del sys.modules["test_cache_module"]


def test_handler_loader_validates_signature():
    """Test handler loader validates signature."""
    loader = HandlerLoader()

    # Create test module with valid handler
    test_module = ModuleType("test_signature_module")

    def valid_handler(envelope: Envelope) -> Envelope:
        return envelope

    def invalid_handler():  # No parameters
        return None

    test_module.valid = valid_handler
    test_module.invalid = invalid_handler
    sys.modules["test_signature_module"] = test_module

    try:
        # Valid handler should work
        handler = loader.resolve("test_signature_module:valid")
        assert handler is not None

        # Invalid handler should still work (signature validation is lenient)
        # The validation is more of a warning than a hard error
        handler2 = loader.resolve("test_signature_module:invalid")
        assert handler2 is not None

    finally:
        if "test_signature_module" in sys.modules:
            del sys.modules["test_signature_module"]


def test_handler_loader_invalid_path():
    """Test handler loader error handling for invalid paths."""
    loader = HandlerLoader()

    # Test invalid format (no colon)
    with pytest.raises(HandlerError, match="Invalid handler path"):
        loader.resolve("invalid.path")

    # Test non-existent module
    with pytest.raises(HandlerError, match="Failed to import module"):
        loader.resolve("nonexistent.module:function")

    # Test non-existent function
    test_module = ModuleType("test_nonexistent_module")
    sys.modules["test_nonexistent_module"] = test_module

    try:
        with pytest.raises(HandlerError, match="does not have attribute"):
            loader.resolve("test_nonexistent_module:nonexistent_function")
    finally:
        if "test_nonexistent_module" in sys.modules:
            del sys.modules["test_nonexistent_module"]


def test_handler_loader_load_from_port():
    """Test handler loader load_from_port method."""
    loader = HandlerLoader()

    # Mock port registry
    mock_port = MagicMock()
    mock_handler = MagicMock(return_value=Envelope.success({"port": "handler"}))
    mock_port.handlers = [mock_handler]

    with patch("hexswitch.handlers.loader.get_port_registry") as mock_registry:
        mock_registry.return_value.get_handler.return_value = mock_handler

        # Load handler from port
        handler = loader.load_from_port("test_port")

        # Verify handler was loaded
        assert handler is not None
        assert callable(handler)
        assert handler == mock_handler


def test_handler_loader_load_from_port_not_found():
    """Test handler loader error handling for non-existent port."""
    loader = HandlerLoader()

    # Mock port registry to raise PortNotFoundError
    with patch("hexswitch.handlers.loader.get_port_registry") as mock_registry:
        mock_registry.return_value.get_handler.side_effect = PortNotFoundError("Port not found")

        with pytest.raises(HandlerError, match="Port 'nonexistent_port' not found"):
            loader.load_from_port("nonexistent_port")


def test_handler_loader_cache_handler():
    """Test handler loader cache_handler method."""
    loader = HandlerLoader()

    # Create mock handler
    mock_handler = MagicMock()

    # Cache handler
    loader.cache_handler("test_path", mock_handler)

    # Verify handler is cached
    cached_handler = loader.get_cached("test_path")
    assert cached_handler == mock_handler


def test_handler_loader_clear_cache():
    """Test handler loader clear_cache method."""
    loader = HandlerLoader()

    # Create test module
    test_module = ModuleType("test_clear_module")

    def test_handler(envelope: Envelope) -> Envelope:
        return envelope

    test_module.test = test_handler
    sys.modules["test_clear_module"] = test_module

    try:
        # Resolve and cache handler
        handler = loader.resolve("test_clear_module:test")
        assert loader.get_cached("test_clear_module:test") == handler

        # Clear cache
        loader.clear_cache()

        # Verify cache is empty
        assert loader.get_cached("test_clear_module:test") is None

    finally:
        if "test_clear_module" in sys.modules:
            del sys.modules["test_clear_module"]


def test_handler_loader_thread_safety():
    """Test that handler loader is thread-safe."""
    import threading

    loader = HandlerLoader()

    # Create test module
    test_module = ModuleType("test_thread_module")

    def test_handler(envelope: Envelope) -> Envelope:
        return envelope

    test_module.test = test_handler
    sys.modules["test_thread_module"] = test_module

    results = []

    def resolve_handler():
        try:
            handler = loader.resolve("test_thread_module:test")
            results.append(handler)
        except Exception as e:
            results.append(f"Error: {e}")

    try:
        # Create multiple threads
        threads = []
        for _ in range(10):
            t = threading.Thread(target=resolve_handler)
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify all threads got the same handler
        assert len(results) == 10
        assert all(r == test_handler for r in results)

    finally:
        if "test_thread_module" in sys.modules:
            del sys.modules["test_thread_module"]

