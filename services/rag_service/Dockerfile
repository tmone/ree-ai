FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared models
COPY shared /app/shared

# Copy service code
COPY services/rag_service /app/services/rag_service

# Set Python path
ENV PYTHONPATH=/app

WORKDIR /app/services/rag_service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
