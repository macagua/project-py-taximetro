FROM python:3.12-slim

# --- uv (fast package manager) ---
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Install OS deps needed by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps (cached layer — only invalidated by lockfile changes)
# .python-version is excluded: FROM python:3.12-slim already provides 3.12
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy application source
COPY . .

# Install the project itself
RUN uv sync --frozen

# Reflex downloads Bun/Node on first compile; persist the cache via volume or
# pre-seed it here with a build-time placeholder key (never used at runtime).
ARG SECRET_KEY=insecure-build-only-key-not-for-production
ARG DEBUG=False
ENV SECRET_KEY=${SECRET_KEY} DEBUG=${DEBUG}
RUN uv run reflex compile

# Remove the build-time key from the final image environment.
# The real key is injected at runtime via docker-compose / --env-file.
ENV SECRET_KEY=""

EXPOSE 3000

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
