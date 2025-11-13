FROM python:3.11-slim

WORKDIR /app

# Copy service requirements first
COPY services/master_data_service/requirements.txt ./service_requirements.txt

# Copy root requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r service_requirements.txt

# Copy core and shared modules
COPY core/ ./core/
COPY shared/ ./shared/

# Copy service code
COPY services/master_data_service/ ./services/master_data_service/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Run service with uvicorn
CMD ["uvicorn", "services.master_data_service.main:app", "--host", "0.0.0.0", "--port", "8080"]
