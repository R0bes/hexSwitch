"""Unit tests for BaseRepository and BaseRepositoryPort."""

from dataclasses import dataclass

import pytest

from hexswitch.domain.repositories import BaseRepository, BaseRepositoryPort


@dataclass
class SampleEntity:
    """Sample entity for repository tests."""
    id: str
    name: str
    value: int = 0


class SampleRepositoryPort(BaseRepositoryPort[SampleEntity]):
    """Concrete implementation of BaseRepositoryPort for testing."""
    pass


class SampleRepository(BaseRepository[SampleEntity], SampleRepositoryPort):
    """Concrete implementation of BaseRepository for testing."""

    def from_dict(self, data: dict) -> SampleEntity:
        """Create entity from dictionary."""
        return SampleEntity(
            id=data.get("id", ""),
            name=data.get("name", ""),
            value=data.get("value", 0),
        )


class TestBaseRepositoryPort:
    """Tests for BaseRepositoryPort interface."""

    def test_port_is_abstract(self):
        """Test that BaseRepositoryPort is abstract and cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseRepositoryPort()  # type: ignore

    def test_port_requires_implementation(self):
        """Test that concrete port must implement all methods."""
        # SampleRepositoryPort is abstract, so we need a concrete implementation
        repo = SampleRepository()
        assert isinstance(repo, BaseRepositoryPort)


class TestBaseRepository:
    """Tests for BaseRepository implementation."""

    def test_repository_initialization(self):
        """Test repository initialization."""
        repo = SampleRepository()
        assert repo.count() == 0
        assert len(repo.list_all()) == 0

    def test_save_entity(self):
        """Test saving an entity."""
        repo = SampleRepository()
        entity = SampleEntity(id="1", name="test", value=42)

        saved = repo.save(entity)
        assert saved.id == "1"
        assert saved.name == "test"
        assert saved.value == 42
        assert repo.count() == 1

    def test_save_entity_without_id_raises_error(self):
        """Test that saving entity without id raises error."""
        repo = SampleRepository()

        @dataclass
        class EntityWithoutId:
            name: str

        entity = EntityWithoutId(name="test")
        with pytest.raises(ValueError, match="id"):
            repo.save(entity)  # type: ignore

    def test_find_by_id_existing(self):
        """Test finding existing entity by ID."""
        repo = SampleRepository()
        entity = SampleEntity(id="1", name="test", value=42)
        repo.save(entity)

        found = repo.find_by_id("1")
        assert found is not None
        assert found.id == "1"
        assert found.name == "test"
        assert found.value == 42

    def test_find_by_id_nonexistent(self):
        """Test finding non-existent entity returns None."""
        repo = SampleRepository()
        found = repo.find_by_id("nonexistent")
        assert found is None

    def test_list_all_empty(self):
        """Test listing all entities when repository is empty."""
        repo = SampleRepository()
        entities = repo.list_all()
        assert entities == []
        assert len(entities) == 0

    def test_list_all_multiple(self):
        """Test listing all entities."""
        repo = SampleRepository()
        entity1 = SampleEntity(id="1", name="test1", value=1)
        entity2 = SampleEntity(id="2", name="test2", value=2)
        entity3 = SampleEntity(id="3", name="test3", value=3)

        repo.save(entity1)
        repo.save(entity2)
        repo.save(entity3)

        entities = repo.list_all()
        assert len(entities) == 3
        assert {e.id for e in entities} == {"1", "2", "3"}

    def test_delete_existing(self):
        """Test deleting existing entity."""
        repo = SampleRepository()
        entity = SampleEntity(id="1", name="test", value=42)
        repo.save(entity)

        deleted = repo.delete("1")
        assert deleted is True
        assert repo.count() == 0
        assert repo.find_by_id("1") is None

    def test_delete_nonexistent(self):
        """Test deleting non-existent entity returns False."""
        repo = SampleRepository()
        deleted = repo.delete("nonexistent")
        assert deleted is False
        assert repo.count() == 0

    def test_count_empty(self):
        """Test count when repository is empty."""
        repo = SampleRepository()
        assert repo.count() == 0

    def test_count_multiple(self):
        """Test count with multiple entities."""
        repo = SampleRepository()
        for i in range(5):
            entity = SampleEntity(id=str(i), name=f"test{i}", value=i)
            repo.save(entity)

        assert repo.count() == 5

    def test_exists_true(self):
        """Test exists returns True for existing entity."""
        repo = SampleRepository()
        entity = SampleEntity(id="1", name="test", value=42)
        repo.save(entity)

        assert repo.exists("1") is True

    def test_exists_false(self):
        """Test exists returns False for non-existent entity."""
        repo = SampleRepository()
        assert repo.exists("nonexistent") is False

    def test_save_updates_existing(self):
        """Test that saving entity with existing ID updates it."""
        repo = SampleRepository()
        entity1 = SampleEntity(id="1", name="original", value=1)
        repo.save(entity1)

        entity2 = SampleEntity(id="1", name="updated", value=2)
        repo.save(entity2)

        assert repo.count() == 1
        found = repo.find_by_id("1")
        assert found is not None
        assert found.name == "updated"
        assert found.value == 2

    def test_from_dict_not_implemented(self):
        """Test that from_dict raises NotImplementedError if not overridden."""
        repo = BaseRepository[SampleEntity]()
        with pytest.raises(NotImplementedError):
            repo.from_dict({"id": "1", "name": "test"})

    def test_from_dict_implemented(self):
        """Test that from_dict works when implemented."""
        repo = SampleRepository()
        entity = repo.from_dict({"id": "1", "name": "test", "value": 42})

        assert entity.id == "1"
        assert entity.name == "test"
        assert entity.value == 42

