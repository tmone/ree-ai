FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy main requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service-specific requirements
COPY services/semantic_chunking/requirements.txt ./semantic_chunking_requirements.txt
RUN pip install --no-cache-dir -r semantic_chunking_requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt')"

# Copy core and shared modules
COPY core/ ./core/
COPY shared/ ./shared/

# Copy service code
COPY services/semantic_chunking/ ./services/semantic_chunking/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Run service
CMD ["python", "services/semantic_chunking/main.py"]
