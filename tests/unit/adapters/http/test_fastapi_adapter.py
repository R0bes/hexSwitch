"""Unit tests for FastAPI HTTP adapter."""

from unittest.mock import MagicMock, patch

import pytest

from hexswitch.adapters.exceptions import AdapterStartError, AdapterStopError, HandlerError
from hexswitch.adapters.http.fastapi_adapter import FastApiHttpAdapterServer
from hexswitch.ports import PortError


class TestFastApiHttpAdapterServer:
    """Test FastAPI HTTP adapter."""

    def test_init_basic(self) -> None:
        """Test basic initialization."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        assert adapter.name == "http"
        assert adapter.port == 8000
        assert adapter.base_path == ""
        assert adapter.routes == []

    def test_init_with_base_path(self) -> None:
        """Test initialization with base_path."""
        config = {
            "enabled": True,
            "port": 8000,
            "base_path": "/api",
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        assert adapter.base_path == "/api"

    def test_init_with_routes(self) -> None:
        """Test initialization with routes."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "handler": "test_module:handler",
                }
            ],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        assert len(adapter.routes) == 1

    def test_init_default_port(self) -> None:
        """Test initialization with default port."""
        config = {
            "enabled": True,
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        assert adapter.port == 8000

    def test_init_disable_default_routes(self) -> None:
        """Test initialization with default routes disabled."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
            "enable_default_routes": False,
        }
        adapter = FastApiHttpAdapterServer("http", config)
        assert adapter.enable_default_routes is False

    def test_setup_default_routes_disabled(self) -> None:
        """Test setup default routes when disabled."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
            "enable_default_routes": False,
        }
        adapter = FastApiHttpAdapterServer("http", config)
        # Should not raise
        assert adapter.enable_default_routes is False

    @patch("hexswitch.adapters.http.fastapi_adapter.get_port_registry")
    def test_setup_routes_with_handler(self, mock_registry) -> None:
        """Test setup routes with handler path."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "handler": "test_module:handler",
                }
            ],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        # Should not raise
        assert len(adapter.routes) == 1

    @patch("hexswitch.adapters.http.fastapi_adapter.get_port_registry")
    def test_setup_routes_with_port(self, mock_registry) -> None:
        """Test setup routes with port name."""
        mock_reg = MagicMock()
        mock_registry.return_value = mock_reg
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "port": "test_port",
                }
            ],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        # Should not raise
        assert len(adapter.routes) == 1

    @patch("hexswitch.adapters.http.fastapi_adapter.get_port_registry")
    def test_setup_routes_with_base_path(self, mock_registry) -> None:
        """Test setup routes with base_path."""
        config = {
            "enabled": True,
            "port": 8000,
            "base_path": "/api",
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "handler": "test_module:handler",
                }
            ],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        # Should not raise
        assert adapter.base_path == "/api"

    def test_start_already_running(self) -> None:
        """Test start when already running."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        adapter._running = True

        # Should not raise, just log warning
        adapter.start()

    @patch("hexswitch.adapters.http.fastapi_adapter.uvicorn")
    def test_start_success(self, mock_uvicorn) -> None:
        """Test successful start."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)

        mock_server = MagicMock()
        mock_config = MagicMock()
        mock_uvicorn.Config.return_value = mock_config
        mock_uvicorn.Server.return_value = mock_server

        # Mock event loop
        with patch("hexswitch.adapters.http.fastapi_adapter.asyncio") as mock_asyncio:
            mock_loop = MagicMock()
            mock_loop.create_task.return_value = MagicMock()
            mock_asyncio.new_event_loop.return_value = mock_loop
            mock_asyncio.set_event_loop = MagicMock()

            with patch("hexswitch.adapters.http.fastapi_adapter.threading") as mock_threading:
                mock_thread = MagicMock()
                mock_threading.Thread.return_value = mock_thread

                adapter.start()

                assert adapter._running is True
                assert adapter._server == mock_server

    @patch("hexswitch.adapters.http.fastapi_adapter.uvicorn")
    def test_start_failure(self, mock_uvicorn) -> None:
        """Test start failure."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)

        mock_uvicorn.Config.side_effect = Exception("Config error")

        with pytest.raises(AdapterStartError):
            adapter.start()

    def test_stop_not_running(self) -> None:
        """Test stop when not running."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        adapter._running = False

        # Should not raise, just log warning
        adapter.stop()

    def test_stop_success(self) -> None:
        """Test successful stop."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        adapter._running = True

        # Mock server and loop
        mock_server = MagicMock()
        adapter._server = mock_server

        mock_task = MagicMock()
        mock_task.done.return_value = False
        adapter._server_task = mock_task

        mock_loop = MagicMock()
        mock_loop.is_running.return_value = False
        adapter._server_loop = mock_loop

        mock_thread = MagicMock()
        mock_thread.is_alive.return_value = False
        adapter._server_thread = mock_thread

        adapter.stop()

        assert adapter._running is False
        assert mock_server.should_exit is True

    def test_stop_with_generator_exit(self) -> None:
        """Test stop with GeneratorExit exception."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        adapter._running = True

        mock_server = MagicMock()
        adapter._server = mock_server

        # Mock to raise GeneratorExit
        mock_task = MagicMock()
        mock_task.done.side_effect = GeneratorExit()
        adapter._server_task = mock_task

        # Should handle GeneratorExit gracefully
        adapter.stop()
        assert adapter._running is False

    def test_stop_with_exception(self) -> None:
        """Test stop with exception."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        adapter._running = True

        mock_server = MagicMock()
        # Make setting should_exit raise an exception
        def set_should_exit(value):
            raise PropertyError("Cannot set should_exit")
        type(mock_server).should_exit = property(lambda self: None, set_should_exit)
        adapter._server = mock_server

        with pytest.raises(AdapterStopError):
            adapter.stop()

    @patch("hexswitch.adapters.http.fastapi_adapter.get_port_registry")
    @patch("hexswitch.adapters.http.fastapi_adapter.importlib")
    def test_route_handler_invalid_handler_format(self, mock_importlib, mock_registry) -> None:
        """Test route handler with invalid handler format."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "handler": "invalid_format",  # Missing colon
                }
            ],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        # Route should be set up, but handler will return error when called
        assert len(adapter.routes) == 1

    @patch("hexswitch.adapters.http.fastapi_adapter.get_port_registry")
    def test_route_handler_no_handler_or_port(self, mock_registry) -> None:
        """Test route handler with no handler or port."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    # Missing both handler and port
                }
            ],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        # Route should be set up, but handler will return error when called
        assert len(adapter.routes) == 1

    @patch("hexswitch.adapters.http.fastapi_adapter.get_port_registry")
    def test_route_handler_port_error(self, mock_registry) -> None:
        """Test route handler with port error."""
        mock_reg = MagicMock()
        mock_registry.return_value = mock_reg
        mock_reg.get_handler.side_effect = PortError("Port not found")

        config = {
            "enabled": True,
            "port": 8000,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "port": "nonexistent_port",
                }
            ],
        }
        adapter = FastApiHttpAdapterServer("http", config)
        # Route should be set up, but handler will return error when called
        assert len(adapter.routes) == 1

    @patch("hexswitch.adapters.http.fastapi_adapter.get_port_registry")
    def test_route_handler_handler_error(self, mock_registry) -> None:
        """Test route handler with handler error."""
        mock_reg = MagicMock()
        mock_registry.return_value = mock_reg

        config = {
            "enabled": True,
            "port": 8000,
            "routes": [
                {
                    "path": "/test",
                    "method": "GET",
                    "handler": "test_module:handler",
                }
            ],
        }

        with patch("hexswitch.adapters.http.fastapi_adapter.importlib") as mock_importlib:
            mock_module = MagicMock()
            mock_importlib.import_module.return_value = mock_module
            mock_module.handler = MagicMock(side_effect=HandlerError("Handler error"))

            adapter = FastApiHttpAdapterServer("http", config)
            # Route should be set up
            assert len(adapter.routes) == 1

    def test_setup_default_routes_import_error(self) -> None:
        """Test setup default routes with import error."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
            "enable_default_routes": True,
        }

        with patch("hexswitch.adapters.http.fastapi_adapter.get_port_registry") as mock_registry:
            mock_reg = MagicMock()
            mock_registry.return_value = mock_reg
            mock_reg.get_handler.side_effect = ImportError("Module not found")

            adapter = FastApiHttpAdapterServer("http", config)
            # Should not raise, just log warning
            assert adapter.enable_default_routes is True

    def test_setup_default_routes_exception(self) -> None:
        """Test setup default routes with exception."""
        config = {
            "enabled": True,
            "port": 8000,
            "routes": [],
            "enable_default_routes": True,
        }

        with patch("hexswitch.adapters.http.fastapi_adapter.get_port_registry") as mock_registry:
            mock_reg = MagicMock()
            mock_registry.return_value = mock_reg
            mock_reg.get_handler.side_effect = Exception("Unexpected error")

            adapter = FastApiHttpAdapterServer("http", config)
            # Should not raise, just log warning
            assert adapter.enable_default_routes is True


class PropertyError(Exception):
    """Test exception for property access."""

