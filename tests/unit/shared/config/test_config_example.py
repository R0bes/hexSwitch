"""Unit tests for config example generation."""

from hexswitch.shared.config.config import get_example_config


class TestExampleConfig:
    """Test example config generation."""

    def test_get_example_config(self) -> None:
        """Test getting example config."""
        example = get_example_config()
        assert isinstance(example, str)
        assert len(example) > 0
        assert "service" in example
        assert "inbound" in example or "outbound" in example

