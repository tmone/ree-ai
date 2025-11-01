FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy core and shared modules
COPY core/ ./core/
COPY shared/ ./shared/

# Copy service code
COPY services/rag_service/ ./services/rag_service/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Run service with uvicorn
CMD ["uvicorn", "services.rag_service.main:app", "--host", "0.0.0.0", "--port", "8080"]
