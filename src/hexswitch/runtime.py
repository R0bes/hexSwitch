"""Runtime orchestration for HexSwitch."""

import signal
from typing import Any

from hexswitch.adapters.base import InboundAdapter, OutboundAdapter
from hexswitch.adapters.exceptions import AdapterError
from hexswitch.adapters.grpc import GrpcAdapterClient, GrpcAdapterServer
from hexswitch.adapters.http import FastApiHttpAdapterServer, HttpAdapterClient
from hexswitch.adapters.mcp import McpAdapterClient, McpAdapterServer
from hexswitch.adapters.websocket import WebSocketAdapterClient, WebSocketAdapterServer
from hexswitch.ports.registry import get_port_registry
from hexswitch.shared.logging import get_logger
from hexswitch.shared.observability import (
    get_global_metrics_collector,
    get_global_tracer,
    start_span,
)

logger = get_logger(__name__)


def build_execution_plan(config: dict[str, Any]) -> dict[str, Any]:
    """Build execution plan from configuration.

    Args:
        config: Configuration dictionary (may contain Pydantic models after validation).

    Returns:
        Execution plan dictionary showing which adapters will be activated.
    """
    # Extract service name
    service_config = config.get("service", {})
    if hasattr(service_config, "name"):
        # Pydantic model
        service_name = service_config.name
    elif isinstance(service_config, dict):
        service_name = service_config.get("name", "unknown")
    else:
        service_name = "unknown"

    plan: dict[str, Any] = {
        "service": service_name,
        "inbound_adapters": [],
        "outbound_adapters": [],
    }

    # Collect enabled inbound adapters
    inbound = config.get("inbound")
    if inbound is not None:
        # Handle Pydantic model
        if hasattr(inbound, "model_dump"):
            inbound_dict = inbound.model_dump(exclude_none=True)
            for adapter_name, adapter_config in inbound_dict.items():
                if adapter_config and isinstance(adapter_config, dict):
                    enabled = adapter_config.get("enabled", False)
                    if enabled:
                        plan["inbound_adapters"].append(
                            {
                                "name": adapter_name,
                                "config": adapter_config,
                            }
                        )
        # Handle dictionary
        elif isinstance(inbound, dict):
            for adapter_name, adapter_config in inbound.items():
                if isinstance(adapter_config, dict) and adapter_config.get("enabled", False):
                    plan["inbound_adapters"].append(
                        {
                            "name": adapter_name,
                            "config": adapter_config,
                        }
                    )

    # Collect enabled outbound adapters
    outbound = config.get("outbound")
    if outbound is not None:
        # Handle Pydantic model
        if hasattr(outbound, "model_dump"):
            outbound_dict = outbound.model_dump(exclude_none=True)
            for adapter_name, adapter_config in outbound_dict.items():
                if adapter_config and isinstance(adapter_config, dict):
                    enabled = adapter_config.get("enabled", False)
                    if enabled:
                        plan["outbound_adapters"].append(
                            {
                                "name": adapter_name,
                                "config": adapter_config,
                            }
                        )
        # Handle dictionary
        elif isinstance(outbound, dict):
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

        # Initialize observability
        self._tracer = get_global_tracer()
        self._metrics = get_global_metrics_collector()

        # Runtime metrics
        self._runtime_start_time: float | None = None
        self._adapter_start_counter = self._metrics.counter("runtime_adapter_starts_total")
        self._adapter_stop_counter = self._metrics.counter("runtime_adapter_stops_total")
        self._adapter_error_counter = self._metrics.counter("runtime_adapter_errors_total")
        self._active_adapters_gauge = self._metrics.gauge("runtime_active_adapters")
        self._adapter_start_duration = self._metrics.histogram("runtime_adapter_start_duration_seconds")

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
            return FastApiHttpAdapterServer(name, adapter_config)
        elif name == "grpc":
            return GrpcAdapterServer(name, adapter_config)
        elif name == "websocket":
            return WebSocketAdapterServer(name, adapter_config)
        elif name == "mcp":
            return McpAdapterServer(name, adapter_config)
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
        if name == "http_client":
            return HttpAdapterClient(name, adapter_config)
        elif name == "mcp_client":
            return McpAdapterClient(name, adapter_config)
        elif name == "grpc_client":
            return GrpcAdapterClient(name, adapter_config)
        elif name == "websocket_client":
            return WebSocketAdapterClient(name, adapter_config)
        else:
            raise ValueError(f"Unsupported outbound adapter type: {name}")

    def start(self) -> None:
        """Start all enabled adapters.

        Raises:
            RuntimeError: If adapter startup fails.
        """
        import time

        span = start_span("runtime.start", tags={"service": self.config.get("service", {}).get("name", "unknown")})
        self._runtime_start_time = time.time()

        try:
            plan = build_execution_plan(self.config)

            # Start inbound adapters
            for adapter_info in plan["inbound_adapters"]:
                adapter_span = start_span(
                    "adapter.start",
                    parent=span,
                    tags={"adapter": adapter_info["name"], "type": "inbound"},
                )
                start_time = time.time()
                try:
                    inbound_adapter: InboundAdapter = self._create_inbound_adapter(
                        adapter_info["name"], adapter_info["config"]
                    )
                    inbound_adapter.start()
                    self.inbound_adapters.append(inbound_adapter)
                    duration = time.time() - start_time
                    self._adapter_start_duration.observe(duration)
                    self._adapter_start_counter.inc()
                    self._active_adapters_gauge.set(len(self.inbound_adapters) + len(self.outbound_adapters))
                    adapter_span.add_tag("status", "success")
                    logger.info(f"Started inbound adapter: {adapter_info['name']}")
                except Exception as e:
                    self._adapter_error_counter.inc()
                    adapter_span.add_tag("status", "error")
                    adapter_span.add_tag("error", str(e))
                    logger.error(f"Failed to start inbound adapter '{adapter_info['name']}': {e}")
                    raise RuntimeError(f"Failed to start adapter '{adapter_info['name']}'") from e
                finally:
                    adapter_span.finish()

            # Start outbound adapters and bind to ports
            port_registry = get_port_registry()
            for adapter_info in plan["outbound_adapters"]:
                adapter_span = start_span(
                    "adapter.connect",
                    parent=span,
                    tags={"adapter": adapter_info["name"], "type": "outbound"},
                )
                start_time = time.time()
                try:
                    adapter: OutboundAdapter = self._create_outbound_adapter(
                        adapter_info["name"], adapter_info["config"]
                    )
                    adapter.connect()
                    self.outbound_adapters.append(adapter)

                    # Bind adapter to outbound ports (if configured)
                    adapter_config = adapter_info["config"]
                    port_names = adapter_config.get("ports", [])
                    if isinstance(port_names, str):
                        port_names = [port_names]

                    for port_name in port_names:
                        try:
                            # Register handler that routes through the adapter
                            def create_adapter_handler(adapter_instance: OutboundAdapter):
                                def handler(envelope):
                                    return adapter_instance.request(envelope)
                                return handler

                            handler = create_adapter_handler(adapter)
                            port_registry.register_handler(port_name, handler)
                            logger.info(f"Bound outbound adapter '{adapter_info['name']}' to port '{port_name}'")
                        except Exception as e:
                            logger.warning(f"Failed to bind adapter to port '{port_name}': {e}")

                    duration = time.time() - start_time
                    self._adapter_start_duration.observe(duration)
                    self._adapter_start_counter.inc()
                    self._active_adapters_gauge.set(len(self.inbound_adapters) + len(self.outbound_adapters))
                    adapter_span.add_tag("status", "success")
                    logger.info(f"Started outbound adapter: {adapter_info['name']}")
                except Exception as e:
                    self._adapter_error_counter.inc()
                    adapter_span.add_tag("status", "error")
                    adapter_span.add_tag("error", str(e))
                    logger.error(f"Failed to start outbound adapter '{adapter_info['name']}': {e}")
                    raise RuntimeError(f"Failed to start adapter '{adapter_info['name']}'") from e
                finally:
                    adapter_span.finish()

            adapters_count = len(self.inbound_adapters) + len(self.outbound_adapters)
            span.add_tag("adapters_started", str(adapters_count))
            logger.info("All adapters started successfully")
        finally:
            span.finish()

    def stop(self) -> None:
        """Stop all adapters gracefully."""
        span = start_span("runtime.stop")
        logger.info("Stopping runtime...")

        try:
            # Stop inbound adapters
            for inbound_adapter in self.inbound_adapters:
                adapter_span = start_span(
                    "adapter.stop",
                    parent=span,
                    tags={"adapter": inbound_adapter.name, "type": "inbound"},
                )
                try:
                    inbound_adapter.stop()
                    self._adapter_stop_counter.inc()
                    self._active_adapters_gauge.set(len(self.inbound_adapters) + len(self.outbound_adapters) - 1)
                    adapter_span.add_tag("status", "success")
                    logger.info(f"Stopped inbound adapter: {inbound_adapter.name}")
                except AdapterError as e:
                    self._adapter_error_counter.inc()
                    adapter_span.add_tag("status", "error")
                    adapter_span.add_tag("error", str(e))
                    logger.error(f"Error stopping inbound adapter '{inbound_adapter.name}': {e}")
                finally:
                    adapter_span.finish()

            # Disconnect outbound adapters
            for outbound_adapter in self.outbound_adapters:
                adapter_span = start_span(
                    "adapter.disconnect",
                    parent=span,
                    tags={"adapter": outbound_adapter.name, "type": "outbound"},
                )
                try:
                    outbound_adapter.disconnect()
                    self._adapter_stop_counter.inc()
                    self._active_adapters_gauge.set(len(self.inbound_adapters) + len(self.outbound_adapters) - 1)
                    adapter_span.add_tag("status", "success")
                    logger.info(f"Disconnected outbound adapter: {outbound_adapter.name}")
                except AdapterError as e:
                    self._adapter_error_counter.inc()
                    adapter_span.add_tag("status", "error")
                    adapter_span.add_tag("error", str(e))
                    logger.error(f"Error disconnecting outbound adapter '{outbound_adapter.name}': {e}")
                finally:
                    adapter_span.finish()

            self.inbound_adapters.clear()
            self.outbound_adapters.clear()
            self._active_adapters_gauge.set(0)
            logger.info("Runtime stopped")
        finally:
            span.finish()

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
