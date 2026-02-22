# Stage 1: Build SvelteKit frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.12-slim
WORKDIR /app

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy Python project files
COPY pyproject.toml uv.lock ./
COPY pypiles/ ./pypiles/
COPY server.py ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Copy built frontend
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Railway assigns $PORT dynamically; default to 8000 for local use
ENV PORT=8000
EXPOSE 8000

# Start FastAPI with uvicorn, using shell form so $PORT is expanded
CMD uv run uvicorn server:app --host 0.0.0.0 --port $PORT
