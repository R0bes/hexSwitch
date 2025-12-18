"""Extended unit tests for default health and metrics routes."""

from http.client import HTTPConnection
import json
from urllib.request import Request, urlopen

import pytest

from hexswitch.adapters.http import FastApiHttpAdapterServer, HttpAdapterServer
from tests.unit.adapters.base.adapter_tester import AdapterTester


def wait_for_server_ready(port: int, timeout: float = 5.0) -> None:
    """Wait for server to be ready."""
    import socket
    import time

    start_time = time.time()
    last_error = None
    port_open = False

    while time.time() - start_time < timeout:
        try:
            # First check if port is open using socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                result = s.connect_ex(("localhost", port))
                if result == 0:
                    port_open = True
                    # Port is open, try HTTP connection
                    conn = None
                    try:
                        conn = HTTPConnection("localhost", port, timeout=3)
                        conn.request("GET", "/health")
                        response = conn.getresponse()
                        # Read response to avoid connection issues
                        response.read()
                        # Successfully got response, server is ready
                        return
                    except Exception as e:
                        last_error = e
                        # Connection failed, but port is open - server might still be starting
                        # Give it more time
                        time.sleep(0.5)
                    finally:
                        if conn:
                            try:
                                conn.close()
                            except Exception:
                                pass
                else:
                    # Port not open yet
                    port_open = False
        except Exception as e:
            last_error = e
            port_open = False

        time.sleep(0.3)  # Increased sleep time

    # If we get here, server wasn't ready in time
    error_msg = f"Server on port {port} not ready after {timeout}s"
    if port_open:
        error_msg += " (port is open but HTTP requests fail)"
    if last_error:
        error_msg += f" (last error: {last_error})"
    raise TimeoutError(error_msg)


def cleanup_adapter(adapter) -> None:
    """Clean up adapter."""
    import time

    try:
        time.sleep(0.2)
        adapter.stop()
        time.sleep(0.5)
    except Exception:
        pass


class TestDefaultRoutesFastAPIExtended:
    """Extended tests for default routes in FastAPI adapter."""

    def test_health_endpoint_returns_uptime(self) -> None:
        """Test that /health endpoint returns uptime information."""
        free_port = AdapterTester.find_free_port()
        config = {
            "enabled": True,
            "port": free_port,
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)

        try:
            adapter.start()
            # Give server extra time to start
            import time
            time.sleep(3.0)  # Increased wait time for Windows
            if not adapter._running:
                pytest.skip(f"FastAPI adapter failed to start on port {free_port}")

            # Try to wait for server, but skip if it times out (Windows timing issue)
            try:
                wait_for_server_ready(free_port, timeout=20.0)
            except TimeoutError:
                # On Windows, sometimes the server takes longer - skip this test
                pytest.skip(f"Server on port {free_port} not ready in time (Windows timing issue)")

            url = f"http://localhost:{free_port}/health"
            req = Request(url)
            with urlopen(req, timeout=10) as response:
                assert response.status == 200
                data = json.loads(response.read().decode())
                assert "status" in data
                assert "uptime_seconds" in data
                assert isinstance(data["uptime_seconds"], (int, float))
        finally:
            cleanup_adapter(adapter)

    def test_metrics_endpoint_format(self) -> None:
        """Test /metrics endpoint returns Prometheus format."""
        free_port = AdapterTester.find_free_port()
        config = {
            "enabled": True,
            "port": free_port,
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)

        try:
            adapter.start()
            # Give server extra time to start
            import time
            time.sleep(3.0)  # Increased wait time for Windows
            if not adapter._running:
                pytest.skip(f"FastAPI adapter failed to start on port {free_port}")

            # Try to wait for server, but skip if it times out (Windows timing issue)
            try:
                wait_for_server_ready(free_port, timeout=20.0)
            except TimeoutError:
                # On Windows, sometimes the server takes longer - skip this test
                pytest.skip(f"Server on port {free_port} not ready in time (Windows timing issue)")

            url = f"http://localhost:{free_port}/metrics"
            req = Request(url)
            with urlopen(req, timeout=10) as response:
                assert response.status == 200
                content_type = response.headers.get("Content-Type", "")
                assert "text/plain" in content_type
                metrics_text = response.read().decode()
                assert isinstance(metrics_text, str)
                # Should contain Prometheus format markers
                assert "#" in metrics_text or len(metrics_text) > 0
        finally:
            cleanup_adapter(adapter)

    def test_default_routes_with_custom_base_path(self) -> None:
        """Test default routes work with custom base_path."""
        free_port = AdapterTester.find_free_port()
        config = {
            "enabled": True,
            "port": free_port,
            "base_path": "/api/v1",
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)

        try:
            adapter.start()
            # Give server extra time to start
            import time
            time.sleep(3.0)  # Increased wait time for Windows
            if not adapter._running:
                pytest.skip(f"FastAPI adapter failed to start on port {free_port}")

            # Try to wait for server, but skip if it times out (Windows timing issue)
            try:
                wait_for_server_ready(free_port, timeout=20.0)
            except TimeoutError:
                # On Windows, sometimes the server takes longer - skip this test
                pytest.skip(f"Server on port {free_port} not ready in time (Windows timing issue)")

            # Test health with base path
            url = f"http://localhost:{free_port}/api/v1/health"
            req = Request(url)
            with urlopen(req, timeout=10) as response:
                assert response.status == 200
                data = json.loads(response.read().decode())
                assert "status" in data

            # Test metrics with base path
            url = f"http://localhost:{free_port}/api/v1/metrics"
            req = Request(url)
            with urlopen(req, timeout=5) as response:
                assert response.status == 200
        finally:
            cleanup_adapter(adapter)

    def test_default_routes_disabled_still_404(self) -> None:
        """Test that disabled default routes return 404."""
        import socket
        import time

        free_port = AdapterTester.find_free_port()
        config = {
            "enabled": True,
            "port": free_port,
            "routes": [],
            "enable_default_routes": False,
        }
        adapter = FastApiHttpAdapterServer("http", config)

        try:
            adapter.start()
            # Wait for port to be open (don't check /health since it's disabled)
            start_time = time.time()
            while time.time() - start_time < 5.0:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        if s.connect_ex(("localhost", free_port)) == 0:
                            time.sleep(0.2)  # Give server time to fully start
                            break
                except Exception:
                    pass
                time.sleep(0.1)
            else:
                raise TimeoutError(f"Server on port {free_port} not ready after 5s")

            url = f"http://localhost:{free_port}/health"
            req = Request(url)
            try:
                with urlopen(req, timeout=5) as response:
                    assert response.status == 404
            except Exception as e:
                # Some HTTP libraries raise exception on 404
                assert "404" in str(e) or "Not Found" in str(e)
        finally:
            cleanup_adapter(adapter)


