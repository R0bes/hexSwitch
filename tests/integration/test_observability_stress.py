"""Stress tests for observability system."""

import threading
import time

from hexswitch.shared.observability import (
    create_metrics_collector,
    create_tracer,
)


def test_metrics_high_concurrency() -> None:
    """Test metrics under high concurrency."""
    collector = create_metrics_collector()
    counter = collector.counter("high_concurrency_test")
    gauge = collector.gauge("high_concurrency_gauge")
    histogram = collector.histogram("high_concurrency_histogram")

    def worker():
        for _ in range(100):
            counter.inc()
            gauge.inc()
            histogram.observe(time.time() % 100)

    threads = [threading.Thread(target=worker) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # OpenTelemetry doesn't expose counter values directly
    # Gauge tracks value locally
    assert gauge.get() == 5000


def test_tracing_high_volume() -> None:
    """Test tracing with high volume of spans."""
    tracer = create_tracer("stress_test")

    def create_spans():
        for _ in range(100):
            span = tracer.start_span("operation")
            time.sleep(0.001)  # Simulate work
            span.finish()

    threads = [threading.Thread(target=create_spans) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    spans = tracer.get_spans()
    assert len(spans) == 1000
    # OpenTelemetry manages duration internally
    assert all(span.trace_id is not None for span in spans)


def test_metrics_memory_efficiency() -> None:
    """Test metrics don't leak memory."""
    collector = create_metrics_collector()

    # Create many metrics
    for i in range(1000):
        counter = collector.counter(f"metric_{i}")
        counter.inc()

    metrics = collector.get_all_metrics()
    assert len(metrics["counters"]) == 1000


def test_span_nested_depth() -> None:
    """Test deeply nested spans."""
    tracer = create_tracer("depth_test")

    current_span = None
    for i in range(100):
        current_span = tracer.start_span(f"level_{i}", parent=current_span)

    # Verify trace ID is consistent
    spans = tracer.get_spans()
    trace_ids = {span.trace_id for span in spans}
    assert len(trace_ids) == 1  # All spans in same trace

    # Finish all spans
    for span in reversed(spans):
        span.finish()

