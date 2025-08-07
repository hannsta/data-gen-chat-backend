# Use the official Playwright Python image with browsers pre-installed
FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Ensure Playwright browsers are installed (should already be in the base image)
RUN playwright install --with-deps chromium

# Create a non-root user for security (optional but recommended)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port that the app runs on
EXPOSE 8000

# Use the start_server.py script to run the application
CMD ["python", "start_server.py", "--host", "0.0.0.0", "--port", "8000", "--no-reload"] 