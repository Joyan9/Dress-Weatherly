FROM python:3.11-slim

WORKDIR /app

# install dependencies
RUN apt-get-update & apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/ ./scripts
COPY .env* ./

ENTRYPOINT ["python", "scripts/run_pipeline.py"]