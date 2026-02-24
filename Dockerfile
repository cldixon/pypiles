FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /tmp/ray

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

COPY pypiles/ ./pypiles/
COPY server.py ./

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

ENV RAY_NUM_CPUS=4
ENV RAY_OBJECT_STORE_MEMORY=100000000
ENV RAY_DISABLE_DOCKER_CPU_WARNING=1
ENV RAY_DEDUP_LOGS=0

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn server:app --host :: --port $PORT"]
