FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python test dependencies
COPY tests/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy core library (needed for imports)
COPY core /app/core

# Copy shared models
COPY shared /app/shared

# Copy test files
COPY tests /app/tests

ENV PYTHONPATH=/app

# Default command (can be overridden)
CMD ["pytest", "/app/tests", "-v", "--tb=short"]
