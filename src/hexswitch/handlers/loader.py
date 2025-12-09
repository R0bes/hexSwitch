"""Handler loader for dynamically importing handler functions."""

import importlib
from typing import Callable

from hexswitch.adapters.exceptions import AdapterError


class HandlerError(AdapterError):
    """Raised when handler loading fails."""

    pass


def load_handler(handler_path: str) -> Callable:
    """Load a handler function from a string reference.

    The handler path should be in the format: 'module.path:function_name'

    Args:
        handler_path: Handler reference in format 'module:function'.

    Returns:
        The handler function (callable).

    Raises:
        HandlerError: If the handler cannot be loaded.

    Example:
        >>> handler = load_handler("adapters.http_handlers:hello")
        >>> handler(request)
    """
    if ":" not in handler_path:
        raise HandlerError(
            f"Invalid handler path format: {handler_path}. "
            "Expected format: 'module.path:function_name'"
        )

    module_path, function_name = handler_path.rsplit(":", 1)

    if not module_path or not function_name:
        raise HandlerError(
            f"Invalid handler path format: {handler_path}. "
            "Module path and function name must not be empty."
        )

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise HandlerError(f"Failed to import module '{module_path}': {e}") from e

    if not hasattr(module, function_name):
        raise HandlerError(
            f"Module '{module_path}' does not have attribute '{function_name}'"
        )

    handler = getattr(module, function_name)

    if not callable(handler):
        raise HandlerError(
            f"'{function_name}' in module '{module_path}' is not callable"
        )

    return handler

