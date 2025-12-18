"""Unit tests for service module."""

import pytest

from hexswitch.service import HexSwitchServer


class TestHexSwitchServer:
    """Test HexSwitchServer class."""

    def test_service_is_abstract(self) -> None:
        """Test that HexSwitchServer is abstract."""
        # Cannot instantiate abstract class
        with pytest.raises(TypeError):
            HexSwitchServer()  # type: ignore[abstract]

