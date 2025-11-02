FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY core/ ./core/
COPY shared/ ./shared/

# Copy service code
COPY services/response_evaluator/ ./services/response_evaluator/

# Set working directory to service
WORKDIR /app/services/response_evaluator

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)"

# Run service
CMD ["python", "main.py"]
