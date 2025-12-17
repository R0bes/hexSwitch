"""Parametrized tests for all outbound adapters."""

from typing import Any, Callable

import pytest

from hexswitch.adapters.base import OutboundAdapter
from tests.unit.adapters.base.adapter_tester import AdapterTester
from tests.unit.adapters.base.adapter_test_data import (
    OUTBOUND_ADAPTERS,
)


@pytest.mark.fast
@pytest.mark.parametrize(
    "adapter_name,adapter_class,config_factory",
    OUTBOUND_ADAPTERS,
)
def test_outbound_adapter_initialization(
    adapter_name: str,  # noqa: ARG001
    adapter_class: type[OutboundAdapter],
    config_factory: Callable[[], dict[str, Any]],
) -> None:
    """Test initialization for all outbound adapters."""
    config = config_factory()
    AdapterTester.test_initialization(adapter_class, config)


@pytest.mark.fast
@pytest.mark.parametrize(
    "adapter_name,adapter_class,config_factory",
    OUTBOUND_ADAPTERS,
)
def test_outbound_adapter_connect_twice(
    adapter_name: str,  # noqa: ARG001
    adapter_class: type[OutboundAdapter],
    config_factory: Callable[[], dict[str, Any]],
) -> None:
    """Test connecting adapter twice for all outbound adapters."""
    AdapterTester.test_connect_twice(adapter_class, config_factory)


@pytest.mark.fast
@pytest.mark.parametrize(
    "adapter_name,adapter_class,config_factory",
    OUTBOUND_ADAPTERS,
)
def test_outbound_adapter_disconnect_when_not_connected(
    adapter_name: str,  # noqa: ARG001
    adapter_class: type[OutboundAdapter],
    config_factory: Callable[[], dict[str, Any]],
) -> None:
    """Test disconnecting adapter when not connected."""
    AdapterTester.test_disconnect_when_not_connected(
        adapter_class, config_factory
    )
