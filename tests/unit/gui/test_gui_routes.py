"""Unit tests for GUI routes."""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient
import pytest

from hexswitch.gui.routes import router
from hexswitch.gui.server import GuiServer


@pytest.fixture
def app():
    """Create FastAPI app with GUI routes."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestGuiRoutes:
    """Test GUI API routes."""

    def test_get_ports(self, client) -> None:
        """Test /api/ports endpoint."""
        response = client.get("/api/ports")
        assert response.status_code == 200
        data = response.json()
        assert "ports" in data
        assert isinstance(data["ports"], list)

    def test_get_handlers(self, client) -> None:
        """Test /api/handlers endpoint."""
        response = client.get("/api/handlers")
        assert response.status_code == 200
        data = response.json()
        assert "handlers" in data
        assert isinstance(data["handlers"], list)

    def test_get_adapters_no_runtime(self, client) -> None:
        """Test /api/adapters endpoint without runtime."""
        response = client.get("/api/adapters")
        assert response.status_code == 200
        data = response.json()
        assert "adapters" in data
        assert isinstance(data["adapters"], list)
        assert len(data["adapters"]) == 0

    def test_get_adapters_with_runtime(self, app, client) -> None:
        """Test /api/adapters endpoint with runtime."""
        # Create mock runtime
        mock_runtime = MagicMock()
        mock_inbound = MagicMock()
        mock_inbound.name = "http"
        mock_inbound._running = True
        mock_outbound = MagicMock()
        mock_outbound.name = "http_client"
        mock_outbound._connected = True
        mock_runtime.inbound_adapters = [mock_inbound]
        mock_runtime.outbound_adapters = [mock_outbound]

        # Set runtime in app state
        app.state.runtime = mock_runtime

        response = client.get("/api/adapters")
        assert response.status_code == 200
        data = response.json()
        assert "adapters" in data
        assert len(data["adapters"]) == 2

        # Check inbound adapter
        inbound_adapter = next(
            (a for a in data["adapters"] if a["type"] == "inbound"), None
        )
        assert inbound_adapter is not None
        assert inbound_adapter["name"] == "http"
        assert inbound_adapter["running"] is True

        # Check outbound adapter
        outbound_adapter = next(
            (a for a in data["adapters"] if a["type"] == "outbound"), None
        )
        assert outbound_adapter is not None
        assert outbound_adapter["name"] == "http_client"
        assert outbound_adapter["connected"] is True

    def test_get_metrics(self, client) -> None:
        """Test /api/metrics endpoint."""
        response = client.get("/api/metrics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_health(self, client) -> None:
        """Test /api/health endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data


class TestGuiServer:
    """Test GUI server."""

    def test_init_disabled(self) -> None:
        """Test GUI server initialization when disabled."""
        config = {"enabled": False, "port": 8080}
        server = GuiServer(config)
        assert not server.enabled
        assert server.port == 8080

    def test_init_enabled(self) -> None:
        """Test GUI server initialization when enabled."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)
        assert server.enabled
        assert server.port == 8080

    def test_init_default_port(self) -> None:
        """Test GUI server with default port."""
        config = {"enabled": True}
        server = GuiServer(config)
        assert server.port == 8080

    def test_create_app(self) -> None:
        """Test app creation."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)
        app = server._create_app()
        assert app is not None
        assert app.title == "HexSwitch GUI"

    def test_create_app_with_runtime(self) -> None:
        """Test app creation with runtime."""
        config = {"enabled": True, "port": 8080}
        mock_runtime = MagicMock()
        server = GuiServer(config, runtime=mock_runtime)
        app = server._create_app()
        assert app.state.runtime == mock_runtime

    def test_start_when_disabled(self) -> None:
        """Test start when disabled."""
        config = {"enabled": False, "port": 8080}
        server = GuiServer(config)
        server.start()  # Should not raise
        assert not server._running

    def test_stop_when_not_running(self) -> None:
        """Test stop when not running."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)
        server.stop()  # Should not raise
        assert not server._running

