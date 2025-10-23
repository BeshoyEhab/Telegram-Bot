# =============================================================================
# FILE: Dockerfile
# DESCRIPTION: Docker container configuration
# LOCATION: Project root directory
# PURPOSE: Builds Docker image for the bot application
# USAGE: docker build -t school-bot .
# =============================================================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs backups exports templates

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run database migrations and start bot
CMD alembic upgrade head && python main.py