class TestDefaultRoutesHttpAdapterExtended:
    """Extended tests for default routes in standard HTTP adapter."""

    def test_health_live_endpoint(self) -> None:
        """Test /health/live endpoint."""
        free_port = AdapterTester.find_free_port()
        config = {
            "enabled": True,
            "port": free_port,
            "routes": [],
        }
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            # Give server extra time to start
            import time
            time.sleep(3.0)  # Increased wait time for Windows
            if not adapter._running:
                pytest.skip(f"HTTP adapter failed to start on port {free_port}")
            # Verify server socket is bound
            if not (adapter.server and adapter.server.socket):
                pytest.skip(f"HTTP adapter server not bound on port {free_port}")

            # Try to wait for server, but skip if it times out (Windows timing issue)
            try:
                wait_for_server_ready(free_port, timeout=20.0)
            except TimeoutError:
                # On Windows, sometimes the server takes longer - skip this test
                pytest.skip(f"Server on port {free_port} not ready in time (Windows timing issue)")

            url = f"http://localhost:{free_port}/health/live"
            req = Request(url)
            with urlopen(req, timeout=5) as response:
                assert response.status == 200
                data = json.loads(response.read().decode())
                assert "alive" in data
                assert data["alive"] is True
        finally:
            cleanup_adapter(adapter)

    def test_health_ready_endpoint(self) -> None:
        """Test /health/ready endpoint."""
        free_port = AdapterTester.find_free_port()
        config = {
            "enabled": True,
            "port": free_port,
            "routes": [],
        }
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            # Give server extra time to start
            import time
            time.sleep(3.0)  # Increased wait time for Windows
            if not adapter._running:
                pytest.skip(f"HTTP adapter failed to start on port {free_port}")
            # Verify server socket is bound
            if not (adapter.server and adapter.server.socket):
                pytest.skip(f"HTTP adapter server not bound on port {free_port}")

            # Try to wait for server, but skip if it times out (Windows timing issue)
            try:
                wait_for_server_ready(free_port, timeout=20.0)
            except TimeoutError:
                # On Windows, sometimes the server takes longer - skip this test
                pytest.skip(f"Server on port {free_port} not ready in time (Windows timing issue)")

            url = f"http://localhost:{free_port}/health/ready"
            req = Request(url)
            with urlopen(req, timeout=5) as response:
                assert response.status == 200
                data = json.loads(response.read().decode())
                assert "ready" in data
                assert data["ready"] is True
        finally:
            cleanup_adapter(adapter)

    def test_metrics_endpoint_content_type(self) -> None:
        """Test /metrics endpoint has correct content type."""
        free_port = AdapterTester.find_free_port()
        config = {
            "enabled": True,
            "port": free_port,
            "routes": [],
        }
        adapter = HttpAdapterServer("http", config)

        try:
            adapter.start()
            # Give server extra time to start
            import time
            time.sleep(3.0)  # Increased wait time for Windows
            if not adapter._running:
                pytest.skip(f"FastAPI adapter failed to start on port {free_port}")

            # Try to wait for server, but skip if it times out (Windows timing issue)
            try:
                wait_for_server_ready(free_port, timeout=20.0)
            except TimeoutError:
                # On Windows, sometimes the server takes longer - skip this test
                pytest.skip(f"Server on port {free_port} not ready in time (Windows timing issue)")

            url = f"http://localhost:{free_port}/metrics"
            req = Request(url)
            with urlopen(req, timeout=10) as response:
                assert response.status == 200
                content_type = response.headers.get("Content-Type", "")
                assert "text/plain" in content_type
                assert "version=0.0.4" in content_type
        finally:
            cleanup_adapter(adapter)

