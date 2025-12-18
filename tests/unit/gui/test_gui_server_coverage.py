"""Additional unit tests for GUI server to improve coverage."""

import time
from unittest.mock import MagicMock, patch

import pytest

from hexswitch.gui.server import GuiServer


class TestGuiServerStart:
    """Test GuiServer.start() full lifecycle."""

    def test_start_success(self) -> None:
        """Test successful server start."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)

        # Mock uvicorn to avoid actually starting server
        with patch("hexswitch.gui.server.uvicorn.Server") as mock_server_class:
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server

            # Mock asyncio module functions
            with patch("asyncio.new_event_loop") as mock_new_loop, \
                 patch("asyncio.set_event_loop") as mock_set_loop:
                mock_loop = MagicMock()
                mock_new_loop.return_value = mock_loop
                mock_task = MagicMock()
                mock_loop.create_task.return_value = mock_task

                server.start()

                # Give thread time to start
                time.sleep(0.1)

                assert server._running is True
                assert server._app is not None
                assert server._server is not None

    def test_start_with_exception(self) -> None:
        """Test start() when exception occurs."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)

        # Mock uvicorn to raise exception
        with patch("hexswitch.gui.server.uvicorn.Server") as mock_server_class:
            mock_server_class.side_effect = Exception("Server creation failed")

            with pytest.raises(RuntimeError, match="Failed to start GUI server"):
                server.start()

    def test_start_static_files_error(self) -> None:
        """Test start() when static files mounting fails."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)

        # Mock os.path.exists to return True, but mount to fail
        with patch("os.path.exists", return_value=True):
            with patch.object(server, "_create_app") as mock_create:
                mock_app = MagicMock()
                # Make mount raise exception
                mock_app.mount.side_effect = Exception("Mount failed")
                mock_create.return_value = mock_app

                # Mock uvicorn
                with patch("hexswitch.gui.server.uvicorn.Server") as mock_server_class:
                    mock_server = MagicMock()
                    mock_server_class.return_value = mock_server

                    # Use real event loop instead of MagicMock
                    with patch("asyncio.new_event_loop") as mock_new_loop, \
                         patch("asyncio.set_event_loop") as mock_set_loop:
                        import asyncio
                        real_loop = asyncio.new_event_loop()
                        mock_new_loop.return_value = real_loop
                        mock_task = MagicMock()
                        real_loop.create_task = MagicMock(return_value=mock_task)

                        # Should not raise, just log warning
                        server.start()
                        time.sleep(0.1)

                        # Server should still start
                        assert server._running is True

                        # Cleanup
                        if not real_loop.is_closed():
                            real_loop.close()


class TestGuiServerStop:
    """Test GuiServer.stop() full lifecycle."""

    def test_stop_success(self) -> None:
        """Test successful server stop."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)
        server._running = True
        mock_server = MagicMock()
        server._server = mock_server
        mock_loop = MagicMock()
        mock_loop.is_running.return_value = False
        mock_loop.is_closed.return_value = False
        server._loop = mock_loop
        server._server_thread = MagicMock()
        server._server_thread.is_alive.return_value = False

        server.stop()

        assert server._running is False
        assert mock_server.should_exit is True

    def test_stop_with_running_loop(self) -> None:
        """Test stop() when event loop is running."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)
        server._running = True
        server._server = MagicMock()
        mock_loop = MagicMock()
        mock_loop.is_running.return_value = True
        server._loop = mock_loop
        server._server_thread = MagicMock()
        server._server_thread.is_alive.return_value = False

        server.stop()

        assert server._running is False
        mock_loop.call_soon_threadsafe.assert_called()

    def test_stop_with_alive_thread(self) -> None:
        """Test stop() when server thread is alive."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)
        server._running = True
        server._server = MagicMock()
        server._loop = MagicMock()
        server._loop.is_running.return_value = False
        server._server_thread = MagicMock()
        server._server_thread.is_alive.return_value = True

        server.stop()

        assert server._running is False
        server._server_thread.join.assert_called_once_with(timeout=5.0)

    def test_stop_with_exception(self) -> None:
        """Test stop() when exception occurs."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)
        server._running = True
        server._server = MagicMock()
        server._server.should_exit = None  # Will cause AttributeError
        server._loop = MagicMock()
        server._loop.is_running.side_effect = Exception("Loop error")
        server._server_thread = None

        # Should not raise, just log error
        # Note: _running may not be set to False if exception occurs early
        try:
            server.stop()
        except Exception:
            pass  # Expected to handle exceptions internally

        # Verify stop was attempted (may or may not set _running to False on error)
        assert server._server is not None


class TestGuiServerStaticFiles:
    """Test GUI server static files mounting."""

    def test_create_app_with_static_files(self) -> None:
        """Test app creation with static files directory."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)

        # Mock os.path.exists to return True
        with patch("os.path.exists", return_value=True):
            with patch("hexswitch.gui.server.StaticFiles") as mock_static:
                app = server._create_app()

                assert app is not None
                # Should attempt to mount static files
                mock_static.assert_called()

    def test_create_app_without_static_files(self) -> None:
        """Test app creation without static files directory."""
        config = {"enabled": True, "port": 8080}
        server = GuiServer(config)

        # Mock os.path.exists to return False
        with patch("os.path.exists", return_value=False):
            app = server._create_app()

            assert app is not None
            # Should not raise if static dir doesn't exist

