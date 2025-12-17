"""HTTP inbound adapter implementation."""

from http.server import BaseHTTPRequestHandler, HTTPServer
import importlib
import json
import logging
from threading import Thread
from typing import Any
from urllib.parse import parse_qs, urlparse

from hexswitch.adapters.base import InboundAdapter
from hexswitch.adapters.exceptions import AdapterStartError, AdapterStopError, HandlerError
from hexswitch.adapters.http._Http_Envelope import HttpEnvelope
from hexswitch.ports import PortError, get_port_registry
from hexswitch.shared.envelope import Envelope
from hexswitch.shared.helpers import parse_path_params

logger = logging.getLogger(__name__)


class HttpRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for HexSwitch routes."""

    def __init__(
        self,
        routes: list[dict[str, Any]],
        base_path: str,
        adapter: "HttpAdapterServer",
        *args: Any,
        **kwargs: Any,
    ):
        """Initialize HTTP request handler.

        Args:
            routes: List of route configurations.
            base_path: Base path prefix for all routes.
            adapter: Reference to HttpAdapterServer instance (for converter access).
            *args: Additional arguments for BaseHTTPRequestHandler.
            **kwargs: Additional keyword arguments for BaseHTTPRequestHandler.
        """
        self.routes = routes
        self.base_path = base_path.rstrip("/")
        self._adapter = adapter
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

        # Find matching route (support path parameters like /orders/:id)
        route = None
        import re

        for r in self.routes:
            if r["method"].upper() != method.upper():
                continue

            route_path = r["path"]
            # Exact match
            if route_path == request_path:
                route = r
                break

            # Check if route has path parameters (e.g., /orders/:id)
            if ":" in route_path:
                # Convert route pattern to regex for matching
                # Replace :param with regex group, but only for parameter names
                pattern = route_path
                # Find all :param patterns and replace them
                param_pattern = r":(\w+)"
                pattern = re.sub(param_pattern, r"([^/]+)", pattern)
                # Escape forward slashes for regex
                pattern = pattern.replace("/", r"\/")
                regex = re.compile(f"^{pattern}$")
                if regex.match(request_path):
                    route = r
                    break

        if not route:
            self._send_response(404, {"error": "Not Found"})
            return

        # Load handler or port
        try:
            # Support both "handler:" and "port:" in config
            if "port" in route:
                handler = get_port_registry().get_handler(route["port"])
            elif "handler" in route:
                handler_path = route["handler"]
                if ":" not in handler_path:
                    raise HandlerError(f"Invalid handler path format: {handler_path}. Expected format: 'module.path:function_name'")
                module_path, function_name = handler_path.rsplit(":", 1)
                if not module_path or not function_name:
                    raise HandlerError(f"Invalid handler path format: {handler_path}. Module path and function name must not be empty.")
                module = importlib.import_module(module_path)
                if not hasattr(module, function_name):
                    raise HandlerError(f"Module '{module_path}' does not have attribute '{function_name}'")
                handler = getattr(module, function_name)
                if not callable(handler):
                    raise HandlerError(f"'{function_name}' in module '{module_path}' is not callable")
            else:
                logger.error("Route must have either 'handler' or 'port' specified")
                self._send_response(500, {"error": "Internal Server Error", "message": "Route configuration error"})
                return
        except (HandlerError, PortError) as e:
            logger.error(f"Failed to load handler/port: {e}")
            self._send_response(500, {"error": "Internal Server Error", "message": str(e)})
            return

        # Convert HTTP Request → Envelope (Request) using converter
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        # Extract path parameters
        path_params = parse_path_params(request_path, route["path"])

        # Parse query parameters (convert from parse_qs format)
        normalized_query_params: dict[str, Any] = {}
        for key, value in query_params.items():
            if isinstance(value, list):
                normalized_query_params[key] = value[0] if len(value) == 1 else value
            else:
                normalized_query_params[key] = value

        # Use converter to create Envelope
        request_envelope = self._adapter.to_envelope(
            method=method,
            path=request_path,
            headers=dict(self.headers),
            query_params=normalized_query_params,
            body=body,
            path_params=path_params,
        )

        # Call handler/port with Envelope
        try:
            response_envelope = handler(request_envelope)
        except Exception as e:
            logger.exception(f"Handler/Port raised exception: {e}")
            response_envelope = Envelope.error(500, "Internal Server Error")

        # Convert Envelope (Response) → HTTP Response using converter
        self._send_envelope_response(response_envelope)

    def _send_envelope_response(self, envelope: Envelope) -> None:
        """Send Envelope as HTTP response.

        Args:
            envelope: Response envelope.
        """
        # Use converter to convert Envelope to HTTP response
        status_code, data, headers = self._adapter.from_envelope(envelope)

        # Send response with headers
        response_body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))

        # Add headers from converter
        for header_name, header_value in headers.items():
            self.send_header(header_name, header_value)

        self.end_headers()
        self.wfile.write(response_body)

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


class HttpAdapterServer(InboundAdapter):
    """HTTP inbound adapter for HexSwitch."""

    def __init__(self, name: str, config: dict[str, Any]):
        """Initialize HTTP adapter.

        Args:
            name: Adapter name.
            config: Adapter configuration dictionary.
        """
        self.name = name
        self.config = config
        self._running = False
        self._converter = HttpEnvelope()
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
                return HttpRequestHandler(self.routes, self.base_path, self, *args, **kwargs)

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

    def to_envelope(
        self,
        method: str,
        path: str,
        headers: dict[str, str],
        query_params: dict[str, Any],
        body: bytes | None,
        path_params: dict[str, str] | None = None,
    ) -> Envelope:
        """Convert HTTP request to Envelope.

        Args:
            method: HTTP method.
            path: Request path.
            headers: HTTP headers.
            query_params: Query parameters.
            body: Request body as bytes.
            path_params: Path parameters.

        Returns:
            Request envelope.
        """
        return self._converter.request_to_envelope(
            method=method,
            path=path,
            headers=headers,
            query_params=query_params,
            body=body,
            path_params=path_params,
        )

    def from_envelope(self, envelope: Envelope) -> tuple[int, dict[str, Any], dict[str, str]]:
        """Convert Envelope response to HTTP response.

        Args:
            envelope: Response envelope.

        Returns:
            Tuple of (status_code, data, headers).
        """
        return self._converter.envelope_to_response(envelope)

