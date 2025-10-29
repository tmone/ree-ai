FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY shared/ ./shared/

# Copy service code
COPY services/price_suggestion/ ./services/price_suggestion/

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Run service
CMD ["uvicorn", "services.price_suggestion.main:app", "--host", "0.0.0.0", "--port", "8080"]
