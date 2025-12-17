# Example3 Service Dockerfile - WebSocket/MCP Service
# Uses hexswitch-base from registry

FROM registry.schwende.lan:5000/hexswitch-base:latest

WORKDIR /app

# Copy service code (relative to service directory)
COPY pyproject.toml /app/service-pyproject.toml
COPY src /app/src

# Install service (framework already installed in base image)
RUN pip install --no-cache-dir /app/service-pyproject.toml

# Copy service configuration
COPY hex-config.yaml /app/hex-config.yaml

# Override health check for service
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import example3_service; print('Service OK')" || exit 1

# Run service
CMD ["python", "-m", "example3_service.main", "run", "--config", "/app/hex-config.yaml"]
