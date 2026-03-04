# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-warn-script-location --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime libs (e.g. libpq for postgres if needed, though asyncpg is pure python mostly but sometimes needs deps)
# asyncpg is binary, wheel should be fine. curl for healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Update PATH
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8080

# Healthcheck — Cloud Run injects $PORT (default 8080)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/api/v1/health || exit 1

# Cloud Run injects PORT at runtime. 2 workers sufficient for MVP;
# Cloud Run scales horizontally for higher load.
CMD ["sh", "-c", "exec gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8080} --timeout 120 --keep-alive 5"]
