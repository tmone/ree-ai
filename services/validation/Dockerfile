FROM python:3.11-slim

WORKDIR /app

# Copy main requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service-specific requirements
COPY services/validation/requirements.txt ./validation_requirements.txt
RUN pip install --no-cache-dir -r validation_requirements.txt

# Copy core and shared modules
COPY core/ ./core/
COPY shared/ ./shared/

# Copy service code
COPY services/validation/ ./services/validation/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Run service
CMD ["python", "services/validation/main.py"]
