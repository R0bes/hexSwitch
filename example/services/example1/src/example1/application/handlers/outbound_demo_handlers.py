"""Handlers demonstrating outbound adapter usage."""

import logging

from hexswitch.infrastructure.ports.registry import get_port_registry
from hexswitch.shared.envelope import Envelope

logger = logging.getLogger(__name__)


def demo_http_client_handler(envelope: Envelope) -> Envelope:
    """Demonstrate HTTP client outbound adapter usage.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with result from external HTTP API.
    """
    try:
        # Get HTTP client adapter from port registry
        port_registry = get_port_registry()
        http_client = port_registry.get_outbound_port("external_api")

        if not http_client:
            return Envelope.error(503, "HTTP client adapter not available")

        # Create request envelope for external API
        external_request = Envelope(
            path="/api/data",
            method="GET",
            headers={"Accept": "application/json"},
        )

        # Make request using HTTP client adapter
        response = http_client.request(external_request)

        logger.info(f"HTTP client response: {response.status_code}")

        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data={
                "message": "HTTP client adapter used successfully",
                "external_response": response.data,
            },
        )
    except Exception as e:
        logger.exception(f"Error using HTTP client adapter: {e}")
        return Envelope.error(500, f"Error using HTTP client: {str(e)}")


def demo_grpc_client_handler(envelope: Envelope) -> Envelope:
    """Demonstrate gRPC client outbound adapter usage.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with result from external gRPC service.
    """
    try:
        # Get gRPC client adapter from port registry
        port_registry = get_port_registry()
        grpc_client = port_registry.get_outbound_port("external_grpc")

        if not grpc_client:
            return Envelope.error(503, "gRPC client adapter not available")

        # Create request envelope for external gRPC service
        external_request = Envelope(
            path="/ExternalService/GetData",
            method="POST",
            body={"query": "example"},
        )

        # Make request using gRPC client adapter
        response = grpc_client.request(external_request)

        logger.info(f"gRPC client response: {response.status_code}")

        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data={
                "message": "gRPC client adapter used successfully",
                "external_response": response.data,
            },
        )
    except Exception as e:
        logger.exception(f"Error using gRPC client adapter: {e}")
        return Envelope.error(500, f"Error using gRPC client: {str(e)}")


def demo_websocket_client_handler(envelope: Envelope) -> Envelope:
    """Demonstrate WebSocket client outbound adapter usage.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with result from external WebSocket server.
    """
    try:
        # Get WebSocket client adapter from port registry
        port_registry = get_port_registry()
        websocket_client = port_registry.get_outbound_port("external_websocket")

        if not websocket_client:
            return Envelope.error(503, "WebSocket client adapter not available")

        # Create request envelope for external WebSocket server
        external_request = Envelope(
            path="/messages",
            method="POST",
            body={"type": "request", "action": "get_data"},
        )

        # Make request using WebSocket client adapter
        response = websocket_client.request(external_request)

        logger.info(f"WebSocket client response: {response.status_code}")

        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data={
                "message": "WebSocket client adapter used successfully",
                "external_response": response.data,
            },
        )
    except Exception as e:
        logger.exception(f"Error using WebSocket client adapter: {e}")
        return Envelope.error(500, f"Error using WebSocket client: {str(e)}")


def demo_mcp_client_handler(envelope: Envelope) -> Envelope:
    """Demonstrate MCP client outbound adapter usage.

    Args:
        envelope: Request envelope.

    Returns:
        Response envelope with result from external MCP server.
    """
    try:
        # Get MCP client adapter from port registry
        port_registry = get_port_registry()
        mcp_client = port_registry.get_outbound_port("external_mcp")

        if not mcp_client:
            return Envelope.error(503, "MCP client adapter not available")

        # Create request envelope for external MCP server
        external_request = Envelope(
            path="/tools/list",
            method="POST",
            body={},
        )

        # Make request using MCP client adapter
        response = mcp_client.request(external_request)

        logger.info(f"MCP client response: {response.status_code}")

        return Envelope(
            path=envelope.path,
            method=envelope.method,
            status_code=200,
            data={
                "message": "MCP client adapter used successfully",
                "external_response": response.data,
            },
        )
    except Exception as e:
        logger.exception(f"Error using MCP client adapter: {e}")
        return Envelope.error(500, f"Error using MCP client: {str(e)}")

