#!/usr/bin/env python3
"""
hexSwitch API Server
Provides REST API for Visual Test Lab to interact with real hexSwitch runtime.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
from pathlib import Path
import sys
from urllib.parse import urlparse

# Add parent directory to path to import hexswitch
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from hexswitch.config import ConfigError, load_config, validate_config
    from hexswitch.runtime import Runtime, build_execution_plan
except ImportError as e:
    print(f"Error importing hexswitch: {e}", file=sys.stderr)
    print("Make sure hexSwitch is installed: pip install -e .", file=sys.stderr)
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HexSwitchAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for hexSwitch API."""

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/api/adapters":
            self._get_adapters()
        elif path == "/api/config":
            self._get_config()
        elif path == "/api/plan":
            self._get_execution_plan()
        else:
            self._send_response(404, {"error": "Not found"})

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/api/config/validate":
            self._validate_config()
        elif path == "/api/config/load":
            self._load_config()
        else:
            self._send_response(404, {"error": "Not found"})

    def _get_adapters(self):
        """Get list of available adapters."""
        # Import from the export script in the same directory
        import importlib.util

        export_script = Path(__file__).parent / "export_adapters.py"
        spec = importlib.util.spec_from_file_location("export_adapters", export_script)
        export_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(export_module)

        adapters = export_module.get_adapter_metadata()
        self._send_response(200, {"adapters": adapters})

    def _get_config(self):
        """Get current configuration."""
        config_path = Path(__file__).parent.parent.parent / "hex-config.yaml"
        try:
            config = load_config(config_path)
            self._send_response(200, {"config": config})
        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def _get_execution_plan(self):
        """Get execution plan from current config."""
        config_path = Path(__file__).parent.parent.parent / "hex-config.yaml"
        try:
            config = load_config(config_path)
            plan = build_execution_plan(config)
            self._send_response(200, {"plan": plan})
        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def _validate_config(self):
        """Validate configuration from request body."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode("utf-8"))
            config = data.get("config", {})

            validate_config(config)
            self._send_response(200, {"valid": True})
        except ConfigError as e:
            self._send_response(400, {"valid": False, "error": str(e)})
        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def _load_config(self):
        """Load configuration from file path in request body."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode("utf-8"))
            config_path = data.get("path", "hex-config.yaml")

            config = load_config(config_path)
            self._send_response(200, {"config": config})
        except Exception as e:
            self._send_response(500, {"error": str(e)})

    def _send_response(self, status_code, data):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        response = json.dumps(data).encode("utf-8")
        self.wfile.write(response)

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.debug(f"{self.address_string()} - {format % args}")


def main():
    """Main entry point."""
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    server = HTTPServer(("localhost", port), HexSwitchAPIHandler)
    logger.info(f"hexSwitch API server running on http://localhost:{port}")
    logger.info("Endpoints:")
    logger.info("  GET  /api/adapters - List available adapters")
    logger.info("  GET  /api/config - Get current configuration")
    logger.info("  GET  /api/plan - Get execution plan")
    logger.info("  POST /api/config/validate - Validate configuration")
    logger.info("  POST /api/config/load - Load configuration from file")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.shutdown()


if __name__ == "__main__":
    main()
