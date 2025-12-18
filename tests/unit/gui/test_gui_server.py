"""Unit tests for GUI server."""

from unittest.mock import MagicMock, patch

import pytest

from hexswitch.gui.server import GuiServer


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

    def test_start_already_running(self) -> None:
        """Test start when already running."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)
        server._running = True
        server.start()  # Should not raise, just return

    def test_stop_already_stopped(self) -> None:
        """Test stop when already stopped."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)
        server._running = False
        server.stop()  # Should not raise

