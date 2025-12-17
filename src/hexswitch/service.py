from abc import ABC, abstractmethod


class HexSwitchService(ABC):
    """Base class for all HexSwitch services."""

    @abstractmethod
    def start(self) -> None:
        """Start the service."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the service."""
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """Check if the service is running."""
        pass
