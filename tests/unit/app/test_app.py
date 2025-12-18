"""Unit tests for HexSwitch CLI application."""

import argparse
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

from hexswitch.app import cmd_init, cmd_run, cmd_validate, cmd_version, main
from hexswitch.shared.config.config import ConfigError


class TestCmdValidate:
    """Test cmd_validate function."""

    def test_validate_valid_config(self) -> None:
        """Test validating a valid config file."""
        config_content = """
service:
  name: test-service
inbound:
  http:
    enabled: true
    port: 8000
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            config_path = f.name

        try:
            args = argparse.Namespace(config=config_path)
            result = cmd_validate(args)
            assert result == 0
        finally:
            Path(config_path).unlink()

    def test_validate_invalid_config(self) -> None:
        """Test validating an invalid config file."""
        config_content = """
service:
  name: test-service
inbound:
  http:
    enabled: true
    port: 70000  # Invalid port
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(config_content)
            config_path = f.name

        try:
            args = argparse.Namespace(config=config_path)
            result = cmd_validate(args)
            assert result == 1
        finally:
            Path(config_path).unlink()

    def test_validate_missing_file(self) -> None:
        """Test validating a non-existent config file."""
        args = argparse.Namespace(config="/nonexistent/path/config.yaml")
        result = cmd_validate(args)
        assert result == 1

    def test_validate_invalid_yaml(self) -> None:
        """Test validating a file with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name

        try:
            args = argparse.Namespace(config=config_path)
            result = cmd_validate(args)
            assert result == 1
        finally:
            Path(config_path).unlink()


class TestCmdRun:
    """Test cmd_run function."""

    @patch("hexswitch.app.Runtime")
    @patch("hexswitch.app.validate_config")
    @patch("hexswitch.app.load_config")
    def test_run_valid_config(
        self, mock_load: MagicMock, mock_validate: MagicMock, mock_runtime_class: MagicMock
    ) -> None:
        """Test running with valid config."""
        import time
        mock_load.return_value = {"service": {"name": "test-service"}}
        mock_runtime = MagicMock()
        mock_runtime_class.return_value = mock_runtime
        # Mock KeyboardInterrupt to exit the while loop
        with patch.object(time, "sleep", side_effect=KeyboardInterrupt()):
            args = argparse.Namespace(config=None, dry_run=False)
            result = cmd_run(args)
        assert result == 0
        mock_load.assert_called_once()
        mock_validate.assert_called_once()
        mock_runtime_class.assert_called_once()
        mock_runtime.start.assert_called_once()
        mock_runtime.stop.assert_called_once()

    @patch("hexswitch.app.build_execution_plan")
    @patch("hexswitch.app.validate_config")
    @patch("hexswitch.app.load_config")
    def test_run_dry_run(
        self, mock_load: MagicMock, mock_validate: MagicMock, mock_plan: MagicMock
    ) -> None:
        """Test running in dry-run mode."""
        mock_load.return_value = {"service": {"name": "test-service"}}
        mock_plan.return_value = {
            "service": "test-service",
            "inbound_adapters": [],
            "outbound_adapters": [],
        }
        args = argparse.Namespace(config=None, dry_run=True)
        result = cmd_run(args)
        assert result == 0
        mock_load.assert_called_once()
        mock_validate.assert_called_once()
        mock_plan.assert_called_once()

    @patch("hexswitch.app.validate_config")
    @patch("hexswitch.app.load_config")
    def test_run_invalid_config(
        self, mock_load: MagicMock, mock_validate: MagicMock
    ) -> None:
        """Test running with invalid config."""
        mock_validate.side_effect = ConfigError("Invalid config")
        args = argparse.Namespace(config=None, dry_run=False)
        result = cmd_run(args)
        assert result == 1
        mock_load.assert_called_once()
        mock_validate.assert_called_once()

    @patch("hexswitch.app.load_config")
    def test_run_load_error(self, mock_load: MagicMock) -> None:
        """Test running when config load fails."""
        mock_load.side_effect = Exception("Load error")
        args = argparse.Namespace(config=None, dry_run=False)
        result = cmd_run(args)
        assert result == 1
        mock_load.assert_called_once()

    @patch("hexswitch.app.Runtime")
    @patch("hexswitch.app.validate_config")
    @patch("hexswitch.app.load_config")
    def test_run_runtime_error(
        self, mock_load: MagicMock, mock_validate: MagicMock, mock_runtime_class: MagicMock
    ) -> None:
        """Test running when runtime fails."""
        mock_load.return_value = {"service": {"name": "test-service"}}
        mock_runtime_class.side_effect = Exception("Runtime error")
        args = argparse.Namespace(config=None, dry_run=False)
        result = cmd_run(args)
        assert result == 2
        mock_load.assert_called_once()
        mock_validate.assert_called_once()
        mock_runtime_class.assert_called_once()


class TestCmdVersion:
    """Test cmd_version function."""

    @patch("builtins.print")
    def test_version_output(self, mock_print: MagicMock) -> None:
        """Test version command output."""
        result = cmd_version()
        assert result == 0
        assert mock_print.call_count == 2


class TestCmdInit:
    """Test cmd_init function."""

    @patch("hexswitch.app.get_example_config")
    def test_init_create_config(self, mock_example: MagicMock) -> None:
        """Test init command creates config file."""
        mock_example.return_value = "service:\n  name: test"
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test-config.yaml"
            args = argparse.Namespace(config=str(config_path), force=False)
            result = cmd_init(args)
            assert result == 0
            assert config_path.exists()
            mock_example.assert_called_once()

    @patch("hexswitch.app.get_example_config")
    def test_init_existing_file_no_force(self, mock_example: MagicMock) -> None:
        """Test init command fails when file exists and force is False."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_path = Path(f.name)

        try:
            args = argparse.Namespace(config=str(config_path), force=False)
            result = cmd_init(args)
            assert result == 1
            mock_example.assert_not_called()
        finally:
            config_path.unlink()

    @patch("hexswitch.app.get_example_config")
    def test_init_existing_file_with_force(self, mock_example: MagicMock) -> None:
        """Test init command overwrites existing file with force."""
        mock_example.return_value = "service:\n  name: test"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_path = Path(f.name)

        try:
            args = argparse.Namespace(config=str(config_path), force=True)
            result = cmd_init(args)
            assert result == 0
            mock_example.assert_called_once()
        finally:
            config_path.unlink()


