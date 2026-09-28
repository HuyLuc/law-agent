FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY data/processed/ data/processed/
COPY data/embeddings/ data/embeddings/

ENV HF_HOME=/root/.cache/huggingface

EXPOSE 8000 8501
