"""In-memory example repository implementation."""

import logging
from typing import Any

from hexswitch.domain.repositories import BaseRepository
from example1.domain.entities.example import ExampleEntity
from example1.domain.ports.repositories.example_repository_port import ExampleRepositoryPort

logger = logging.getLogger(__name__)


class ExampleRepository(BaseRepository[ExampleEntity], ExampleRepositoryPort):
    """In-memory implementation of example repository.
    
    Inherits from BaseRepository which provides:
    - save(), find_by_id(), list_all(), delete()
    - count(), exists()
    
    Can add domain-specific methods here if needed.
    """

    def __init__(self) -> None:
        """Initialize repository with empty storage."""
        super().__init__()
        logger.debug("ExampleRepository initialized")

    def from_dict(self, data: dict[str, Any]) -> ExampleEntity:
        """Create entity from dictionary.

        Args:
            data: Dictionary containing entity data.

        Returns:
            Created entity.
        """
        return ExampleEntity(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description"),
            data=data.get("data"),
        )
