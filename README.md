# AI Agent tư vấn Luật Lao động Việt Nam

Agent trả lời câu hỏi về Bộ luật Lao động Việt Nam kèm trích dẫn điều luật kiểm chứng được, tự tính chính xác các khoản trợ cấp/lương, tự hỏi lại khi thiếu thông tin, và rà soát hợp đồng lao động để phát hiện điều khoản sai luật.

> Xem [PLAN.md](./PLAN.md) để biết lộ trình đầy đủ, tiến độ từng buổi và các ghi chú kỹ thuật chi tiết hơn.

## Kiến trúc

```mermaid
graph TD;
	__start__([<p>__start__</p>]):::first
	router(router)
	agent_loop(agent_loop)
	tools(tools)
	verify_citation(verify_citation)
	contract_review(contract_review)
	out_of_scope(out_of_scope)
	__end__([<p>__end__</p>]):::last
	__start__ --> router;
	agent_loop -.-> tools;
	agent_loop -.-> verify_citation;
	router -. &nbsp;legal_qa&nbsp; .-> agent_loop;
	router -. &nbsp;contract&nbsp; .-> contract_review;
	router -.-> out_of_scope;
	tools --> agent_loop;
	verify_citation -. &nbsp;end&nbsp; .-> __end__;
	verify_citation -.-> agent_loop;
	contract_review --> __end__;
	out_of_scope --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```

`router` phân loại câu hỏi (tra cứu luật / rà soát hợp đồng / ngoài phạm vi). `agent_loop` gọi công cụ (tra luật, tính toán, hỏi lại người dùng — `ask_user` dùng LangGraph `interrupt()` để dừng và chờ người dùng trả lời) cho tới khi đủ dữ liệu để trả lời. `verify_citation` kiểm tra bằng code mọi "Điều X" agent trích trong câu trả lời có thực sự nằm trong evidence đã tra được không; nếu có Điều bịa, agent bị bắt trả lời lại (tối đa 2 vòng).

Pipeline dữ liệu: `vbpl.vn` (Playwright, vượt chặn WAF) → parser tách theo Chương/Điều/Khoản (giữ cấu trúc phân cấp, không cắt theo độ dài cố định) → embedding `BAAI/bge-m3` (dense 1024 chiều + sparse) tạo trên Kaggle GPU → Qdrant (hybrid search dense+sparse, RRF) → rerank `BAAI/bge-reranker-v2-m3`.

## Kết quả

### Retrieval (Hit@5 / MRR@5, đo trên Kaggle GPU T4)

| Phiên bản | Dev (n=35) Hit@5 | Dev MRR@5 | Test (n=85) Hit@5 | Test MRR@5 |
|---|---|---|---|---|
| V1 — dense only | 0.971 | 0.884 | 0.976 | 0.903 |
| V2 — hybrid (dense+sparse, RRF) | **1.000** | 0.910 | 0.976 | 0.901 |
| V3 — hybrid + rerank | **1.000** | 0.895 | **0.988** | **0.940** |

→ Rerank cải thiện rõ nhất ở MRR (thứ hạng kết quả đúng cao hơn), quan trọng khi top-1 được dùng làm ngữ cảnh chính.

### Sinh câu trả lời (giám khảo LLM 1-5, trích dẫn precision/recall, bộ dev n=40)

| Phiên bản | Judge (1-5) | Citation P | Citation R | Từ chối đúng* | Độ trễ p50 | p95 |
|---|---|---|---|---|---|---|
| V0 — không RAG | 4.85 | 0.91 | 0.80 | 0.20 | 47s | 194s |
| V1 — dense RAG | 4.70 | 0.66 | 0.81 | 0.20 | 48s | 90s |
| V2 — hybrid RAG (dense+sparse, RRF) | 4.60 | 0.70 | 0.82 | 0.60 | 79s | 133s |
| V3 — hybrid + rerank RAG | 3.00 | 0.79 | 0.67 | 0.40 | 55s | 148s |
| V4 — agent đầy đủ (tool-calling + verify_citation) | **4.76** | 0.75 | **0.86** | **1.00** | 175s | 352s |

### Sinh câu trả lời trên bộ test khóa cứng (n=100)

