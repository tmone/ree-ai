FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared models
COPY shared /app/shared

# Copy service code
COPY services/core_gateway /app/services/core_gateway

# Set Python path
ENV PYTHONPATH=/app

WORKDIR /app/services/core_gateway

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
