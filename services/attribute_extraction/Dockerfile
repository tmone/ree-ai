FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy core and shared modules
COPY core/ ./core/
COPY shared/ ./shared/

# Copy service code
COPY services/attribute_extraction/ ./services/attribute_extraction/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8084

# Run service with uvicorn
CMD ["uvicorn", "services.attribute_extraction.main:app", "--host", "0.0.0.0", "--port", "8084"]
