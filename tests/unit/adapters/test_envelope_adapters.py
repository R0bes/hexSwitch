"""Tests for Envelope-based adapter conversions."""

import json
import pytest

from hexswitch.shared.envelope import Envelope
from hexswitch.adapters.http import HttpAdapterServer, HttpAdapterClient


class TestHttpAdapterEnvelope:
    """Test HTTP adapter Envelope conversion."""

    def test_http_adapter_creates_envelope_from_request(self) -> None:
        """Test that HTTP adapter creates Envelope from HTTP request."""
        config = {
            "port": 8000,
            "base_path": "",
            "routes": [
                {
                    "path": "/test",
                    "method": "POST",
                    "port": "test_port",
                }
            ],
        }
        
        adapter = HttpAdapterServer("http", config)
        
        # Mock handler that checks Envelope
        def test_handler(envelope: Envelope) -> Envelope:
            assert envelope.path == "/test"
            assert envelope.method == "POST"
            assert envelope.body == {"key": "value"}
            return Envelope.success({"status": "ok"})
        
        # Register handler
        from hexswitch.ports import get_port_registry
        registry = get_port_registry()
        registry.register_handler("test_port", test_handler)
        
        # Test would require actual HTTP server, so we'll test the conversion logic separately
        # This is a placeholder test structure


class TestHttpClientAdapterEnvelope:
    """Test HTTP client adapter Envelope conversion."""

    def test_http_client_adapter_converts_envelope_to_request(self) -> None:
        """Test that HTTP client adapter converts Envelope to HTTP request."""
        config = {
            "base_url": "https://api.example.com",
            "timeout": 30,
        }
        
        adapter = HttpAdapterClient("http_client", config)
        
        # Create Envelope
        envelope = Envelope(
            path="/users",
            method="POST",
            body={"name": "John"},
            headers={"Authorization": "Bearer token"},
        )
        
        # Note: This test requires the adapter to be connected
        # We'll test the conversion logic separately


class TestEnvelopeConversion:
    """Test Envelope conversion utilities."""

    def test_envelope_metadata_stores_protocol_data(self) -> None:
        """Test that Envelope metadata stores protocol-agnostic data."""
        envelope = Envelope(
            path="/test",
            metadata={
                "session_id": "session_123",
                "cookies": {"session": "abc"},
                "trace_id": "trace_123",
            },
        )
        
        assert envelope.metadata["session_id"] == "session_123"
        assert envelope.metadata["cookies"] == {"session": "abc"}
        assert envelope.metadata["trace_id"] == "trace_123"
    
    def test_envelope_success_factory(self) -> None:
        """Test Envelope.success() factory method."""
        envelope = Envelope.success({"order_id": "123"})
        assert envelope.status_code == 200
        assert envelope.data == {"order_id": "123"}
        assert envelope.error_message is None
    
    def test_envelope_error_factory(self) -> None:
        """Test Envelope.error() factory method."""
        envelope = Envelope.error(404, "Not found")
        assert envelope.status_code == 404
        assert envelope.error_message == "Not found"
        assert envelope.data is None

