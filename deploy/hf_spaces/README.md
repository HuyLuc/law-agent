---
title: VN Labor Law Agent
emoji: ⚖️
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 8501
pinned: false
license: mit
---

# ⚖️ VN Labor Law Agent - Hugging Face Space

Agent AI hỗ trợ tra cứu và tư vấn Luật Lao động Việt Nam được xây dựng bằng **LangGraph**, **Hybrid Search (Dense + Sparse)**, **Reranker ONNX**, và các công cụ kiểm tra trích dẫn & rà soát hợp đồng.

## 🚀 Hướng dẫn triển khai lên Hugging Face Spaces (CPU Miễn phí)

### Cách 1: Triển khai qua giao diện Web của Hugging Face
1. Truy cập [Hugging Face Spaces](https://huggingface.co/spaces) và bấm **Create new Space**.
2. Đặt tên Space (ví dụ `vn-labor-law-agent`), chọn **Docker** (Blank) và phần cứng **CPU Basic (miễn phí)**.
3. Trong phần **Settings** -> **Variables and secrets**, thêm Secret:
   - `GEMINI_API_KEY`: Key Google Gemini của bạn.
   - `GROQ_API_KEY`: (Tùy chọn) Key Groq để dự phòng khi Gemini cạn quota.
   - `LANGFUSE_PUBLIC_KEY` & `LANGFUSE_SECRET_KEY`: (Tùy chọn) Key Langfuse nếu muốn theo dõi observability.
4. Clone repo Space về máy hoặc đẩy thư mục này lên Space:
   ```bash
   git remote add space https://huggingface.co/spaces/<your-username>/<space-name>
   git push space master
   ```

### Cách 2: Chạy thử cục bộ bằng Docker image của Space
```bash
docker build -t vn-labor-law-space -f deploy/hf_spaces/Dockerfile .
docker run -p 8501:8501 --env-file .env vn-labor-law-space
```
Truy cập trình duyệt tại `http://localhost:8501`.
