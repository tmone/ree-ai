FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy shared modules
COPY shared /app/shared
COPY core /app/core

# Expose port
EXPOSE 8080

# Run service
CMD ["python", "-m", "services.user_management.main"]
