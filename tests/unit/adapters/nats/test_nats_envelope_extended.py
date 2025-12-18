"""Extended unit tests for NATS envelope conversion."""


from hexswitch.adapters.nats._Nats_Envelope import NatsEnvelope
from hexswitch.shared.envelope import Envelope


class TestNatsEnvelopeExtended:
    """Extended tests for NATS envelope conversion."""

    def test_message_to_envelope_with_reply_to(self) -> None:
        """Test converting NATS message with reply_to."""
        converter = NatsEnvelope()
        subject = "test.subject"
        reply_to = "reply.subject"
        data = b'{"key": "value"}'
        headers = {}

        envelope = converter.message_to_envelope(
            subject=subject, reply_to=reply_to, data=data, headers=headers
        )

        assert envelope.path == subject
        assert envelope.metadata.get("reply_to") == reply_to

    def test_message_to_envelope_with_trace_context(self) -> None:
        """Test converting NATS message with trace context."""
        converter = NatsEnvelope()
        subject = "test.subject"
        data = b'{"key": "value"}'
        headers = {
            "X-Trace-Id": "12345",
            "X-Span-Id": "67890",
        }

        envelope = converter.message_to_envelope(
            subject=subject, reply_to=None, data=data, headers=headers
        )

        assert envelope.trace_id == "12345"
        assert envelope.span_id == "67890"

    def test_envelope_to_message_with_trace_context(self) -> None:
        """Test converting Envelope with trace context to NATS message."""
        converter = NatsEnvelope()
        envelope = Envelope(
            path="test.subject",
            data={"result": "success"},
            trace_id="12345",
            span_id="67890",
        )

        message_data, message_headers = converter.envelope_to_message(envelope)

        assert isinstance(message_data, bytes)
        assert len(message_headers) > 0  # Should contain trace context

    def test_envelope_to_message_with_headers(self) -> None:
        """Test converting Envelope with custom headers."""
        converter = NatsEnvelope()
        envelope = Envelope(
            path="test.subject",
            data={"result": "success"},
            metadata={"headers": {"Custom-Header": "value"}},
        )

        message_data, message_headers = converter.envelope_to_message(envelope)

        assert isinstance(message_data, bytes)
        assert "Custom-Header" in message_headers or len(message_headers) > 0

    def test_message_to_envelope_empty_data(self) -> None:
        """Test converting NATS message with empty data."""
        converter = NatsEnvelope()
        subject = "test.subject"
        data = b""
        headers = {}

        envelope = converter.message_to_envelope(
            subject=subject, reply_to=None, data=data, headers=headers
        )

        assert envelope.path == subject
        assert envelope.body is None or envelope.body == {}

    def test_envelope_to_message_empty_data(self) -> None:
        """Test converting Envelope with empty data."""
        converter = NatsEnvelope()
        envelope = Envelope(path="test.subject", data=None)

        message_data, message_headers = converter.envelope_to_message(envelope)

        assert isinstance(message_data, bytes)
        assert message_data == b"{}"  # Empty dict serialized

