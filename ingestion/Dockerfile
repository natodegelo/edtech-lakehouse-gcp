FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ingest.py .

ENV GCS_PROJECT=edtech-lakehouse \
    GCS_RAW_BUCKET=edtech-raw-dev \
    GCS_QUARANTINE_BUCKET=edtech-quarantine-dev \
    DATA_DIR=/app/data

CMD ["python", "ingest.py"]