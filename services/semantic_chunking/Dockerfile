FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy core and shared modules
COPY core/ ./core/
COPY shared/ ./shared/

# Copy service code
COPY services/semantic_chunking/ ./services/semantic_chunking/

# Set Python path
ENV PYTHONPATH=/app

# Run service
CMD ["python", "-m", "services.semantic_chunking.main"]