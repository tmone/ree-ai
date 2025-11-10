FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy service requirements first
COPY services/auth_service/requirements.txt ./service_requirements.txt

# Copy root requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r service_requirements.txt

# Copy core and shared modules
COPY core/ ./core/
COPY shared/ ./shared/

# Copy service code
COPY services/auth_service/ ./services/auth_service/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Run service with uvicorn
CMD ["uvicorn", "services.auth_service.main:app", "--host", "0.0.0.0", "--port", "8080"]
