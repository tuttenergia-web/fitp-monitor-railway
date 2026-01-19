# STAGE 1: Build environment
FROM python:3.14.2 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Create virtual environment
RUN python -m venv .venv

# Install system dependencies (Tesseract OCR)
RUN apt-get update && apt-get install -y tesseract-ocr

# Install Python dependencies
COPY requirements.txt ./
RUN .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install -r requirements.txt

# STAGE 2: Final image
FROM python:3.14.2-slim

WORKDIR /app

# PaddleOCR dependencies (minimali, compatibili con Fly.io)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy app and virtual environment
COPY --from=builder /app/.venv .venv/
COPY . .

# Entrypoint using virtualenv Python
CMD [".venv/bin/python", "main.py"]