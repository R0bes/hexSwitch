"""Pytest configuration and fixtures."""

import sys
from types import ModuleType
from typing import Any, Callable

import pytest

from hexswitch.shared.envelope import Envelope
from tests.unit.adapters.base.adapter_tester import AdapterTester

# Try to import pytest-timeout, if available
try:
    import pytest_timeout  # noqa: F401
except ImportError:
    # pytest-timeout not installed, timeout markers will be ignored
    # Tests will rely on subprocess timeouts instead
    pass


@pytest.fixture
def free_port() -> int:
    """Get a free port for testing.

    Returns:
        Free port number.
    """
    return AdapterTester.find_free_port()


@pytest.fixture
def malicious_payloads() -> list[str]:
    """Get list of malicious payloads for security testing.

    Returns:
        List of malicious payload strings.
    """
    return AdapterTester.create_malicious_payloads()


@pytest.fixture
def mock_handler() -> Callable[[Envelope], Envelope]:
    """Create mock handler for testing.

    Returns:
        Mock handler function.
    """
    def handler(envelope: Envelope) -> Envelope:
        return Envelope.success({"result": "success", "path": envelope.path})
    return handler


@pytest.fixture
def handler_module(mock_handler: Callable) -> ModuleType:
    """Create a test handler module.

    Args:
        mock_handler: Mock handler function.

    Yields:
        Test module with handler.
    """
    module_name = "test_handler_module"
    if module_name in sys.modules:
        del sys.modules[module_name]

    test_module = ModuleType(module_name)
    test_module.test_handler = mock_handler  # type: ignore[attr-defined]
    sys.modules[module_name] = test_module

    yield test_module

    if module_name in sys.modules:
        del sys.modules[module_name]
