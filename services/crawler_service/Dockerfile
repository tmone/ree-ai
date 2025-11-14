FROM python:3.11-slim

# Install system dependencies for Crawl4AI
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy crawler-specific requirements
COPY services/crawler_service/requirements-crawler.txt .
RUN pip install --no-cache-dir -r requirements-crawler.txt

# Copy shared code
COPY shared/ /app/shared/
COPY core/ /app/core/

# Copy service code
COPY services/crawler_service/ /app/services/crawler_service/

# Set environment variables for Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

EXPOSE 8080

CMD ["python", "-m", "services.crawler_service.main"]
