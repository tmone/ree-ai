FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY services/reranking/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared models
COPY shared/ /app/shared/

# Copy service code
COPY services/reranking/ /app/

# Expose port
EXPOSE 8080

# Run service
CMD ["python", "main.py"]
