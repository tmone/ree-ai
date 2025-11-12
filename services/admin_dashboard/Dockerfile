FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy core and shared modules
COPY core/ ./core/
COPY shared/ ./shared/

# Copy service code
COPY services/admin_dashboard/ ./services/admin_dashboard/

# Set Python path
ENV PYTHONPATH=/app

EXPOSE 8080

# Run service
CMD ["python", "-m", "services.admin_dashboard.main"]