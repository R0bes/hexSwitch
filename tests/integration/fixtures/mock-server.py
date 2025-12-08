#!/usr/bin/env python3
"""Mock HTTP server for testing outbound HTTP calls."""

import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockHTTPHandler(BaseHTTPRequestHandler):
    """Mock HTTP request handler."""

    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "healthy", "service": "mock-server"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        """Handle POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode())
            logger.info(f"Mock server received: {data}")
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            response = {
                "status": "received",
                "service": "mock-server",
                "received_data": data,
            }
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.send_response(500)
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")


def run(port: int = 9090) -> None:
    """Run the mock HTTP server."""
    server_address = ("", port)
    httpd = HTTPServer(server_address, MockHTTPHandler)
    logger.info(f"Mock HTTP server starting on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Mock HTTP server stopping")
        httpd.shutdown()


if __name__ == "__main__":
    run()

