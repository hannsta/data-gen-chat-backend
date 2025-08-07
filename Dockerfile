# Use Ubuntu 22.04 with Python 3.11
FROM ubuntu:22.04

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and Python 3.11
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-pip \
    python3.11-dev \
    python3.11-venv \
    wget \
    curl \
    && ln -s /usr/bin/python3.11 /usr/bin/python \
    && ln -s /usr/bin/pip3.11 /usr/bin/pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Install Playwright browsers with system dependencies
RUN playwright install --with-deps chromium

# Create a non-root user for security (optional but recommended)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port that the app runs on
EXPOSE 8000

# Use the start_server.py script to run the application
CMD ["python", "start_server.py", "--host", "0.0.0.0", "--port", "8000", "--no-reload"] 