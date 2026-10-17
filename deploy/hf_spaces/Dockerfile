FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Cai dat Qdrant binary cho Linux x86_64
RUN curl -L https://github.com/qdrant/qdrant/releases/download/v1.9.0/qdrant-x86_64-unknown-linux-gnu.tar.gz \
    | tar -xz -C /usr/local/bin/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY data/processed/ data/processed/
COPY data/embeddings/ data/embeddings/
COPY scripts/ scripts/
COPY deploy/hf_spaces/entrypoint.sh entrypoint.sh

RUN chmod +x entrypoint.sh /usr/local/bin/qdrant

ENV HF_HOME=/root/.cache/huggingface \
    QDRANT_URL=http://localhost:6333 \
    PYTHONUNBUFFERED=1

EXPOSE 8501

ENTRYPOINT ["/app/entrypoint.sh"]
