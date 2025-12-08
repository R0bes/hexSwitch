# Multi-stage Dockerfile for HexSwitch
# Build stage
FROM python:3.12-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir --user -e .

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy installed package from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

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

