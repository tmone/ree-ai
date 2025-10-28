FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy core library
COPY core /app/core

# Copy shared models
COPY shared /app/shared

# Copy service code
COPY services/service_registry /app/services/service_registry

# Set Python path
ENV PYTHONPATH=/app

WORKDIR /app/services/service_registry

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
