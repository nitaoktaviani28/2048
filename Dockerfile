# ─────────────────────────────────────────────
#  Stage 1 – Builder
# ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies in an isolated layer for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────
#  Stage 2 – Runtime
# ─────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="debuglifeindonesia"
LABEL org.opencontainers.image.title="2048 Game – FastAPI"
LABEL org.opencontainers.image.description="2048 puzzle game served via FastAPI + Uvicorn"
LABEL org.opencontainers.image.version="1.0.0"

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY . .


# Expose the application port
EXPOSE 8080

# Run Uvicorn bound to all interfaces on port 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
