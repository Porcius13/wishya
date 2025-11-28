FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Set environment variables
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]

