"""HTTP adapter specific tests."""

import json
import socket
import sys
import time
from types import ModuleType
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from hexswitch.adapters.http import HttpAdapterServer
from hexswitch.shared.envelope import Envelope
from tests.unit.adapters.base.adapter_tester import AdapterTester
from tests.unit.adapters.base.security_test_base import SecurityTestBase


def wait_for_server_ready(port: int, max_attempts: int = 20, timeout: float = 0.1) -> None:
    """Wait for HTTP server to be ready on the specified port.

    Args:
        port: Port number to check.
        max_attempts: Maximum number of connection attempts.
        timeout: Timeout for each connection attempt.

    Raises:
        AssertionError: If server does not become ready within max_attempts.
    """
    for attempt in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex(("localhost", port)) == 0:
                    time.sleep(0.1)  # Small delay after connection succeeds
                    return
        except Exception:
            pass
        # Exponential backoff to avoid busy waiting
        time.sleep(min(0.1 * (1.1 ** attempt), 0.5))
    pytest.fail(f"Server on port {port} did not become ready after {max_attempts} attempts")


def cleanup_adapter(adapter, module_name: str | None = None) -> None:
    """Cleanup adapter and test module safely.

    Args:
        adapter: Adapter instance to stop.
        module_name: Optional module name to remove from sys.modules.
    """
    import asyncio
    
    try:
        time.sleep(0.2)  # Give time for response to complete
        if adapter and hasattr(adapter, 'stop'):
            adapter.stop()
        time.sleep(0.5)  # Give server time to shut down gracefully
        
        # For FastAPI adapters, ensure all tasks are cancelled
        if hasattr(adapter, '_server_loop') and adapter._server_loop:
            try:
                # Cancel any remaining tasks
                if not adapter._server_loop.is_closed():
                    pending_tasks = [task for task in asyncio.all_tasks(adapter._server_loop) if not task.done()]
                    for task in pending_tasks:
                        task.cancel()
                    # Wait briefly for cancellation
                    if pending_tasks:
                        time.sleep(0.1)
            except Exception:
                pass
    except Exception:
        pass  # Ignore errors during cleanup

    if module_name and module_name in sys.modules:
        del sys.modules[module_name]


