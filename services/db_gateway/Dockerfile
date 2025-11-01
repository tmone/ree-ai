FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install asyncpg for Postgres async access
RUN pip install --no-cache-dir asyncpg==0.29.0

# Copy core and shared modules
COPY core/ ./core/
COPY shared/ ./shared/

# Copy service code
COPY services/db_gateway/ ./services/db_gateway/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Run service with uvicorn
CMD ["uvicorn", "services.db_gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]
