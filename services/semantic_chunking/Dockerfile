FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared models
COPY shared /app/shared

# Copy service code
COPY services/semantic_chunking /app/services/semantic_chunking

# Set Python path
ENV PYTHONPATH=/app

WORKDIR /app/services/semantic_chunking

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
