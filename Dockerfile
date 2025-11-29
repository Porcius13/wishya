FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Update package lists and install missing font packages manually
# This avoids the --with-deps flag which tries to install obsolete packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    fonts-unifont \
    fonts-liberation \
    fonts-dejavu-core \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers WITHOUT --with-deps flag
# The base image already has most dependencies, we just need the browser
RUN playwright install chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Run the application with gunicorn for production
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --max-requests 1000 --max-requests-jitter 100 --preload
