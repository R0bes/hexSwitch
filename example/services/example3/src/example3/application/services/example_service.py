"""Example service implementation."""

import logging
from typing import Any
import uuid

from example3_service.domain.entities.example import ExampleEntity
from example3_service.domain.ports.repositories.example_repository_port import ExampleRepositoryPort

logger = logging.getLogger(__name__)


class ExampleService:
    """Service for example entity management."""

    def __init__(self, repository: ExampleRepositoryPort) -> None:
        """Initialize example service.

        Args:
            repository: Example repository port implementation.
        """
        self.repository = repository
        logger.debug("ExampleService initialized")

    def get_example(self, entity_id: str) -> ExampleEntity:
        """Get entity by ID.

        Args:
            entity_id: Entity ID.

        Returns:
            Entity.

        Raises:
            ValueError: If entity not found.
        """
        entity = self.repository.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"Entity with id '{entity_id}' not found")
        return entity

    def list_examples(self) -> list[ExampleEntity]:
        """List all entities.

        Returns:
            List of all entities.
        """
        return self.repository.list_all()

    def create_example(self, name: str, description: str | None = None, data: dict[str, Any] | None = None, entity_id: str | None = None) -> ExampleEntity:
        """Create a new entity.

        Args:
            name: Entity name (required).
            description: Optional description.
            data: Optional additional data.
            entity_id: Optional entity ID (generated if not provided).

        Returns:
            Created entity.

        Raises:
            ValueError: If name is empty.
        """
        if not name:
            raise ValueError("Field 'name' is required")

        if entity_id is None:
            entity_id = f"item_{uuid.uuid4().hex[:8]}"

        entity = ExampleEntity(
            id=entity_id,
            name=name,
            description=description,
            data=data,
        )

        saved_entity = self.repository.save(entity)
        logger.info(f"Created entity: {saved_entity.id}")
        return saved_entity

    def update_example(self, entity_id: str, name: str | None = None, description: str | None = None, data: dict[str, Any] | None = None) -> ExampleEntity:
        """Update an existing entity.

        Args:
            entity_id: Entity ID.
            name: Optional new name.
            description: Optional new description.
            data: Optional new data.

        Returns:
            Updated entity.

        Raises:
            ValueError: If entity not found.
        """
        entity = self.repository.find_by_id(entity_id)
        if not entity:
            raise ValueError(f"Entity with id '{entity_id}' not found")

        entity.update(name=name, description=description, data=data)
        saved_entity = self.repository.save(entity)
        logger.info(f"Updated entity: {saved_entity.id}")
        return saved_entity

    def delete_example(self, entity_id: str) -> bool:
        """Delete an entity.

        Args:
            entity_id: Entity ID.

        Returns:
            True if deleted, False if not found.
        """
        deleted = self.repository.delete(entity_id)
        if deleted:
            logger.info(f"Deleted entity: {entity_id}")
        else:
            logger.warning(f"Entity not found for deletion: {entity_id}")
        return deleted

    def create_from_dict(self, data: dict[str, Any]) -> ExampleEntity:
        """Create entity from dictionary.

        Args:
            data: Dictionary containing entity data.

        Returns:
            Created entity.

        Raises:
            ValueError: If required fields are missing.
        """
        name = data.get("name", "")
        if not name:
            raise ValueError("Field 'name' is required")

        return self.create_example(
            name=name,
            description=data.get("description"),
            data=data.get("data"),
            entity_id=data.get("id"),
        )


# Singleton instance (will be initialized with repository)
_example3_service: ExampleService | None = None


def initialize_example3_service(repository: ExampleRepositoryPort | None = None) -> ExampleService:
    """Initialize the global example service instance.

    Args:
        repository: Example repository port implementation (creates default if not provided).

    Returns:
        Initialized example service.
    """
    global _example3_service
    if repository is None:
        from example3_service.infrastructure.repositories.example_repository import ExampleRepository
        repository = ExampleRepository()
    _example3_service = ExampleService(repository)
    return _example3_service


def get_example3_service() -> ExampleService:
    """Get the global example service instance.

    Returns:
        Example service instance.

    Raises:
        RuntimeError: If service is not initialized.
    """
    global _example3_service
    if _example3_service is None:
        _example3_service = initialize_example3_service()
    return _example3_service