| Phiên bản | Judge (1-5) | Citation P | Citation R | Từ chối đúng* | Độ trễ p50 | p95 |
|---|---|---|---|---|---|---|
| V0 — không RAG | 4.59 | 0.85 | 0.55 | 0.27 | 36s | 58s |
| V1 — dense RAG | **4.68** | 0.78 | **0.87** | 0.80 | 54s | 210s |
| V2 — hybrid RAG (dense+sparse, RRF) | 2.89 | 0.71 | 0.59 | 0.53 | 40s | 80s |
| V3 — hybrid + rerank RAG | 4.08 | **0.87** | 0.82 | 0.53 | 67s | 173s |
| **V4 — agent đầy đủ** | 4.39 | 0.75 | 0.84 | **1.00** | 161s | 385s |

\* Tỷ lệ từ chối đúng trên nhóm câu hỏi `ngoai_pham_vi` (câu hỏi không thuộc phạm vi luật lao động, agent phải biết từ chối thay vì bịa câu trả lời).

→ **Nhận xét quan trọng trên tập test:**
- **V4 (agent đầy đủ)** là phiên bản duy nhất **từ chối đúng tuyệt đối 100% (15/15)** các câu hỏi ngoài phạm vi nhờ có `router` độc lập, đồng thời duy trì Citation Recall cao (0.84) và Judge Score 4.39.
- **V2 (hybrid RAG)** trên bộ test có judge score thấp (2.89) do 49/100 câu rơi vào trạng thái *"Không tìm thấy căn cứ"* (bị chấm 1 điểm): nguyên nhân do RAG tĩnh không có reranker, khi RRF mang về chunk nhiễu kết hợp với mô hình fallback cạn quota cuối ngày có xu hướng phản hồi bảo thủ. Khi lên **V3** (thêm reranker), điểm phục hồi lên 4.08, và ở **V4** (agent tự tìm lại qua `get_article`/tool khác), điểm số đạt 4.39.

Bộ câu hỏi: 40 câu dev / 100 câu test, chia 4 nhóm — `tra_cuu` (tra 1 điều), `nhieu_dieu` (cần gộp nhiều điều), `tinh_huong` (cần tính toán), `ngoai_pham_vi` (phải từ chối).

### Rà soát hợp đồng

Trên 10 hợp đồng mẫu tự tạo (2 đúng, 8 có lỗi cài cắm có chủ đích): **precision = recall = 1.0** (14/14 lỗi phát hiện đúng, không có false positive).

## Quyết định thiết kế

- **Chia chunk theo Điều/Khoản, không theo độ dài cố định** — giữ nguyên đơn vị pháp lý nhỏ nhất có ý nghĩa độc lập, tránh cắt ngang một quy định.
- **Hybrid search + rerank thay vì chỉ dense** — luật có nhiều thuật ngữ/con số chính xác (tỷ lệ %, số ngày) mà sparse/tìm từ khóa bắt tốt hơn dense thuần.
- **Không để LLM tự tính toán** — mọi phép tính (trợ cấp thôi việc, lương thử việc, làm thêm giờ...) đi qua hàm Python thuần (`src/tools/calculators.py`), LLM chỉ được gọi tool và trình bày kết quả. Tránh lỗi số học/làm tròn của LLM.
- **Kiểm tra trích dẫn bằng code, không tin LLM tự báo cáo đúng** — `verify_citation` đối chiếu "Điều X" trong câu trả lời với danh sách Điều thực sự được tool trả về (parse từ `chunk_id`, không quét nội dung chunk vì một chunk có thể *dẫn chiếu* tới Điều khác mà không đồng nghĩa Điều đó đã được tra đúng).
- **Chia dev/test tách biệt, mỗi bộ đều có nhóm `ngoai_pham_vi`** — đo được cả khả năng từ chối đúng lúc, không chỉ khả năng trả lời đúng.
- **Xoay vòng nhiều Gemini API key + fallback Groq, nhớ key nào đã chết** — free tier Gemini chỉ ~20 request/ngày/key; `src/llm.py` tự động bỏ qua key đã biết là hết quota trong ngày (lưu vào `.gemini_dead_keys.json`, tự reset qua ngày mới) thay vì thử lại tất cả mỗi lần gọi.

## Hạn chế và lỗi đã biết

