# Crypto-Replicator - NIS2Shield Encrypted Twin
# Multi-stage build for smaller image

# ==============================================================================
# Stage 1: Builder
# ==============================================================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ==============================================================================
# Stage 2: Production
# ==============================================================================
FROM python:3.11-slim

LABEL org.opencontainers.image.title="NIS2Shield Crypto-Replicator"
LABEL org.opencontainers.image.description="Encrypted database replication for NIS2 compliance"
LABEL org.opencontainers.image.vendor="NIS2Shield"
LABEL org.opencontainers.image.source="https://github.com/nis2shield/infrastructure"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r nis2 && useradd -r -g nis2 nis2user

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY crypto_replicator/ ./crypto_replicator/

# Create directories for keys and data
RUN mkdir -p /keys /data && chown -R nis2user:nis2 /keys /data

# Switch to non-root user
USER nis2user

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default configuration
ENV DATABASE_URL="postgresql://nis2user:password@db:5432/nis2_app"
ENV LISTEN_CHANNEL="nis2_changes"
ENV RSA_PUBLIC_KEY_PATH="/keys/cloud.pub"
ENV DEBUG="false"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8080), timeout=5)" || exit 0

# Run the service
CMD ["python", "-m", "crypto_replicator.main"]
