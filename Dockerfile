# Use Python 3.11 official image
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies needed for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Make startup script executable
RUN chmod +x startup.sh

# Install Playwright browsers with system dependencies
RUN playwright install --with-deps chromium

# Note: Running as root for now to avoid Playwright permission issues
# In production, you might want to create a proper non-root user setup

# Expose the port that the app runs on (Railway will set PORT dynamically)
EXPOSE 8000

# Use startup script for better debugging
# Railway will override this command via startCommand in railway.toml
CMD ["./startup.sh"] 