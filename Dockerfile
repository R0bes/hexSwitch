# HexSwitch Framework Base Image
# This image contains the framework and all its dependencies.
# Services can use this as a base image to avoid rebuilding the framework.

FROM python:3.12-slim as hexswitch-base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy framework source
COPY src/hexswitch /app/src/hexswitch
COPY pyproject.toml /app/pyproject.toml

# Install framework and dependencies
RUN pip install --no-cache-dir -e /app/

# Create non-root user for security
RUN useradd -m -u 1000 hexswitch && \
    chown -R hexswitch:hexswitch /app

USER hexswitch

# Health check (optional - can be overridden by services)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import hexswitch; print('OK')" || exit 1

# Default command (can be overridden by services)
CMD ["python", "-c", "import hexswitch; print('HexSwitch Framework Ready')"]