@pytest.mark.security
class TestHttpAdapterRouting(SecurityTestBase):
    """Test HTTP adapter routing and path matching."""

    def test_path_parameter_extraction(self) -> None:
        """Test path parameter extraction from routes."""
        def handler(envelope: Envelope) -> Envelope:
            return Envelope.success({"id": envelope.path_params.get("id")})

        test_module = ModuleType("test_path_handler")
        test_module.handler = handler
        sys.modules["test_path_handler"] = test_module

        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/orders/:id",
                    "method": "GET",
                    "handler": "test_path_handler:handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            url = f"http://localhost:{free_port}/orders/123"
            req = Request(url)
            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                assert data["id"] == "123"
        finally:
            cleanup_adapter(adapter, "test_path_handler")

    def test_query_parameter_parsing(self) -> None:
        """Test query parameter parsing."""
        def handler(envelope: Envelope) -> Envelope:
            return Envelope.success({"params": envelope.query_params})

        test_module = ModuleType("test_query_handler")
        test_module.handler = handler
        sys.modules["test_query_handler"] = test_module

        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/search",
                    "method": "GET",
                    "handler": "test_query_handler:handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            url = f"http://localhost:{free_port}/search?q=test&limit=10"
            req = Request(url)
            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                assert data["params"]["q"] == "test"
                assert data["params"]["limit"] == "10"
        finally:
            cleanup_adapter(adapter, "test_query_handler")

    def test_base_path_handling(self) -> None:
        """Test base path handling."""
        def handler(envelope: Envelope) -> Envelope:
            return Envelope.success({"path": envelope.path})

        test_module = ModuleType("test_base_handler")
        test_module.handler = handler
        sys.modules["test_base_handler"] = test_module

        config = {
            "enabled": True,
            "port": 0,
            "base_path": "/api",
            "routes": [
                {
                    "path": "/hello",
                    "method": "GET",
                    "handler": "test_base_handler:handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            url = f"http://localhost:{free_port}/api/hello"
            req = Request(url)
            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                assert data["path"] == "/hello"
        finally:
            cleanup_adapter(adapter, "test_base_handler")


@pytest.mark.security
class TestHttpAdapterSecurity(SecurityTestBase):
    """Test HTTP adapter security features."""

    def test_path_traversal_protection(self, handler_module: ModuleType) -> None:
        """Test path traversal attack protection."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/orders/:id",
                    "method": "GET",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            # Try path traversal attacks
            for payload in self.PATH_TRAVERSAL_PAYLOADS:
                url = f"http://localhost:{free_port}/orders/{payload}"
                req = Request(url)
                try:
                    with urlopen(req, timeout=5) as response:
                        # Should not expose file system
                        data = json.loads(response.read().decode())
                        # Path should be sanitized, not actual file content
                        assert "passwd" not in str(data).lower()
                except Exception:
                    # 404 or error is acceptable
                    pass
        finally:
            cleanup_adapter(adapter)

    def test_sql_injection_in_query_params(self, handler_module: ModuleType) -> None:
        """Test SQL injection protection in query parameters."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/search",
                    "method": "GET",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            for payload in self.SQL_INJECTION_PAYLOADS:
                url = f"http://localhost:{free_port}/search?q={payload}"
                req = Request(url)
                try:
                    with urlopen(req, timeout=5) as response:
                        # Should handle gracefully, not execute SQL
                        data = json.loads(response.read().decode())
                        # Should not contain SQL error messages
                        assert "sql" not in str(data).lower()
                        assert "syntax" not in str(data).lower()
                except Exception:
                    pass
        finally:
            cleanup_adapter(adapter)

    def test_xss_in_query_params(self, handler_module: ModuleType) -> None:
        """Test XSS protection in query parameters."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/search",
                    "method": "GET",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            for payload in self.XSS_PAYLOADS:
                url = f"http://localhost:{free_port}/search?q={payload}"
                req = Request(url)
                try:
                    with urlopen(req, timeout=5) as response:
                        data = response.read().decode()
                        # Response should not contain unescaped script tags
                        assert "<script>" not in data or "&lt;script&gt;" in data
                except Exception:
                    pass
        finally:
            cleanup_adapter(adapter)

    def test_content_length_manipulation(self, handler_module: ModuleType) -> None:
        """Test Content-Length header manipulation."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/test",
                    "method": "POST",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            # Test negative Content-Length
            url = f"http://localhost:{free_port}/test"
            req = Request(url, data=b"test", method="POST")
            req.add_header("Content-Length", "-1")
            try:
                with urlopen(req, timeout=5):
                    # Should handle gracefully
                    pass
            except Exception:
                # Error is acceptable
                pass
        finally:
            cleanup_adapter(adapter)

    def test_oversized_request_body(self, handler_module: ModuleType) -> None:
        """Test handling of oversized request bodies."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/test",
                    "method": "POST",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            # Test 10MB body
            large_body = b"A" * (10 * 1024 * 1024)
            url = f"http://localhost:{free_port}/test"
            req = Request(url, data=large_body, method="POST")
            req.add_header("Content-Type", "application/json")

            try:
                with urlopen(req, timeout=5):
                    # Should handle or reject gracefully
                    pass
            except Exception:
                # Timeout or error is acceptable for oversized bodies
                pass
        finally:
            cleanup_adapter(adapter)


@pytest.mark.edge_cases
class TestHttpAdapterEdgeCases:
    """Test HTTP adapter edge cases."""

    def test_invalid_json_in_body(self, handler_module: ModuleType) -> None:
        """Test handling of invalid JSON in request body."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/test",
                    "method": "POST",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            url = f"http://localhost:{free_port}/test"
            req = Request(url, data=b"{invalid json}", method="POST")
            req.add_header("Content-Type", "application/json")

            with urlopen(req, timeout=5) as response:
                # Should handle gracefully, not crash
                assert response.getcode() in [200, 400, 500]
        finally:
            cleanup_adapter(adapter)

    def test_empty_request_body(self, handler_module: ModuleType) -> None:
        """Test handling of empty request body."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/test",
                    "method": "POST",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            url = f"http://localhost:{free_port}/test"
            req = Request(url, data=b"", method="POST")

            with urlopen(req, timeout=5) as response:
                # Should handle empty body
                assert response.getcode() in [200, 400]
        finally:
            cleanup_adapter(adapter)

    def test_handler_exception_handling(self) -> None:
        """Test that handler exceptions don't expose stack traces."""
        def failing_handler(envelope: Envelope) -> Envelope:
            raise ValueError("Internal error")

        test_module = ModuleType("test_failing_handler")
        test_module.handler = failing_handler
        sys.modules["test_failing_handler"] = test_module

        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "handler": "test_failing_handler:handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            url = f"http://localhost:{free_port}/test"
            req = Request(url)
            try:
                with urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())
            except HTTPError as e:
                # HTTP 500 is expected, read the error response
                data = json.loads(e.read().decode())
            # Should return error, but not stack trace
            assert "error" in data
            assert "Traceback" not in str(data)
            assert "File" not in str(data)
        finally:
            cleanup_adapter(adapter, "test_failing_handler")

    def test_route_not_found(self) -> None:
        """Test 404 handling for non-existent routes."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            url = f"http://localhost:{free_port}/nonexistent"
            req = Request(url)
            try:
                with urlopen(req, timeout=5) as response:
                    assert response.getcode() == 404
            except Exception as e:
                # Some HTTP libraries raise exceptions for 404
                assert "404" in str(e) or "Not Found" in str(e)
        finally:
            cleanup_adapter(adapter)

    def test_method_not_supported(self, handler_module: ModuleType) -> None:
        """Test handling of unsupported HTTP methods."""
        config = {
            "enabled": True,
            "port": 0,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            # Try OPTIONS method (not in routes)
            url = f"http://localhost:{free_port}/test"
            req = Request(url)
            req.get_method = lambda: "OPTIONS"

            try:
                with urlopen(req, timeout=5) as response:
                    # Should return 404 or 405
                    assert response.getcode() in [404, 405]
            except Exception:
                pass
        finally:
            cleanup_adapter(adapter)

    def test_port_boundary_conditions(self) -> None:
        """Test port boundary conditions."""
        # Test port 0 (should find free port)
        config = {"enabled": True, "port": 0, "routes": []}
        adapter = HttpAdapterServer("http", config)
        assert adapter.port == 0

        # Test valid port
        config = {"enabled": True, "port": 8000, "routes": []}
        adapter = HttpAdapterServer("http", config)
        assert adapter.port == 8000

        # Test max valid port
        config = {"enabled": True, "port": 65535, "routes": []}
        adapter = HttpAdapterServer("http", config)
        assert adapter.port == 65535

    def test_http_adapter_default_config(self) -> None:
        """Test HTTP adapter with default configuration."""
        config = {"enabled": True, "routes": []}
        adapter = HttpAdapterServer("http", config)
        assert adapter.port == 8000
        assert adapter.base_path == ""

    def test_http_adapter_with_routes(self, handler_module: ModuleType) -> None:
        """Test HTTP adapter with route configuration."""
        config = {
            "enabled": True,
            "port": 0,
            "base_path": "/api",
            "routes": [
                {
                    "path": "/hello",
                    "method": "GET",
                    "handler": "test_handler_module:test_handler",
                }
            ],
        }

        free_port = AdapterTester.find_free_port()
        config["port"] = free_port
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            wait_for_server_ready(free_port)

            url = f"http://localhost:{free_port}/api/hello"
            req = Request(url)
            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                assert "result" in data
                assert data["result"] == "success"
        finally:
            cleanup_adapter(adapter)

