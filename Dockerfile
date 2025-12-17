# Multi-stage Dockerfile for HexSwitch
# Build stage
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install the package system-wide (will be copied to user location)
RUN pip install --no-cache-dir -e .

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (for potential native extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy project files and install package properly
COPY pyproject.toml ./
COPY src/ ./src/
COPY assets/ ./assets/

# Install the package (not editable, regular install)
RUN pip install --no-cache-dir .

# Create non-root user for security
RUN useradd -m -u 1000 hexswitch && \
    chown -R hexswitch:hexswitch /app

USER hexswitch

# Health check (optional - can be overridden by services)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import hexswitch; print('OK')" || exit 1

# Default command (can be overridden by services)
CMD ["hexswitch", "--help"]
