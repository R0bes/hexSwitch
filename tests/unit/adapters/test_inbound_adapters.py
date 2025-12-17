"""Parametrized tests for all inbound adapters."""

from typing import Any, Callable

import pytest

from hexswitch.adapters.base import InboundAdapter
from tests.unit.adapters.base.adapter_tester import AdapterTester
from tests.unit.adapters.base.adapter_test_data import (
    INBOUND_ADAPTERS,
)


@pytest.mark.fast
@pytest.mark.parametrize(
    "adapter_name,adapter_class,config_factory,expected_attrs",
    INBOUND_ADAPTERS,
)
def test_inbound_adapter_initialization(
    adapter_name: str,  # noqa: ARG001
    adapter_class: type[InboundAdapter],
    config_factory: Callable[[], dict[str, Any]],
    expected_attrs: dict[str, Any],
) -> None:
    """Test initialization for all inbound adapters."""
    config = config_factory()
    # Set port to a fixed value for initialization test
    if "port" in config:
        config["port"] = expected_attrs.get("port", 0)
    AdapterTester.test_initialization(adapter_class, config, expected_attrs)


@pytest.mark.fast
@pytest.mark.parametrize(
    "adapter_name,adapter_class,config_factory,_",
    INBOUND_ADAPTERS,
)
def test_inbound_adapter_lifecycle(
    adapter_name: str,
    adapter_class: type[InboundAdapter],
    config_factory: Callable[[], dict[str, Any]],
    _: dict[str, Any],
) -> None:
    """Test lifecycle for all inbound adapters."""
    # Use appropriate sleep time based on adapter type
    sleep_time = 0.5 if adapter_name == "websocket" else 0.1
    AdapterTester.test_inbound_lifecycle(
        adapter_class, config_factory, sleep_time=sleep_time
    )


@pytest.mark.fast
@pytest.mark.parametrize(
    "adapter_name,adapter_class,config_factory,_",
    INBOUND_ADAPTERS,
)
def test_inbound_adapter_start_twice(
    adapter_name: str,
    adapter_class: type[InboundAdapter],
    config_factory: Callable[[], dict[str, Any]],
    _: dict[str, Any],
) -> None:
    """Test starting adapter twice for all inbound adapters."""
    # Use appropriate sleep time based on adapter type
    sleep_time = 0.5 if adapter_name == "websocket" else 0.1
    AdapterTester.test_start_twice(
        adapter_class, config_factory, sleep_time=sleep_time
    )


@pytest.mark.fast
@pytest.mark.parametrize(
    "adapter_name,adapter_class,config_factory,expected_attrs",
    INBOUND_ADAPTERS,
)
def test_inbound_adapter_stop_when_not_running(
    adapter_name: str,  # noqa: ARG001
    adapter_class: type[InboundAdapter],
    config_factory: Callable[[], dict[str, Any]],
    expected_attrs: dict[str, Any],
) -> None:
    """Test stopping adapter when not running for all inbound adapters."""
    config = config_factory()
    # Set port to a fixed value for this test
    if "port" in config:
        config["port"] = expected_attrs.get("port", 0)
    AdapterTester.test_stop_when_not_running(adapter_class, lambda: config)
