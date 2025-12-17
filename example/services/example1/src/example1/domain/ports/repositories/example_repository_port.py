"""Example repository port interface."""

from example1.domain.entities.example import ExampleEntity
from hexswitch.domain.repositories import BaseRepositoryPort


class ExampleRepositoryPort(BaseRepositoryPort[ExampleEntity]):
    """Port interface for example repository operations.

    Extends BaseRepositoryPort with any domain-specific methods.
    For now, we only use the base CRUD operations.
    """
