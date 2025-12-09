"""Base classes for HexSwitch adapters."""

from abc import ABC, abstractmethod


class InboundAdapter(ABC):
    """Base class for inbound adapters (receiving requests/messages)."""

    def __init__(self, name: str, config: dict):
        """Initialize inbound adapter.

        Args:
            name: Adapter name.
            config: Adapter configuration dictionary.
        """
        self.name = name
        self.config = config
        self._running = False

    @abstractmethod
    def start(self) -> None:
        """Start the adapter.

        Raises:
            AdapterStartError: If the adapter fails to start.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the adapter.

        Raises:
            AdapterStopError: If the adapter fails to stop.
        """
        pass

    def is_running(self) -> bool:
        """Check if the adapter is currently running.

        Returns:
            True if running, False otherwise.
        """
        return self._running


class OutboundAdapter(ABC):
    """Base class for outbound adapters (sending requests/messages)."""

    def __init__(self, name: str, config: dict):
        """Initialize outbound adapter.

        Args:
            name: Adapter name.
            config: Adapter configuration dictionary.
        """
        self.name = name
        self.config = config
        self._connected = False

    @abstractmethod
    def connect(self) -> None:
        """Connect to the external system.

        Raises:
            AdapterConnectionError: If the connection fails.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the external system."""
        pass

    def is_connected(self) -> bool:
        """Check if the adapter is currently connected.

        Returns:
            True if connected, False otherwise.
        """
        return self._connected

