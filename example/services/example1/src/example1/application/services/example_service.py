"""Example service implementation."""

import logging
from typing import Any
import uuid

from example1.domain.entities.example import ExampleEntity
from example1.domain.ports.repositories.example_repository_port import ExampleRepositoryPort
from hexswitch.domain.services import BaseService

logger = logging.getLogger(__name__)


class ExampleService(BaseService[ExampleEntity, ExampleRepositoryPort]):
    """Service for example entity management.

    Inherits from BaseService which provides:
    - get_by_id(), list_all(), delete()
    - exists(), count()

    Adds domain-specific business logic here.
    """

    def get_example(self, entity_id: str) -> ExampleEntity:
        """Get entity by ID (alias for get_by_id for backward compatibility).

        Args:
            entity_id: Entity ID.

        Returns:
            Entity.

        Raises:
            ValueError: If entity not found.
        """
        return self.get_by_id(entity_id)

    def list_examples(self) -> list[ExampleEntity]:
        """List all entities (alias for list_all for backward compatibility).

        Returns:
            List of all entities.
        """
        return self.list_all()

    def create_example(
        self,
        name: str,
        description: str | None = None,
        data: dict[str, Any] | None = None,
        entity_id: str | None = None,
    ) -> ExampleEntity:
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
        self.logger.info(f"Created entity: {saved_entity.id}")
        return saved_entity

    def update_example(
        self,
        entity_id: str,
        name: str | None = None,
        description: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> ExampleEntity:
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
        entity = self.get_by_id(entity_id)
        entity.update(name=name, description=description, data=data)
        saved_entity = self.repository.save(entity)
        self.logger.info(f"Updated entity: {saved_entity.id}")
        return saved_entity

    def delete_example(self, entity_id: str) -> bool:
        """Delete an entity (alias for delete for backward compatibility).

        Args:
            entity_id: Entity ID.

        Returns:
            True if deleted, False if not found.
        """
        return self.delete(entity_id)

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
_example_service: ExampleService | None = None


def initialize_example_service(repository: ExampleRepositoryPort | None = None) -> ExampleService:
    """Initialize the global example service instance.

    Args:
        repository: Example repository port implementation (creates default if not provided).

    Returns:
        Initialized example service.
    """
    global _example_service
    if repository is None:
        from example1.infrastructure.repositories.example_repository import ExampleRepository
        repository = ExampleRepository()
    _example_service = ExampleService(repository)
    return _example_service


def get_example_service() -> ExampleService:
    """Get the global example service instance.

    Returns:
        Example service instance.

    Raises:
        RuntimeError: If service is not initialized.
    """
    global _example_service
    if _example_service is None:
        _example_service = initialize_example_service()
    return _example_service
