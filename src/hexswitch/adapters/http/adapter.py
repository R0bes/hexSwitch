"""HTTP inbound adapter implementation."""

import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any
from urllib.parse import parse_qs, urlparse

from hexswitch.adapters.base import InboundAdapter
from hexswitch.adapters.exceptions import AdapterStartError, AdapterStopError
from hexswitch.handlers import HandlerError, load_handler

logger = logging.getLogger(__name__)


class HttpRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for HexSwitch routes."""

    def __init__(
        self,
        routes: list[dict[str, Any]],
        base_path: str,
        *args: Any,
        **kwargs: Any,
    ):
        """Initialize HTTP request handler.

        Args:
            routes: List of route configurations.
            base_path: Base path prefix for all routes.
            *args: Additional arguments for BaseHTTPRequestHandler.
            **kwargs: Additional keyword arguments for BaseHTTPRequestHandler.
        """
        self.routes = routes
        self.base_path = base_path.rstrip("/")
        super().__init__(*args, **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        """Override to use our logger instead of stderr."""
        logger.debug(f"{self.address_string()} - {format % args}")

    def do_GET(self) -> None:
        """Handle GET requests."""
        self._handle_request("GET")

    def do_POST(self) -> None:
        """Handle POST requests."""
        self._handle_request("POST")

    def do_PUT(self) -> None:
        """Handle PUT requests."""
        self._handle_request("PUT")

    def do_DELETE(self) -> None:
        """Handle DELETE requests."""
        self._handle_request("DELETE")

    def do_PATCH(self) -> None:
        """Handle PATCH requests."""
        self._handle_request("PATCH")

    def _handle_request(self, method: str) -> None:
        """Handle HTTP request by routing to appropriate handler.

        Args:
            method: HTTP method.
        """
        parsed_url = urlparse(self.path)
        request_path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        # Remove base_path prefix if present
        if self.base_path and request_path.startswith(self.base_path):
            request_path = request_path[len(self.base_path) :]

        # Find matching route
        route = None
        for r in self.routes:
            if r["path"] == request_path and r["method"].upper() == method.upper():
                route = r
                break

        if not route:
            self._send_response(404, {"error": "Not Found"})
            return

        # Load and call handler
        try:
            handler = load_handler(route["handler"])
        except HandlerError as e:
            logger.error(f"Failed to load handler '{route['handler']}': {e}")
            self._send_response(500, {"error": "Internal Server Error", "message": str(e)})
            return

        # Prepare request data
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        request_data = {
            "method": method,
            "path": request_path,
            "query_params": {k: v[0] if len(v) == 1 else v for k, v in query_params.items()},
            "headers": dict(self.headers),
            "body": body.decode("utf-8") if body else None,
        }

        # Call handler
        try:
            response = handler(request_data)
        except Exception as e:
            logger.exception(f"Handler '{route['handler']}' raised exception: {e}")
            self._send_response(500, {"error": "Internal Server Error", "message": str(e)})
            return

        # Send response
        if isinstance(response, dict):
            self._send_response(200, response)
        elif isinstance(response, tuple) and len(response) == 2:
            status_code, data = response
            self._send_response(status_code, data)
        else:
            self._send_response(200, {"result": str(response)})

    def _send_response(self, status_code: int, data: dict[str, Any]) -> None:
        """Send JSON response.

        Args:
            status_code: HTTP status code.
            data: Response data dictionary.
        """
        response_body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)


class HttpAdapter(InboundAdapter):
    """HTTP inbound adapter for HexSwitch."""

    def __init__(self, name: str, config: dict[str, Any]):
        """Initialize HTTP adapter.

        Args:
            name: Adapter name.
            config: Adapter configuration dictionary.
        """
        super().__init__(name, config)
        self.server: HTTPServer | None = None
        self.server_thread: Thread | None = None
        self.port = config.get("port", 8000)
        self.base_path = config.get("base_path", "")
        self.routes = config.get("routes", [])

    def start(self) -> None:
        """Start the HTTP server.

        Raises:
            AdapterStartError: If the server fails to start.
        """
        if self._running:
            logger.warning(f"HTTP adapter '{self.name}' is already running")
            return

        try:
            # Create request handler factory
            def handler_factory(*args: Any, **kwargs: Any) -> HttpRequestHandler:
                return HttpRequestHandler(self.routes, self.base_path, *args, **kwargs)

            # Create and start server
            self.server = HTTPServer(("", self.port), handler_factory)
            self.server_thread = Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            self._running = True

            logger.info(
                f"HTTP adapter '{self.name}' started on port {self.port} "
                f"with base_path '{self.base_path}'"
            )
        except Exception as e:
            raise AdapterStartError(f"Failed to start HTTP adapter '{self.name}': {e}") from e

    def stop(self) -> None:
        """Stop the HTTP server.

        Raises:
            AdapterStopError: If the server fails to stop.
        """
        if not self._running:
            logger.warning(f"HTTP adapter '{self.name}' is not running")
            return

        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            if self.server_thread:
                self.server_thread.join(timeout=5.0)
            self._running = False
            logger.info(f"HTTP adapter '{self.name}' stopped")
        except Exception as e:
            raise AdapterStopError(f"Failed to stop HTTP adapter '{self.name}': {e}") from e

