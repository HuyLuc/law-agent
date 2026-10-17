#!/bin/bash
set -e

echo "=== [1/4] Khoi dong Qdrant ==="
if [ "$QDRANT_URL" = "http://localhost:6333" ] || [ -z "$QDRANT_URL" ]; then
    echo "Chay Qdrant local trong container..."
    qdrant &
    # Cho Qdrant san sang
    while ! curl -s http://localhost:6333/healthz > /dev/null; do
        sleep 1
    done
    echo "Qdrant da san sang!"

    # Kiem tra xem collection labor_law da ton tai chua, neu chua thi index du lieu
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:6333/collections/labor_law || true)
    if [ "$STATUS_CODE" != "200" ]; then
        echo "Dang index 379 chunks vao Qdrant..."
        python -m src.ingestion.index_qdrant
    else
        echo "Collection labor_law da co san."
    fi
else
    echo "Ket noi den Qdrant tu xa: $QDRANT_URL"
fi

echo "=== [2/4] Khoi dong FastAPI Backend ==="
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 &
while ! curl -s http://127.0.0.1:8000/health > /dev/null; do
    sleep 1
done
echo "FastAPI backend da san sang!"

echo "=== [3/4] Export ONNX Reranker neu can ==="
if [ ! -f "data/models/bge-reranker-base.onnx" ]; then
    echo "Chuyen doi reranker sang ONNX de tang toc CPU..."
    python -m scripts.export_onnx_reranker || true
fi

echo "=== [4/4] Khoi dong Streamlit UI ==="
export API_URL="http://127.0.0.1:8000"
exec streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0 --browser.gatherUsageStats false
