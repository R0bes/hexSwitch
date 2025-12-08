"""Mock consumer handler for integration testing."""

import json
import logging
import os

logger = logging.getLogger(__name__)


def handle_consume(request_data: dict) -> dict:
    """Handle consume request - simulates business logic."""
    logger.info(f"Consumer received: {request_data}")
    
    # Mock business logic: finalize processing
    result = {
        "consumer_id": os.getenv("SERVICE_NAME", "consumer"),
        "input_data": request_data,
        "processed_by": "consumer",
        "final_status": "completed",
        "message": "Data successfully processed through pipeline",
    }
    
    logger.info(f"Consumer returning: {result}")
    return result


def handle_health() -> dict:
    """Health check handler."""
    return {"status": "healthy", "service": "consumer"}

