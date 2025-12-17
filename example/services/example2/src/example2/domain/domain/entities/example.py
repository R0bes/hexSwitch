"""Example domain entity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ExampleEntity:
    """Example domain entity for demonstration."""

    id: str
    name: str
    description: str | None = None
    data: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def update(self, name: str | None = None, description: str | None = None, data: dict[str, Any] | None = None) -> None:
        """Update entity fields."""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if data is not None:
            self.data = data
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "data": self.data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

