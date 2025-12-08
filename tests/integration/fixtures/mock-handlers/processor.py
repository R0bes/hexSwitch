"""Mock processor handler for integration testing."""

import json
import logging
import os

logger = logging.getLogger(__name__)


def handle_process(request_data: dict) -> dict:
    """Handle process request - simulates business logic."""
    logger.info(f"Processor received: {request_data}")
    
    # Mock business logic: transform data
    result = {
        "processor_id": os.getenv("SERVICE_NAME", "processor"),
        "input_data": request_data,
        "processed_by": "processor",
        "transformation": "uppercase_keys",
        "data": {k.upper(): v for k, v in request_data.get("original_data", {}).items()},
    }
    
    logger.info(f"Processor returning: {result}")
    return result


def handle_health() -> dict:
    """Health check handler."""
    return {"status": "healthy", "service": "processor"}

