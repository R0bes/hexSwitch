"""FastAPI-based HTTP inbound adapter for HexSwitch."""

import asyncio
import importlib
import logging
import threading
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn

from hexswitch.adapters.base import InboundAdapter
from hexswitch.adapters.exceptions import AdapterStartError, AdapterStopError, HandlerError
from hexswitch.adapters.http._Http_Envelope import HttpEnvelope
from hexswitch.ports import PortError, get_port_registry
from hexswitch.shared.helpers import parse_path_params

logger = logging.getLogger(__name__)


class FastApiHttpAdapterServer(InboundAdapter):
    """FastAPI-based HTTP inbound adapter for HexSwitch."""

    def __init__(self, name: str, config: dict[str, Any]):
        """Initialize FastAPI HTTP adapter.

        Args:
            name: Adapter name.
            config: Adapter configuration dictionary.
        """
        self.name = name
        self.config = config
        self._running = False
        self._converter = HttpEnvelope()
        self.port = config.get("port", 8000)
        self.base_path = config.get("base_path", "")
        self.routes = config.get("routes", [])

        # Create FastAPI app
        self.app = FastAPI(title="HexSwitch", version="0.1.0")
        self._setup_routes()

        # OpenTelemetry instrumentation
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(self.app)
            logger.debug("OpenTelemetry FastAPI instrumentation enabled")
        except ImportError:
            logger.warning(
                "OpenTelemetry FastAPI instrumentation not available"
            )

        # Server task and event loop
        self._server_task: asyncio.Task | None = None
        self._server: uvicorn.Server | None = None
        self._server_loop: asyncio.AbstractEventLoop | None = None
        self._server_thread: threading.Thread | None = None

    def _setup_routes(self) -> None:
        """Set up FastAPI routes from configuration."""
        port_registry = get_port_registry()

        for route_config in self.routes:
            path = route_config["path"]
            method = route_config["method"].upper()
            handler_path = route_config.get("handler")
            port_name = route_config.get("port")

            # Build full path with base_path
            base = self.base_path.rstrip("/")
            full_path = f"{base}{path}" if base else path

            # Create route handler
            def create_handler(
                route_cfg: dict[str, Any],
                route_path: str,
                route_pattern: str,
                handler_path_val: str | None,
                port_name_val: str | None,
            ):
                """Create async route handler."""

                async def route_handler(request: Request) -> Response:
                    """Handle HTTP request."""
                    try:
                        # Load handler or port
                        handler = None
                        if port_name_val:
                            handler = port_registry.get_handler(port_name_val)
                        elif handler_path_val:
                            if ":" not in handler_path_val:
                                return JSONResponse(
                                    {"error": "Invalid handler format"},
                                    status_code=500,
                                )
                            module_path, function_name = handler_path_val.rsplit(":", 1)
                            module = importlib.import_module(module_path)
                            handler = getattr(module, function_name)
                        else:
                            return JSONResponse(
                                {"error": "No handler or port specified"},
                                status_code=500,
                            )

                        # Convert FastAPI request to Envelope
                        body = await request.body()
                        query_params = dict(request.query_params)
                        path_params = parse_path_params(
                            route_path, route_pattern
                        )
                        headers = dict(request.headers)

                        request_envelope = self._converter.request_to_envelope(
                            method=request.method,
                            path=route_path,
                            headers=headers,
                            query_params=query_params,
                            body=body,
                            path_params=path_params,
                        )

                        # Call handler (sync or async)
                        if asyncio.iscoroutinefunction(handler):
                            response_envelope = await handler(request_envelope)
                        else:
                            # Run sync handler in thread pool
                            loop = asyncio.get_event_loop()
                            response_envelope = await loop.run_in_executor(
                                None, handler, request_envelope
                            )

                        # Convert Envelope to FastAPI response
                        (
                            status_code,
                            data,
                            response_headers,
                        ) = self._converter.envelope_to_response(response_envelope)

                        return JSONResponse(
                            content=data,
                            status_code=status_code,
                            headers=response_headers,
                        )
                    except (HandlerError, PortError) as e:
                        logger.error(f"Handler/Port error: {e}")
                        return JSONResponse(
                            {"error": "Internal Server Error", "message": str(e)},
                            status_code=500,
                        )
                    except Exception as e:
                        logger.exception(f"Handler error: {e}")
                        return JSONResponse(
                            {"error": "Internal Server Error", "message": str(e)},
                            status_code=500,
                        )

                return route_handler

            # Register route with FastAPI
            handler_func = create_handler(
                route_config, full_path, path, handler_path, port_name
            )
            self.app.add_api_route(full_path, handler_func, methods=[method])

    def start(self) -> None:
        """Start the FastAPI server.

        Raises:
            AdapterStartError: If the server fails to start.
        """
        if self._running:
            logger.warning(f"HTTP adapter '{self.name}' is already running")
            return

        try:
            config = uvicorn.Config(
                self.app, host="0.0.0.0", port=self.port, log_level="info"
            )
            self._server = uvicorn.Server(config)

            # Start server in background
            import threading

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._server_loop = loop
            self._server_task = loop.create_task(self._server.serve())

            # Run server in separate thread
            def run_server():
                loop.run_forever()

            self._server_thread = threading.Thread(target=run_server, daemon=True)
            self._server_thread.start()
            self._running = True

            logger.info(
                f"FastAPI HTTP adapter '{self.name}' started on port {self.port} "
                f"with base_path '{self.base_path}'"
            )
        except Exception as e:
            raise AdapterStartError(
                f"Failed to start HTTP adapter '{self.name}': {e}"
            ) from e

    def stop(self) -> None:
        """Stop the FastAPI server.

        Raises:
            AdapterStopError: If the server fails to stop.
        """
        if not self._running:
            logger.warning(f"HTTP adapter '{self.name}' is not running")
            return

        try:
            # Gracefully stop the uvicorn server
            if self._server:
                self._server.should_exit = True

            # Cancel the server task
            if self._server_task and not self._server_task.done():
                self._server_task.cancel()

            # Stop the event loop gracefully
            if self._server_loop and self._server_loop.is_running():
                try:
                    # Schedule loop stop in a thread-safe way
                    self._server_loop.call_soon_threadsafe(self._server_loop.stop)
                    # Wait briefly for loop to stop
                    import time
                    time.sleep(0.2)
                except Exception:
                    pass  # Loop may already be closed

            # Wait for server thread to finish (with timeout)
            if self._server_thread and self._server_thread.is_alive():
                import time
                timeout = 2.0
                start_time = time.time()
                while self._server_thread.is_alive() and (time.time() - start_time) < timeout:
                    time.sleep(0.1)

            self._running = False
            logger.info(f"HTTP adapter '{self.name}' stopped")
        except GeneratorExit:
            # GeneratorExit is expected during shutdown when lifespan generators are closed
            # This is not an error, just a normal part of the shutdown process
            logger.debug("GeneratorExit during shutdown (expected)")
            self._running = False
        except Exception as e:
            raise AdapterStopError(
                f"Failed to stop HTTP adapter '{self.name}': {e}"
            ) from e

