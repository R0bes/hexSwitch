"""Runtime orchestration for HexSwitch."""

import logging
import signal
import sys
from typing import Any

from hexswitch.adapters.base import InboundAdapter, OutboundAdapter
from hexswitch.adapters.exceptions import AdapterError
from hexswitch.adapters.http import HttpAdapter

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

    if plan["inbound_adapters"] or plan["outbound_adapters"]:
        logger.info("")
        logger.info("Ready to start runtime")
    else:
        logger.info("")
        logger.info("No adapters enabled")
    logger.info("")


class Runtime:
    """Runtime orchestrator for HexSwitch adapters."""

    def __init__(self, config: dict[str, Any]):
        """Initialize runtime with configuration.

        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.inbound_adapters: list[InboundAdapter] = []
        self.outbound_adapters: list[OutboundAdapter] = []
        self._shutdown_requested = False

    def _create_inbound_adapter(self, name: str, adapter_config: dict[str, Any]) -> InboundAdapter:
        """Create an inbound adapter instance.

        Args:
            name: Adapter name.
            adapter_config: Adapter configuration.

        Returns:
            InboundAdapter instance.

        Raises:
            ValueError: If adapter type is not supported.
        """
        if name == "http":
            return HttpAdapter(name, adapter_config)
        else:
            raise ValueError(f"Unsupported inbound adapter type: {name}")

    def _create_outbound_adapter(
        self, name: str, adapter_config: dict[str, Any]
    ) -> OutboundAdapter:
        """Create an outbound adapter instance.

        Args:
            name: Adapter name.
            adapter_config: Adapter configuration.

        Returns:
            OutboundAdapter instance.

        Raises:
            ValueError: If adapter type is not supported.
        """
        raise ValueError(f"Unsupported outbound adapter type: {name}")

    def start(self) -> None:
        """Start all enabled adapters.

        Raises:
            RuntimeError: If adapter startup fails.
        """
        plan = build_execution_plan(self.config)

        # Start inbound adapters
        for adapter_info in plan["inbound_adapters"]:
            try:
                adapter = self._create_inbound_adapter(
                    adapter_info["name"], adapter_info["config"]
                )
                adapter.start()
                self.inbound_adapters.append(adapter)
                logger.info(f"Started inbound adapter: {adapter_info['name']}")
            except Exception as e:
                logger.error(f"Failed to start inbound adapter '{adapter_info['name']}': {e}")
                raise RuntimeError(f"Failed to start adapter '{adapter_info['name']}'") from e

        # Start outbound adapters
        for adapter_info in plan["outbound_adapters"]:
            try:
                adapter = self._create_outbound_adapter(
                    adapter_info["name"], adapter_info["config"]
                )
                adapter.connect()
                self.outbound_adapters.append(adapter)
                logger.info(f"Started outbound adapter: {adapter_info['name']}")
            except Exception as e:
                logger.error(f"Failed to start outbound adapter '{adapter_info['name']}': {e}")
                raise RuntimeError(f"Failed to start adapter '{adapter_info['name']}'") from e

        logger.info("All adapters started successfully")

    def stop(self) -> None:
        """Stop all adapters gracefully."""
        logger.info("Stopping runtime...")

        # Stop inbound adapters
        for adapter in self.inbound_adapters:
            try:
                adapter.stop()
                logger.info(f"Stopped inbound adapter: {adapter.name}")
            except AdapterError as e:
                logger.error(f"Error stopping inbound adapter '{adapter.name}': {e}")

        # Disconnect outbound adapters
        for adapter in self.outbound_adapters:
            try:
                adapter.disconnect()
                logger.info(f"Disconnected outbound adapter: {adapter.name}")
            except AdapterError as e:
                logger.error(f"Error disconnecting outbound adapter '{adapter.name}': {e}")

        self.inbound_adapters.clear()
        self.outbound_adapters.clear()
        logger.info("Runtime stopped")

    def run(self) -> None:
        """Run the runtime event loop (blocking).

        This method blocks until shutdown is requested (via signal or stop()).
        """
        logger.info("Runtime event loop started")
        try:
            # Simple blocking loop - can be enhanced with async/await later
            while not self._shutdown_requested:
                import time

                time.sleep(0.1)  # Small sleep to avoid busy-waiting
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            self.stop()

    def request_shutdown(self) -> None:
        """Request graceful shutdown of the runtime."""
        self._shutdown_requested = True


def run_runtime(config: dict[str, Any]) -> None:
    """Start the runtime event loop.

    Args:
        config: Configuration dictionary.

    Raises:
        RuntimeError: If runtime fails to start.
    """
    runtime = Runtime(config)

    # Set up signal handlers for graceful shutdown
    def signal_handler(signum: int, frame: Any) -> None:
        logger.info(f"Received signal {signum}, initiating shutdown...")
        runtime.request_shutdown()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        runtime.start()
        runtime.run()
    except Exception as e:
        logger.error(f"Runtime error: {e}")
        runtime.stop()
        raise RuntimeError(f"Runtime execution failed: {e}") from e


