"""Extended unit tests for Envelope class."""



from hexswitch.shared.envelope import Envelope


class TestEnvelopeObservability:
    """Test Envelope observability features."""

    def test_start_span(self) -> None:
        """Test starting a span from envelope."""
        envelope = Envelope(path="/test", method="GET")
        span = envelope.start_span("test_span")
        assert span is not None
        assert envelope._span == span
        span.finish()

    def test_start_span_with_tags(self) -> None:
        """Test starting a span with tags."""
        envelope = Envelope(path="/test", method="GET")
        span = envelope.start_span("test_span", tags={"key": "value"})
        assert span is not None
        span.finish()

    def test_finish_span(self) -> None:
        """Test finishing a span."""
        envelope = Envelope(path="/test", method="GET")
        span = envelope.start_span("test_span")
        envelope.finish_span()  # Should not raise
        assert envelope._span is not None

    def test_finish_span_with_error(self) -> None:
        """Test finishing a span with error message."""
        envelope = Envelope(path="/test", method="GET", error_message="Test error")
        span = envelope.start_span("test_span")
        envelope.finish_span()  # Should add error tags
        span.finish()

    def test_finish_span_with_data(self) -> None:
        """Test finishing a span with data."""
        envelope = Envelope(path="/test", method="GET", data={"result": "success"})
        span = envelope.start_span("test_span")
        envelope.finish_span()  # Should add success tags
        span.finish()

    def test_get_span(self) -> None:
        """Test getting span from envelope."""
        envelope = Envelope(path="/test", method="GET")
        assert envelope.get_span() is None
        span = envelope.start_span("test_span")
        assert envelope.get_span() == span
        span.finish()

    def test_has_trace_context(self) -> None:
        """Test checking trace context."""
        envelope = Envelope(path="/test", method="GET")
        assert not envelope.has_trace_context()
        envelope.trace_id = "12345"
        assert envelope.has_trace_context()

    def test_create_child_context(self) -> None:
        """Test creating child context."""
        envelope = Envelope(path="/test", method="GET")
        context = envelope.create_child_context()
        assert "trace_id" in context
        assert "span_id" in context
        assert envelope.trace_id is not None

    def test_create_child_context_with_existing_trace(self) -> None:
        """Test creating child context with existing trace."""
        envelope = Envelope(path="/test", method="GET", trace_id="12345", span_id="67890")
        context = envelope.create_child_context()
        assert context["trace_id"] == "12345"
        assert context["parent_span_id"] == "67890"
        assert envelope.parent_span_id == "67890"

    def test_envelope_context_manager(self) -> None:
        """Test envelope as context manager."""
        envelope = Envelope(path="/test", method="GET")
        with envelope:
            assert envelope._span is not None
        # Span should be finished after context exit

    def test_envelope_context_manager_with_exception(self) -> None:
        """Test envelope context manager with exception."""
        envelope = Envelope(path="/test", method="GET")
        try:
            with envelope:
                raise ValueError("test error")
        except ValueError:
            pass
        # Span should be finished with error tag

