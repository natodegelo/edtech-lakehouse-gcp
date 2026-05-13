FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY load.py .

ENV GCS_PROJECT=edtech-lakehouse \
    GCS_RAW_BUCKET=edtech-raw-dev \
    BQ_DATASET=raw_dev \
    BQ_LOCATION=us-east1

CMD ["python", "load.py"]