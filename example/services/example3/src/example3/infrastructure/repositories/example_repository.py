"""In-memory example repository implementation."""

import logging
from typing import Any

from example3_service.domain.entities.example import ExampleEntity
from example3_service.domain.ports.repositories.example_repository_port import ExampleRepositoryPort

logger = logging.getLogger(__name__)


class ExampleRepository(ExampleRepositoryPort):
    """In-memory implementation of example repository."""

    def __init__(self) -> None:
        """Initialize repository with empty storage."""
        self._storage: dict[str, ExampleEntity] = {}
        logger.debug("ExampleRepository initialized")

    def save(self, entity: ExampleEntity) -> ExampleEntity:
        """Save entity to repository.

        Args:
            entity: Entity to save.

        Returns:
            Saved entity.
        """
        self._storage[entity.id] = entity
        logger.debug(f"Saved entity: {entity.id}")
        return entity

    def find_by_id(self, entity_id: str) -> ExampleEntity | None:
        """Find entity by ID.

        Args:
            entity_id: Entity ID.

        Returns:
            Entity if found, None otherwise.
        """
        entity = self._storage.get(entity_id)
        if entity:
            logger.debug(f"Found entity: {entity_id}")
        else:
            logger.debug(f"Entity not found: {entity_id}")
        return entity

    def list_all(self) -> list[ExampleEntity]:
        """List all entities.

        Returns:
            List of all entities.
        """
        entities = list(self._storage.values())
        logger.debug(f"Listed {len(entities)} entities")
        return entities

    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID.

        Args:
            entity_id: Entity ID.

        Returns:
            True if deleted, False if not found.
        """
        if entity_id in self._storage:
            del self._storage[entity_id]
            logger.debug(f"Deleted entity: {entity_id}")
            return True
        logger.debug(f"Entity not found for deletion: {entity_id}")
        return False

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

