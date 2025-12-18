"""Unit tests for metrics handler."""

from unittest.mock import MagicMock, patch

import pytest

from hexswitch.handlers.metrics import metrics_handler
from hexswitch.shared.envelope import Envelope


class TestMetricsHandler:
    """Test metrics handler."""

    def test_metrics_handler_returns_prometheus_format(self) -> None:
        """Test metrics handler returns Prometheus format."""
        envelope = Envelope(path="/metrics", method="GET")

        with patch(
            "hexswitch.handlers.metrics.get_global_metrics_collector"
        ) as mock_collector:
            mock_metrics = MagicMock()
            mock_metrics.get_all_metrics.return_value = {
                "counters": {"test_counter": 10},
                "gauges": {"test_gauge": 5},
                "histograms": {},
            }
            mock_collector.return_value = mock_metrics

            response = metrics_handler(envelope)

            assert response.status_code == 200
            assert "metrics" in response.data
            metrics_text = response.data["metrics"]
            assert isinstance(metrics_text, str)
            assert "test_counter" in metrics_text or "#" in metrics_text

    def test_metrics_handler_with_empty_metrics(self) -> None:
        """Test metrics handler with empty metrics."""
        envelope = Envelope(path="/metrics", method="GET")

        with patch(
            "hexswitch.handlers.metrics.get_global_metrics_collector"
        ) as mock_collector:
            mock_metrics = MagicMock()
            mock_metrics.get_all_metrics.return_value = {
                "counters": {},
                "gauges": {},
                "histograms": {},
            }
            mock_collector.return_value = mock_metrics

            response = metrics_handler(envelope)

            assert response.status_code == 200
            assert "metrics" in response.data

    def test_metrics_handler_with_labeled_metrics(self) -> None:
        """Test metrics handler with labeled metrics."""
        envelope = Envelope(path="/metrics", method="GET")

        with patch(
            "hexswitch.handlers.metrics.get_global_metrics_collector"
        ) as mock_collector:
            mock_metrics = MagicMock()
            mock_metrics.get_all_metrics.return_value = {
                "counters": {"test_counter{method=GET}": 5},
                "gauges": {},
                "histograms": {},
            }
            mock_collector.return_value = mock_metrics

            response = metrics_handler(envelope)

            assert response.status_code == 200
            assert "metrics" in response.data
            metrics_text = response.data["metrics"]
            assert "test_counter" in metrics_text

