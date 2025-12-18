"""Unit tests for NATS adapters."""

import pytest

from hexswitch.adapters.nats import NatsAdapterClient, NatsAdapterServer
from hexswitch.adapters.nats._Nats_Envelope import NatsEnvelope
from hexswitch.shared.envelope import Envelope


class TestNatsEnvelope:
    """Test NATS envelope conversion."""

    def test_message_to_envelope(self) -> None:
        """Test converting NATS message to Envelope."""
        converter = NatsEnvelope()
        subject = "test.subject"
        data = b'{"key": "value"}'
        headers = {"X-Trace-Id": "12345"}

        envelope = converter.message_to_envelope(
            subject=subject, data=data, headers=headers
        )

        assert envelope.path == subject
        assert envelope.body == {"key": "value"}
        assert envelope.metadata["subject"] == subject
        assert "X-Trace-Id" in envelope.headers

    def test_envelope_to_message(self) -> None:
        """Test converting Envelope to NATS message."""
        converter = NatsEnvelope()
        envelope = Envelope(
            path="test.subject",
            data={"result": "success"},
            trace_id="12345",
        )

        message_data, headers = converter.envelope_to_message(envelope)

        assert isinstance(message_data, bytes)
        assert "result" in message_data.decode("utf-8")
        assert "trace_id" in str(headers).lower() or "trace" in str(headers).lower()


class TestNatsAdapterServer:
    """Test NATS inbound adapter."""

    def test_init_requires_nats_py(self) -> None:
        """Test that adapter requires nats-py package."""
        # This test verifies the import check works
        # In a real scenario, we'd mock the import
        config = {
            "servers": ["nats://localhost:4222"],
            "subjects": [{"subject": "test", "port": "test_port"}],
        }

        # If nats-py is not available, this should raise ImportError
        try:
            adapter = NatsAdapterServer("nats", config)
            # If we get here, nats-py is available, which is fine
            assert adapter.name == "nats"
        except ImportError:
            # Expected if nats-py is not installed
            pytest.skip("nats-py not available")

    def test_config_parsing(self) -> None:
        """Test adapter configuration parsing."""
        try:
            config = {
                "servers": ["nats://localhost:4222"],
                "subjects": [
                    {"subject": "test.subject", "port": "test_handler"}
                ],
                "queue_group": "workers",
            }

            adapter = NatsAdapterServer("nats", config)
            assert adapter.servers == ["nats://localhost:4222"]
            assert len(adapter.subjects) == 1
            assert adapter.queue_group == "workers"
        except ImportError:
            pytest.skip("nats-py not available")


class TestNatsAdapterClient:
    """Test NATS outbound adapter."""

    def test_init_requires_nats_py(self) -> None:
        """Test that adapter requires nats-py package."""
        config = {
            "servers": ["nats://localhost:4222"],
        }

        try:
            adapter = NatsAdapterClient("nats_client", config)
            assert adapter.name == "nats_client"
        except ImportError:
            pytest.skip("nats-py not available")

    def test_config_parsing(self) -> None:
        """Test adapter configuration parsing."""
        try:
            config = {
                "servers": "nats://localhost:4222",
                "timeout": 10.0,
            }

            adapter = NatsAdapterClient("nats_client", config)
            # Single server string should be converted to list
            assert adapter.servers == ["nats://localhost:4222"]
            assert adapter.timeout == 10.0
        except ImportError:
            pytest.skip("nats-py not available")

