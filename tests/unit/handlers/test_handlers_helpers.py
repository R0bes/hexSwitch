"""Unit tests for handler helpers."""

import json

from hexswitch.shared.helpers import (
    extract_query_params,
    format_response,
    parse_path_params,
    parse_request_body,
    prepare_request_data,
)


def test_parse_path_params():
    """Test parsing path parameters."""
    params = parse_path_params("/orders/123", "/orders/:id")
    assert params == {"id": "123"}

    params = parse_path_params("/orders/123/items/456", "/orders/:order_id/items/:item_id")
    assert params == {"order_id": "123", "item_id": "456"}


def test_parse_path_params_no_match():
    """Test parsing path parameters with no match."""
    params = parse_path_params("/orders/123", "/products/:id")
    assert params == {}


def test_parse_request_body():
    """Test parsing request body."""
    body = '{"key": "value"}'
    result = parse_request_body(body)
    assert result == {"key": "value"}


def test_parse_request_body_empty():
    """Test parsing empty request body."""
    assert parse_request_body(None) is None
    assert parse_request_body("") is None


def test_parse_request_body_invalid_json():
    """Test parsing invalid JSON."""
    result = parse_request_body("invalid json")
    assert result is None


def test_format_response():
    """Test formatting response."""
    response = format_response({"key": "value"})
    assert response == {"key": "value"}

    response = format_response({"error": "Not found"}, 404)
    assert response == (404, {"error": "Not found"})


def test_format_response_tuple():
    """Test formatting response that's already a tuple."""
    response = format_response((404, {"error": "Not found"}))
    assert response == (404, {"error": "Not found"})


def test_extract_query_params():
    """Test extracting query parameters."""
    params = extract_query_params({"id": ["123"], "name": "test"})
    assert params == {"id": "123", "name": "test"}


def test_prepare_request_data():
    """Test preparing request data."""
    data = prepare_request_data(
        path="/orders/123",
        route_path="/orders/:id",
        method="GET",
        query_params={"filter": "active"},
        headers={"Content-Type": "application/json"},
        body='{"key": "value"}',
    )

    assert data["path"] == "/orders/123"
    assert data["method"] == "GET"
    assert data["path_params"] == {"id": "123"}
    assert data["query_params"] == {"filter": "active"}
    assert data["headers"]["Content-Type"] == "application/json"
    assert data["body"] == {"key": "value"}

