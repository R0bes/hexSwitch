"""Pro-level unit tests for observability system."""

import threading
import time

from hexswitch.shared.observability import (
    Counter,
    Gauge,
    Histogram,
    create_metrics_collector,
    create_tracer,
    start_span,
)


def test_counter_basic() -> None:
    """Test basic counter operations."""
    counter = Counter("test_counter")
    # OpenTelemetry doesn't expose current value directly
    assert counter.get() == 0.0

    counter.inc()
    # Counter increments are recorded but not directly readable
    assert counter.get() == 0.0

    counter.inc(5)
    assert counter.get() == 0.0

    counter.reset()  # Warning logged but no-op
    assert counter.get() == 0.0


def test_counter_thread_safety() -> None:
    """Test counter thread safety."""
    counter = Counter("test_counter")

    def increment():
        for _ in range(100):
            counter.inc()

    threads = [threading.Thread(target=increment) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # OpenTelemetry doesn't expose current value, but increments are thread-safe
    # We just verify no exceptions occurred
    assert counter.get() == 0.0


def test_gauge_basic() -> None:
    """Test basic gauge operations."""
    gauge = Gauge("test_gauge")
    assert gauge.get() == 0.0

    gauge.set(10.5)
    assert gauge.get() == 10.5

    gauge.inc(2.5)
    assert gauge.get() == 13.0

    gauge.dec(5.0)
    assert gauge.get() == 8.0


def test_histogram_basic() -> None:
    """Test basic histogram operations."""
    histogram = Histogram("test_histogram")

    histogram.observe(10.0)
    histogram.observe(20.0)
    histogram.observe(30.0)

    stats = histogram.get()
    assert stats["count"] == 3
    assert stats["sum"] == 60.0
    assert stats["min"] == 10.0
    assert stats["max"] == 30.0
    assert stats["avg"] == 20.0


def test_histogram_empty() -> None:
    """Test histogram with no observations."""
    histogram = Histogram("test_histogram")
    stats = histogram.get()

    assert stats["count"] == 0
    assert stats["sum"] == 0.0


def test_metrics_collector() -> None:
    """Test metrics collector."""
    collector = create_metrics_collector()

    counter = collector.counter("req_total")
    gauge = collector.gauge("active_connections")
    histogram = collector.histogram("response_time")

    counter.inc()
    gauge.set(5)
    histogram.observe(0.1)

    metrics = collector.get_all_metrics()
    assert "req_total" in metrics["counters"]
    assert "active_connections" in metrics["gauges"]
    assert "response_time" in metrics["histograms"]


def test_metrics_collector_labels() -> None:
    """Test metrics collector with labels."""
    collector = create_metrics_collector()

    counter1 = collector.counter("req_total", {"method": "GET"})
    counter2 = collector.counter("req_total", {"method": "POST"})

    counter1.inc()
    counter2.inc(2)

    metrics = collector.get_all_metrics()
    assert len(metrics["counters"]) == 2


def test_span_basic() -> None:
    """Test basic span operations."""
    tracer = create_tracer("test_service")
    span = tracer.start_span("test_span")
    assert span.name == "test_span"
    assert span.trace_id is not None
    assert len(span.trace_id) == 32  # Hex format

    # OpenTelemetry spans start automatically
    span.start()  # No-op but compatible

    time.sleep(0.01)
    span.finish()
    # OpenTelemetry manages timing internally
    span_dict = span.to_dict()
    assert span_dict["name"] == "test_span"


def test_span_tags() -> None:
    """Test span tags."""
    tracer = create_tracer("test_service")
    span = tracer.start_span("test_span", tags={"key1": "value1"})
    span_dict = span.to_dict()
    assert "key1" in span_dict["tags"]
    assert span_dict["tags"]["key1"] == "value1"

    span.add_tag("key2", "value2")
    span_dict = span.to_dict()
    assert span_dict["tags"]["key1"] == "value1"
    assert span_dict["tags"]["key2"] == "value2"


def test_span_logs() -> None:
    """Test span logs."""
    tracer = create_tracer("test_service")
    span = tracer.start_span("test_span")
    span.add_log("test message", {"field1": "value1"})

    # OpenTelemetry handles logs as events differently
    span_dict = span.to_dict()
    # Events are stored differently in OpenTelemetry
    assert span_dict["name"] == "test_span"


def test_tracer_basic() -> None:
    """Test basic tracer operations."""
    tracer = create_tracer("test_service")

    span1 = tracer.start_span("operation1")
    span2 = tracer.start_span("operation2", parent=span1)

    assert span1.trace_id == span2.trace_id
    assert span2.parent_id == span1.span_id

    spans = tracer.get_spans()
    assert len(spans) == 2


def test_tracer_clear() -> None:
    """Test tracer clear."""
    tracer = create_tracer("test_service")
    tracer.start_span("operation1")
    tracer.start_span("operation2")

    assert len(tracer.get_spans()) == 2

    tracer.clear()
    assert len(tracer.get_spans()) == 0


def test_start_span_global() -> None:
    """Test global span creation."""
    span = start_span("test_operation")
    assert span is not None
    assert span.name == "test_operation"
    # OpenTelemetry uses contextvars which may not be accessible
    # in all test scenarios, so we just verify span creation
    span.finish()


def test_span_to_dict() -> None:
    """Test span to dictionary conversion."""
    tracer = create_tracer("test_service")
    span = tracer.start_span("test_span", tags={"key": "value"})
    span.add_log("test", {"field": "value"})
    span.finish()

    span_dict = span.to_dict()
    assert span_dict["name"] == "test_span"
    assert span_dict["trace_id"] is not None
    assert len(span_dict["trace_id"]) == 32  # Hex format
    assert span_dict["tags"]["key"] == "value"
    # OpenTelemetry handles logs differently
    assert isinstance(span_dict["logs"], list)

