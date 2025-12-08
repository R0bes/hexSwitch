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

ARG VERSION=0.1.0
ENV HEXSWITCH_VERSION=${VERSION}

LABEL org.opencontainers.image.title="HexSwitch"
LABEL org.opencontainers.image.description="Hexagonal runtime switchboard for config-driven microservices"
LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.vendor="HexSwitch Contributors"

WORKDIR /app

# Copy project files and install package properly
COPY pyproject.toml ./
COPY src/ ./src/

# Install the package (not editable, regular install)
RUN pip install --no-cache-dir .

# Create non-root user for security
RUN useradd -m -u 1000 hexswitch && \
    chown -R hexswitch:hexswitch /app

USER hexswitch

# Set working directory
WORKDIR /app

# Expose port (if needed in the future)
# EXPOSE 8080

# Default command
CMD ["hexswitch", "--help"]

