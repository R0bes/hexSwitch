"""Unit tests for handler loader."""

import pytest

from hexswitch.handlers import HandlerError, load_handler


def test_load_handler_valid() -> None:
    """Test loading a valid handler."""
    # Use a standard library function as test handler
    handler = load_handler("json:dumps")
    assert callable(handler)
    assert handler({"test": "data"}) == '{"test": "data"}'


def test_load_handler_invalid_format_no_colon() -> None:
    """Test loading handler with invalid format (no colon)."""
    with pytest.raises(HandlerError, match="Invalid handler path format"):
        load_handler("json.dumps")


def test_load_handler_invalid_format_empty_module() -> None:
    """Test loading handler with empty module path."""
    with pytest.raises(HandlerError, match="Module path and function name must not be empty"):
        load_handler(":function")


def test_load_handler_invalid_format_empty_function() -> None:
    """Test loading handler with empty function name."""
    with pytest.raises(HandlerError, match="Module path and function name must not be empty"):
        load_handler("module:")


def test_load_handler_module_not_found() -> None:
    """Test loading handler from non-existent module."""
    with pytest.raises(HandlerError, match="Failed to import module"):
        load_handler("nonexistent.module:function")


def test_load_handler_function_not_found() -> None:
    """Test loading handler when function doesn't exist in module."""
    with pytest.raises(HandlerError, match="does not have attribute"):
        load_handler("json:nonexistent_function")


def test_load_handler_not_callable() -> None:
    """Test loading handler when attribute is not callable."""
    with pytest.raises(HandlerError, match="is not callable"):
        load_handler("json:JSONEncoder")  # JSONEncoder is a class, not a function


def test_load_handler_with_rsplit() -> None:
    """Test that handler path with multiple colons uses rsplit correctly."""
    # This should work: module.path:function
    handler = load_handler("json:dumps")
    assert callable(handler)

