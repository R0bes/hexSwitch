"""Example repository port interface."""

from abc import ABC, abstractmethod

from example3_service.domain.entities.example import ExampleEntity


class ExampleRepositoryPort(ABC):
    """Port interface for example repository operations."""

    @abstractmethod
    def save(self, entity: ExampleEntity) -> ExampleEntity:
        """Save entity to repository.

        Args:
            entity: Entity to save.

        Returns:
            Saved entity.
        """
        pass

    @abstractmethod
    def find_by_id(self, entity_id: str) -> ExampleEntity | None:
        """Find entity by ID.

        Args:
            entity_id: Entity ID.

        Returns:
            Entity if found, None otherwise.
        """
        pass

    @abstractmethod
    def list_all(self) -> list[ExampleEntity]:
        """List all entities.

        Returns:
            List of all entities.
        """
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID.

        Args:
            entity_id: Entity ID.

        Returns:
            True if deleted, False if not found.
        """
        pass

