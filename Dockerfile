FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from scripts/ dir to /app/scripts in the container
COPY scripts/ /app/scripts/
COPY . .


# Use CMD instead of ENTRYPOINT for flexibility
CMD ["python", "scripts/run_pipeline.py"]