FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy core and shared modules
COPY core/ ./core/
COPY shared/ ./shared/

# Copy service code
COPY services/service_registry/ ./services/service_registry/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run service
CMD ["python", "services/service_registry/main.py"]
