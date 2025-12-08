"""Mock producer handler for integration testing."""

import json
import logging
import os

logger = logging.getLogger(__name__)


def handle_produce(request_data: dict) -> dict:
    """Handle produce request - simulates business logic."""
    logger.info(f"Producer received: {request_data}")
    
    # Mock business logic: add producer metadata
    result = {
        "producer_id": os.getenv("SERVICE_NAME", "producer"),
        "original_data": request_data,
        "processed_by": "producer",
        "timestamp": "2024-01-01T00:00:00Z",
    }
    
    logger.info(f"Producer returning: {result}")
    return result


def handle_health() -> dict:
    """Health check handler."""
    return {"status": "healthy", "service": "producer"}

