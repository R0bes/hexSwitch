"""Runtime orchestration for HexSwitch."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def build_execution_plan(config: dict[str, Any]) -> dict[str, Any]:
    """Build execution plan from configuration.

    Args:
        config: Configuration dictionary.

    Returns:
        Execution plan dictionary showing which adapters will be activated.
    """
    plan: dict[str, Any] = {
        "service": config.get("service", {}).get("name", "unknown"),
        "inbound_adapters": [],
        "outbound_adapters": [],
    }

    # Collect enabled inbound adapters
    inbound = config.get("inbound", {})
    for adapter_name, adapter_config in inbound.items():
        if isinstance(adapter_config, dict) and adapter_config.get("enabled", False):
            plan["inbound_adapters"].append(
                {
                    "name": adapter_name,
                    "config": adapter_config,
                }
            )

    # Collect enabled outbound adapters
    outbound = config.get("outbound", {})
    for adapter_name, adapter_config in outbound.items():
        if isinstance(adapter_config, dict) and adapter_config.get("enabled", False):
            plan["outbound_adapters"].append(
                {
                    "name": adapter_name,
                    "config": adapter_config,
                }
            )

    return plan


def print_execution_plan(plan: dict[str, Any]) -> None:
    """Print execution plan in human-readable format.

    Args:
        plan: Execution plan dictionary.
    """
    logger.info(f"Execution Plan for service: {plan['service']}")
    logger.info("")

    if plan["inbound_adapters"]:
        logger.info("Inbound Adapters:")
        for adapter in plan["inbound_adapters"]:
            logger.info(f"  - {adapter['name']}: enabled")
    else:
        logger.info("Inbound Adapters: none")

    logger.info("")

    if plan["outbound_adapters"]:
        logger.info("Outbound Adapters:")
        for adapter in plan["outbound_adapters"]:
            logger.info(f"  - {adapter['name']}: enabled")
    else:
        logger.info("Outbound Adapters: none")

    logger.info("")
    logger.info("Runtime execution is not implemented yet.")


def run_runtime(config: dict[str, Any]) -> None:
    """Start the runtime event loop.

    Args:
        config: Configuration dictionary.

    Raises:
        NotImplementedError: Runtime execution is not yet implemented.
    """
    raise NotImplementedError("Runtime execution is not yet implemented")