- **Độ trễ V0-V4 đo được bị ảnh hưởng bởi retry quota** — khi chạy, quota Gemini free-tier (nhiều key x nhiều model) cạn dần giữa chừng và phải rơi xuống Groq; số liệu p50/p95 vì vậy cao hơn tốc độ thực khi quota còn đủ, đặc biệt rõ ở V4 (161s/385s trên test). Chưa đo lại trong điều kiện quota ổn định hoàn toàn.
- **V2 (hybrid) điểm thấp trên test do cơ chế bảo thủ của RAG tĩnh** — đã phân tích nguyên nhân: 49/100 câu rơi vào "Không tìm thấy căn cứ" khi không có reranker lọc nhiễu trước ngữ cảnh RAG.
- **RAGAS faithfulness** (đo trong PLAN.md) chưa triển khai — bị hoãn có chủ đích do giới hạn thời gian, ưu tiên các chỉ số citation precision/recall và giám khảo LLM trước.
- **Đã hoàn thành đánh giá toàn diện V0 → V4 trên cả 2 bộ dev (40 câu) và test (100 câu)** — lưu tại `eval/results/generation_dev.json` và `eval/results/generation_test.json`.
- **Reranker vẫn chậm trên CPU dù đã chuyển ONNX** (~13s/query với backend mặc định `onnx_fp32`, giảm từ ~27s/query của bản gốc — xem `eval/results/onnx_reranker.json`) — khả thi hơn nhiều cho demo nhưng vẫn chưa đủ nhanh cho sản phẩm thời gian thực có nhiều người dùng đồng thời trên CPU.
- **Dữ liệu nguồn giới hạn 3 văn bản** (Bộ luật Lao động 2019, NĐ 145/2020, NĐ 293/2025) — chưa có Luật BHXH 2024, chưa xử lý hiệu lực theo thời gian khi văn bản có nhiều đợt sửa đổi.

## Cách chạy

### Docker (khuyến nghị)

```bash
cp .env.example .env               # điền GEMINI_API_KEY (hoặc GEMINI_API_KEYS), GROQ_API_KEY
# data/embeddings/embeddings.parquet không nằm trong git (file lớn, sinh từ Kaggle,
# xem mục Kaggle bên dưới) — cần có sẵn file này trước khi build.
docker compose build
docker compose up -d
make docker-index                  # nạp chunks + embeddings vào Qdrant trong container
```

- API: http://localhost:8000 (`/health`, `/chat`, `/chat/resume`, `/review-contract`, docs tại `/docs`)
- UI: http://localhost:8501
- Container `api` chưa có sẵn model ONNX đã export (không nằm trong image) nên tự fallback về reranker gốc (chậm hơn nhưng vẫn đúng); muốn có tốc độ ONNX trong Docker thì chạy `docker compose exec api python -m scripts.export_onnx_reranker` sau khi `up` (cần mount thêm volume nếu muốn giữ qua lần restart).

### Chạy trực tiếp trên máy (không Docker)

```bash
python -m venv .venv
.venv\Scripts\activate              # Windows; Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
docker run -p 6333:6333 qdrant/qdrant   # hoặc dùng Qdrant Cloud, sửa QDRANT_URL trong .env
make index                          # nạp dữ liệu vào Qdrant
python -m scripts.export_onnx_reranker  # tuỳ chọn: xuất ONNX cho reranker nhanh gấp đôi
                                         # (bỏ qua bước này cũng chạy được, tự fallback về bản gốc)
uvicorn src.api.main:app --reload   # terminal 1
streamlit run src/ui/app.py         # terminal 2
```

### Kaggle (tạo embedding, đánh giá retrieval trên GPU)

Xem `kaggle/01_embed_chunks.ipynb` (tạo `embeddings.parquet` từ `data/processed/chunks.jsonl`) và `kaggle/02_eval_retrieval.ipynb` (đo Hit@5/MRR@5 cho V1-V3 trên GPU T4). Cấu hình `~/.kaggle/kaggle.json` trước, chi tiết ở [PLAN.md § 6](./PLAN.md#6-hướng-dẫn-làm-việc-với-kaggle).

### Test và lint

```bash
make test    # pytest
make lint    # ruff check . (kaggle/*.ipynb loại trừ — xem pyproject.toml)
```

## Lời lưu ý pháp lý

Nội dung do agent trả lời chỉ mang tính tham khảo, không thay thế tư vấn pháp lý chuyên nghiệp. Dữ liệu nguồn cập nhật tới **10/11/2025** (Nghị định 293/2025/NĐ-CP, hiệu lực từ 01/01/2026) — xem `data/raw/sources.yaml` để biết chi tiết từng văn bản và ngày hiệu lực.
