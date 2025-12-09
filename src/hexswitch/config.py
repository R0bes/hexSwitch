"""Configuration loading and validation for HexSwitch."""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = "hex-config.yaml"


class ConfigError(Exception):
    """Raised when configuration validation fails."""

    pass


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration file. Defaults to hex-config.yaml.

    Returns:
        Configuration dictionary.

    Raises:
        ConfigError: If configuration file cannot be loaded or is invalid.
    """
    if config_path is None:
        config_path = Path(DEFAULT_CONFIG_PATH)
    else:
        config_path = Path(config_path)

    # Check if file exists
    if not config_path.exists():
        raise ConfigError(f"Configuration file not found: {config_path}")

    # Load YAML
    try:
        with config_path.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML syntax in {config_path}: {e}") from e
    except Exception as e:
        raise ConfigError(f"Error reading configuration file {config_path}: {e}") from e

    if config is None:
        raise ConfigError(f"Configuration file is empty: {config_path}")

    if not isinstance(config, dict):
        raise ConfigError(f"Configuration must be a dictionary, got {type(config).__name__}")

    return config


def validate_config(config: dict[str, Any]) -> None:
    """Validate configuration structure and values.

    Args:
        config: Configuration dictionary to validate.

    Raises:
        ConfigError: If validation fails.
    """
    # Check required sections
    required_sections = ["service"]
    for section in required_sections:
        if section not in config:
            raise ConfigError(f"Missing required section: {section}")

    # Validate service section
    service = config.get("service", {})
    if not isinstance(service, dict):
        raise ConfigError("Section 'service' must be a dictionary")

    if "name" not in service:
        raise ConfigError("Section 'service' must contain 'name'")

    # Validate inbound section (optional but if present must be valid)
    if "inbound" in config:
        inbound = config["inbound"]
        if not isinstance(inbound, dict):
            raise ConfigError("Section 'inbound' must be a dictionary")
        _validate_adapters(inbound, "inbound")

    # Validate outbound section (optional but if present must be valid)
    if "outbound" in config:
        outbound = config["outbound"]
        if not isinstance(outbound, dict):
            raise ConfigError("Section 'outbound' must be a dictionary")
        _validate_adapters(outbound, "outbound")

    # Validate logging section (optional)
    if "logging" in config:
        logging_config = config["logging"]
        if not isinstance(logging_config, dict):
            raise ConfigError("Section 'logging' must be a dictionary")


def _validate_adapters(adapters: dict[str, Any], section_name: str) -> None:
    """Validate adapter configuration.

    Args:
        adapters: Adapter configuration dictionary.
        section_name: Name of the section (for error messages).

    Raises:
        ConfigError: If validation fails.
    """
    for adapter_name, adapter_config in adapters.items():
        if not isinstance(adapter_config, dict):
            raise ConfigError(
                f"Adapter '{adapter_name}' in section '{section_name}' must be a dictionary"
            )

        # Check if 'enabled' flag exists and is boolean
        if "enabled" in adapter_config:
            if not isinstance(adapter_config["enabled"], bool):
                raise ConfigError(
                    f"Adapter '{adapter_name}' in section '{section_name}': "
                    "'enabled' must be a boolean"
                )

        # Validate HTTP adapter specific configuration
        if adapter_name == "http" and section_name == "inbound":
            _validate_http_adapter(adapter_name, adapter_config, section_name)


def _validate_http_adapter(
    adapter_name: str, adapter_config: dict[str, Any], section_name: str
) -> None:
    """Validate HTTP adapter configuration.

    Args:
        adapter_name: Name of the adapter.
        adapter_config: Adapter configuration dictionary.
        section_name: Name of the section (for error messages).

    Raises:
        ConfigError: If validation fails.
    """
    # Validate base_path (optional, must be string if present)
    if "base_path" in adapter_config:
        if not isinstance(adapter_config["base_path"], str):
            raise ConfigError(
                f"Adapter '{adapter_name}' in section '{section_name}': "
                "'base_path' must be a string"
            )

    # Validate port (optional, must be integer if present)
    if "port" in adapter_config:
        if not isinstance(adapter_config["port"], int):
            raise ConfigError(
                f"Adapter '{adapter_name}' in section '{section_name}': "
                "'port' must be an integer"
            )
        if not (1 <= adapter_config["port"] <= 65535):
            raise ConfigError(
                f"Adapter '{adapter_name}' in section '{section_name}': "
                "'port' must be between 1 and 65535"
            )

    # Validate routes (optional, must be list if present)
    if "routes" in adapter_config:
        routes = adapter_config["routes"]
        if not isinstance(routes, list):
            raise ConfigError(
                f"Adapter '{adapter_name}' in section '{section_name}': "
                "'routes' must be a list"
            )

        for i, route in enumerate(routes):
            if not isinstance(route, dict):
                raise ConfigError(
                    f"Adapter '{adapter_name}' in section '{section_name}': "
                    f"Route at index {i} must be a dictionary"
                )

            # Validate required route fields
            if "path" not in route:
                raise ConfigError(
                    f"Adapter '{adapter_name}' in section '{section_name}': "
                    f"Route at index {i} must contain 'path'"
                )
            if not isinstance(route["path"], str):
                raise ConfigError(
                    f"Adapter '{adapter_name}' in section '{section_name}': "
                    f"Route at index {i}: 'path' must be a string"
                )

            if "method" not in route:
                raise ConfigError(
                    f"Adapter '{adapter_name}' in section '{section_name}': "
                    f"Route at index {i} must contain 'method'"
                )
            if not isinstance(route["method"], str):
                raise ConfigError(
                    f"Adapter '{adapter_name}' in section '{section_name}': "
                    f"Route at index {i}: 'method' must be a string"
                )
            if route["method"].upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                raise ConfigError(
                    f"Adapter '{adapter_name}' in section '{section_name}': "
                    f"Route at index {i}: 'method' must be one of: GET, POST, PUT, DELETE, PATCH"
                )

            if "handler" not in route:
                raise ConfigError(
                    f"Adapter '{adapter_name}' in section '{section_name}': "
                    f"Route at index {i} must contain 'handler'"
                )
            if not isinstance(route["handler"], str):
                raise ConfigError(
                    f"Adapter '{adapter_name}' in section '{section_name}': "
                    f"Route at index {i}: 'handler' must be a string"
                )
            # Validate handler format (module:function)
            _validate_handler_reference(route["handler"], adapter_name, section_name, i)


def _validate_handler_reference(
    handler_path: str, adapter_name: str, section_name: str, route_index: int | None = None
) -> None:
    """Validate handler reference format.

    Args:
        handler_path: Handler reference string.
        adapter_name: Name of the adapter (for error messages).
        section_name: Name of the section (for error messages).
        route_index: Optional route index (for error messages).

    Raises:
        ConfigError: If validation fails.
    """
    if ":" not in handler_path:
        route_info = f" at route index {route_index}" if route_index is not None else ""
        raise ConfigError(
            f"Adapter '{adapter_name}' in section '{section_name}'{route_info}: "
            f"Invalid handler format '{handler_path}'. "
            "Expected format: 'module.path:function_name'"
        )

    module_path, function_name = handler_path.rsplit(":", 1)

    if not module_path or not function_name:
        route_info = f" at route index {route_index}" if route_index is not None else ""
        raise ConfigError(
            f"Adapter '{adapter_name}' in section '{section_name}'{route_info}: "
            f"Invalid handler format '{handler_path}'. "
            "Module path and function name must not be empty."
        )


def get_example_config() -> str:
    """Generate example configuration file content.

    Returns:
        Example configuration as YAML string.
    """
    return """service:
  name: example-service
  runtime: python

inbound:
  http:
    enabled: true
    base_path: /api
    routes:
      - path: /hello
        method: GET
        handler: adapters.http_handlers:hello

outbound:
  postgres:
    enabled: false
    dsn_env: POSTGRES_DSN

logging:
  level: INFO
"""

