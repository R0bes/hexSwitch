"""WebSocket and MCP handlers for example3 service."""

from example3_service.application.handlers.websocket_handlers import (
    websocket_message_handler,
    call_example1_handler,
    call_example2_handler,
)
from example3_service.application.handlers.mcp_handlers import (
    mcp_initialize_handler,
    mcp_tools_list_handler,
    mcp_tools_call_handler,
    mcp_resources_list_handler,
    mcp_resources_read_handler,
)

__all__ = [
    "websocket_message_handler",
    "call_example1_handler",
    "call_example2_handler",
    "mcp_initialize_handler",
    "mcp_tools_list_handler",
    "mcp_tools_call_handler",
    "mcp_resources_list_handler",
    "mcp_resources_read_handler",
]

