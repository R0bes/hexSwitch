"""Tests for outbound ports.

Note: Outbound ports are now handled directly through the port registry's route() method
with outbound adapters. These tests verify that outbound adapters can be used with ports.
"""

import pytest

from hexswitch.shared.envelope import Envelope
from hexswitch.ports import get_port_registry, reset_port_registry


class TestOutboundPortIntegration:
    """Test outbound adapter integration with ports."""

    def test_outbound_adapter_can_be_used_with_port(self) -> None:
        """Test that outbound adapters can route through ports."""
        reset_port_registry()
        registry = get_port_registry()
        
        # Create mock adapter
        received_envelopes = []
        
        class MockOutboundAdapter:
            def __init__(self):
                self.name = "test_adapter"
            
            def request(self, envelope: Envelope) -> Envelope:
                received_envelopes.append(envelope)
                return Envelope.success({"result": "ok"})
        
        adapter = MockOutboundAdapter()
        
        # Register handler that uses the adapter
        def handler(envelope: Envelope) -> Envelope:
            return adapter.request(envelope)
        
        registry.register_handler("test_outbound_port", handler)
        
        # Route envelope through port
        request_envelope = Envelope(path="/test", method="GET")
        results = registry.route("test_outbound_port", request_envelope)
        
        # Verify adapter was called
        assert len(received_envelopes) == 1
        assert received_envelopes[0].path == "/test"
        assert len(results) == 1
        assert results[0].status_code == 200
        assert results[0].data == {"result": "ok"}
    
    def test_outbound_adapter_passes_envelope_correctly(self) -> None:
        """Test that outbound adapter receives correct envelope."""
        reset_port_registry()
        registry = get_port_registry()
        
        received_envelopes = []
        
        class MockOutboundAdapter:
            def __init__(self):
                self.name = "test_adapter"
            
            def request(self, envelope: Envelope) -> Envelope:
                received_envelopes.append(envelope)
                return Envelope.success({"received": True})
        
        adapter = MockOutboundAdapter()
        
        def handler(envelope: Envelope) -> Envelope:
            return adapter.request(envelope)
        
        registry.register_handler("test_port", handler)
        
        # Call port with complex envelope
        request_envelope = Envelope(
            path="/test",
            method="POST",
            body={"key": "value"},
        )
        results = registry.route("test_port", request_envelope)
        
        # Verify envelope was passed correctly
        assert len(received_envelopes) == 1
        assert received_envelopes[0].path == "/test"
        assert received_envelopes[0].method == "POST"
        assert received_envelopes[0].body == {"key": "value"}
        assert results[0].status_code == 200

