"""Unit tests for version import."""

import pytest

from hexswitch import __version__


def test_version_is_defined() -> None:
    """Test that __version__ is defined and is a string."""
    assert isinstance(__version__, str)
    assert __version__ == "0.1.0"


def test_version_format() -> None:
    """Test that version follows semantic versioning format."""
    parts = __version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)

