# Production Dockerfile for Koyeb Deployment
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for scipy/numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application files
COPY main.py .
COPY convert_audio.py .

# Copy the evaluation engine
COPY evaluation_engine ./evaluation_engine

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
