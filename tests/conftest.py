"""Pytest configuration and fixtures."""

import sys
from pathlib import Path
from types import ModuleType
from typing import Callable

import pytest

# Add src directory to Python path if not already there
# This ensures hexswitch can be imported even when pytest is called directly
project_root = Path(__file__).parent.parent.resolve()
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from hexswitch.shared.envelope import Envelope
from tests.unit.adapters.base.adapter_tester import AdapterTester

# Try to import pytest-timeout, if available
try:
    import pytest_timeout  # noqa: F401
except ImportError:
    # pytest-timeout not installed, timeout markers will be ignored
    # Tests will rely on subprocess timeouts instead
    pass


# Auto-mark tests based on directory structure
def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark basic tests (core functionality)
        if "test_envelope" in str(item.fspath) or "test_ports" in str(item.fspath) or "test_strategies" in str(item.fspath):
            item.add_marker(pytest.mark.basic)
            item.add_marker(pytest.mark.order(1))

        # Mark unit tests
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.order(2))

        # Mark integration tests
        elif "integration" in str(item.fspath):
            if "e2e" in str(item.fspath) or "test_e2e" in str(item.fspath):
                item.add_marker(pytest.mark.e2e)
                item.add_marker(pytest.mark.order(4))
            else:
                item.add_marker(pytest.mark.integration)
                item.add_marker(pytest.mark.order(3))


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
