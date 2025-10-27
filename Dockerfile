# syntax=docker/dockerfile:1.6

# Build stage
FROM python:3.12 AS builder
WORKDIR /code

# Use --mount=type=cache to cache pip downloads between builds
COPY requirements.txt /code/requirements.txt
COPY requirements.build.txt /code/requirements.build.txt
RUN --mount=type=cache,target=/root/.cache/pip,id=pip-cache \
    python -m pip install --upgrade pip wheel \
 && pip wheel -r requirements.txt -w /wheels \
 && pip wheel -r requirements.build.txt -w /wheels

# Copy source code
COPY . /code

# Install dependencies from wheels cache (offline installation)
RUN --mount=type=cache,target=/root/.cache/pip,id=pip-cache \
    pip install --no-index --find-links=/wheels -r requirements.txt \
 && pip install --no-index --find-links=/wheels -r requirements.build.txt

# Run PyInstaller to create a single executable
RUN --mount=type=cache,target=/root/.cache/pip,id=pip-cache \
    pip install --no-index --find-links=/wheels pyinstaller \
 && pyinstaller -F main.py


# Runtime stage
FROM ubuntu:24.04 AS runtime
WORKDIR /app

# Install runner dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy the built executable from the builder stage
COPY --from=builder /code/dist/main /app/main

# Health check
# HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
#   CMD curl -fsS http://localhost:8080/health || exit 1

ENTRYPOINT ["/app/main"]
