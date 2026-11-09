# --- Stage 1: Build Frontend SPA ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# --- Stage 2: Production Python Backend ---
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    HF_HOME=/app/models_cache \
    TRANSFORMERS_CACHE=/app/models_cache \
    TORCH_HOME=/app/models_cache

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./backend/
COPY docs/ ./docs/
COPY sample_resume.txt ./
COPY README.md ./

# Pre-index textbook corpus during build so container starts instantly
RUN python backend/scripts/ingest_corpus.py && chmod -R 777 /app/models_cache /app/backend

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 8000

# Start script: launch FastAPI uvicorn directly on the port provided by Render
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --app-dir backend"]

