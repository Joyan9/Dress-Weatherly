FROM python:3.11-slim

WORKDIR /app

# Install any needed system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scripts/ ./scripts/
COPY .env* ./

# Set environment variables will be provided via GitHub Actions

ENTRYPOINT ["python", "scripts/run_pipeline.py"]


