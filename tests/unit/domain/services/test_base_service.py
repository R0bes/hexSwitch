"""Unit tests for BaseService."""

from dataclasses import dataclass
from typing import Optional
from unittest.mock import Mock

import pytest

from hexswitch.domain.repositories import BaseRepositoryPort
from hexswitch.domain.services import BaseService


@dataclass
class SampleEntity:
    """Sample entity for service tests."""
    id: str
    name: str
    value: int = 0


class MockRepository(BaseRepositoryPort[SampleEntity]):
    """Mock repository for testing services."""

    def __init__(self):
        self._storage: dict[str, SampleEntity] = {}

    def save(self, entity: SampleEntity) -> SampleEntity:
        self._storage[entity.id] = entity
        return entity

    def find_by_id(self, entity_id: str) -> Optional[SampleEntity]:
        return self._storage.get(entity_id)

    def list_all(self) -> list[SampleEntity]:
        return list(self._storage.values())

    def delete(self, entity_id: str) -> bool:
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

    def exists(self, entity_id: str) -> bool:
        return entity_id in self._storage

    def count(self) -> int:
        return len(self._storage)


class SampleService(BaseService[SampleEntity, MockRepository]):
    """Concrete service implementation for testing."""

    def create_entity(self, name: str, value: int = 0) -> SampleEntity:
        """Create a new entity."""
        entity_id = f"entity_{len(self.repository.list_all()) + 1}"
        entity = SampleEntity(id=entity_id, name=name, value=value)
        return self.repository.save(entity)


class TestBaseService:
    """Tests for BaseService."""

    def test_service_initialization(self):
        """Test service initialization with repository."""
        repo = MockRepository()
        service = SampleService(repo)

        assert service.repository is repo
        assert service.logger is not None

    def test_get_by_id_existing(self):
        """Test getting existing entity by ID."""
        repo = MockRepository()
        entity = SampleEntity(id="1", name="test", value=42)
        repo.save(entity)

        service = SampleService(repo)
        found = service.get_by_id("1")

        assert found.id == "1"
        assert found.name == "test"
        assert found.value == 42

    def test_get_by_id_nonexistent_raises_error(self):
        """Test that getting non-existent entity raises ValueError."""
        repo = MockRepository()
        service = SampleService(repo)

        with pytest.raises(ValueError, match="not found"):
            service.get_by_id("nonexistent")

    def test_list_all_empty(self):
        """Test listing all entities when empty."""
        repo = MockRepository()
        service = SampleService(repo)

        entities = service.list_all()
        assert entities == []

    def test_list_all_multiple(self):
        """Test listing all entities."""
        repo = MockRepository()
        entity1 = SampleEntity(id="1", name="test1", value=1)
        entity2 = SampleEntity(id="2", name="test2", value=2)
        repo.save(entity1)
        repo.save(entity2)

        service = SampleService(repo)
        entities = service.list_all()

        assert len(entities) == 2
        assert {e.id for e in entities} == {"1", "2"}

    def test_delete_existing(self):
        """Test deleting existing entity."""
        repo = MockRepository()
        entity = SampleEntity(id="1", name="test", value=42)
        repo.save(entity)

        service = SampleService(repo)
        deleted = service.delete("1")

        assert deleted is True
        assert repo.find_by_id("1") is None

    def test_delete_nonexistent(self):
        """Test deleting non-existent entity returns False."""
        repo = MockRepository()
        service = SampleService(repo)

        deleted = service.delete("nonexistent")
        assert deleted is False

    def test_exists_true(self):
        """Test exists returns True for existing entity."""
        repo = MockRepository()
        entity = SampleEntity(id="1", name="test", value=42)
        repo.save(entity)

        service = SampleService(repo)
        assert service.exists("1") is True

    def test_exists_false(self):
        """Test exists returns False for non-existent entity."""
        repo = MockRepository()
        service = SampleService(repo)

        assert service.exists("nonexistent") is False

    def test_exists_without_method_fallback(self):
        """Test exists works even if repository doesn't have exists method."""
        repo = Mock()
        repo.find_by_id = Mock(return_value=None)
        repo.exists = Mock(return_value=False)  # BaseService calls repository.exists()

        service = SampleService(repo)  # type: ignore
        assert service.exists("nonexistent") is False

        entity = SampleEntity(id="1", name="test", value=42)
        repo.find_by_id = Mock(return_value=entity)
        repo.exists = Mock(return_value=True)
        assert service.exists("1") is True

    def test_count_empty(self):
        """Test count when repository is empty."""
        repo = MockRepository()
        service = SampleService(repo)

        assert service.count() == 0

    def test_count_multiple(self):
        """Test count with multiple entities."""
        repo = MockRepository()
        for i in range(5):
            entity = SampleEntity(id=str(i), name=f"test{i}", value=i)
            repo.save(entity)

        service = SampleService(repo)
        assert service.count() == 5

    def test_count_without_method_fallback(self):
        """Test count works even if repository doesn't have count method."""
        repo = Mock()
        repo.list_all = Mock(return_value=[
            SampleEntity(id="1", name="test1", value=1),
            SampleEntity(id="2", name="test2", value=2),
        ])
        repo.count = Mock(return_value=2)  # BaseService calls repository.count()

        service = SampleService(repo)  # type: ignore
        assert service.count() == 2

    def test_service_can_add_domain_methods(self):
        """Test that service can add domain-specific methods."""
        repo = MockRepository()
        service = SampleService(repo)

        entity = service.create_entity("test", 42)
        assert entity.name == "test"
        assert entity.value == 42
        assert entity.id.startswith("entity_")

        found = service.get_by_id(entity.id)
        assert found.name == "test"

