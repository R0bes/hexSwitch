"""gRPC handlers for example2 service."""

from example2_service.application.handlers.grpc_handlers import (
    call_example1_handler,
    call_example3_handler,
    grpc_create_example_handler,
    grpc_delete_example_handler,
    grpc_get_example_handler,
    grpc_list_examples_handler,
    grpc_update_example_handler,
)

__all__ = [
    "grpc_get_example_handler",
    "grpc_create_example_handler",
    "grpc_list_examples_handler",
    "grpc_update_example_handler",
    "grpc_delete_example_handler",
    "call_example1_handler",
    "call_example3_handler",
]