class TestMain:
    """Test main function."""

    @patch("hexswitch.app.setup_logging")
    @patch("hexswitch.app.argparse.ArgumentParser.parse_args")
    @patch("hexswitch.app.cmd_version")
    def test_main_version(
        self, mock_cmd: MagicMock, mock_parse: MagicMock, mock_setup: MagicMock
    ) -> None:
        """Test main function with version command."""
        mock_parse.return_value = argparse.Namespace(
            command="version", log_level="INFO", config=None
        )
        mock_cmd.return_value = 0
        result = main()
        assert result == 0
        mock_cmd.assert_called_once()

    @patch("hexswitch.app.setup_logging")
    @patch("hexswitch.app.argparse.ArgumentParser.parse_args")
    @patch("hexswitch.app.cmd_validate")
    def test_main_validate(
        self, mock_cmd: MagicMock, mock_parse: MagicMock, mock_setup: MagicMock
    ) -> None:
        """Test main function with validate command."""
        mock_parse.return_value = argparse.Namespace(
            command="validate", log_level="INFO", config="test.yaml"
        )
        mock_cmd.return_value = 0
        result = main()
        assert result == 0
        mock_cmd.assert_called_once()

    @patch("hexswitch.app.setup_logging")
    @patch("hexswitch.app.argparse.ArgumentParser.parse_args")
    @patch("hexswitch.app.cmd_run")
    def test_main_run(
        self, mock_cmd: MagicMock, mock_parse: MagicMock, mock_setup: MagicMock
    ) -> None:
        """Test main function with run command."""
        mock_parse.return_value = argparse.Namespace(
            command="run", log_level="INFO", config=None, dry_run=False
        )
        mock_cmd.return_value = 0
        result = main()
        assert result == 0
        mock_cmd.assert_called_once()

    @patch("hexswitch.app.setup_logging")
    @patch("hexswitch.app.argparse.ArgumentParser.parse_args")
    @patch("hexswitch.app.cmd_version")
    def test_main_no_command(
        self, mock_cmd: MagicMock, mock_parse: MagicMock, mock_setup: MagicMock
    ) -> None:
        """Test main function with no command (defaults to version)."""
        mock_parse.return_value = argparse.Namespace(
            command=None, log_level="INFO", config=None
        )
        mock_cmd.return_value = 0
        result = main()
        assert result == 0
        mock_cmd.assert_called_once()

    @patch("hexswitch.app.setup_logging")
    @patch("hexswitch.app.argparse.ArgumentParser.parse_args")
    def test_main_unknown_command(
        self, mock_parse: MagicMock, mock_setup: MagicMock
    ) -> None:
        """Test main function with unknown command."""
        mock_parse.return_value = argparse.Namespace(
            command="unknown", log_level="INFO", config=None
        )
        with patch("hexswitch.app.argparse.ArgumentParser.print_help") as mock_help:
            result = main()
            assert result == 1
            mock_help.assert_called_once()

