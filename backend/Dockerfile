# syntax=docker/dockerfile:1
# Multi-stage Dockerfile for FastAPI LLM Chatbot Backend

# ==========================================
# Stage 1: Build Dependencies
# ==========================================
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install uv for fast, deterministic dependency resolution
RUN pip install --no-cache-dir uv

# Copy dependency specifications
COPY pyproject.toml requirements.txt ./

# Create isolated virtualenv and install pinned requirements
RUN uv venv /app/.venv && \
    uv pip install --no-cache -r requirements.txt

# ==========================================
# Stage 2: Production Runtime
# ==========================================
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install curl for healthcheck validation and libsndfile1 for audio/soundfile libraries
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl libsndfile1 && \
    rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user and persistent SQLite /data directory
RUN useradd -u 10001 -d /app -s /bin/bash appuser && \
    mkdir -p /data /app && \
    chown -R appuser:appuser /data /app && \
    chmod 777 /data

# Copy isolated virtualenv from builder stage
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application source code
COPY --chown=appuser:appuser . /app/

# Switch to non-root user for principle of least privilege
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
