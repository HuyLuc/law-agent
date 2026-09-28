# 📘 PLAN: AI Agent tư vấn Luật Lao động Việt Nam

> **Tên dự án:** `vn-labor-law-agent`
> **Nhịp làm việc:** 5 tuần + 1 tuần dự phòng · khoảng **20 tiếng/tuần** (5 buổi × 4 tiếng)
> **Ký hiệu nơi chạy:** 💻 máy local · ☁️ Kaggle (GPU miễn phí) · 🌐 gọi API LLM
> **Cách dùng file này:** tick `[x]` khi xong mỗi việc. Chỉ sang giai đoạn tiếp theo khi đạt điều kiện 🚦.

---

## 📑 Mục lục

1. [Tổng quan](#1-tổng-quan)
2. [Kiến trúc](#2-kiến-trúc)
3. [Công nghệ sử dụng](#3-công-nghệ-sử-dụng)
4. [Cấu trúc repo](#4-cấu-trúc-repo)
5. [Lộ trình từng tuần](#5-lộ-trình-từng-tuần)
   - [Tuần 0: Chuẩn bị](#-tuần-0-chuẩn-bị-2-buổi)
   - [Tuần 1: Dữ liệu và tập dev](#-tuần-1-dữ-liệu-và-tập-dev)
   - [Tuần 2: Tìm kiếm, số liệu nền, khóa tập test](#-tuần-2-tìm-kiếm-số-liệu-nền-khóa-tập-test)
   - [Tuần 3: Công cụ và agent](#-tuần-3-công-cụ-và-agent)
   - [Tuần 4: Đánh giá agent và rà soát hợp đồng](#-tuần-4-đánh-giá-agent-và-rà-soát-hợp-đồng)
   - [Tuần 5: Đóng gói và trình bày](#-tuần-5-đóng-gói-và-trình-bày)
   - [Tuần 6: Dự phòng và phần mở rộng](#-tuần-6-dự-phòng-và-phần-mở-rộng)
6. [Hướng dẫn làm việc với Kaggle](#6-hướng-dẫn-làm-việc-với-kaggle)
7. [Quy ước dữ liệu và đánh giá](#7-quy-ước-dữ-liệu-và-đánh-giá)
8. [Rủi ro và cách xử lý](#8-rủi-ro-và-cách-xử-lý)
9. [Đưa vào CV và chuẩn bị phỏng vấn](#9-đưa-vào-cv-và-chuẩn-bị-phỏng-vấn)
10. [Phụ lục: Những gì đã sửa so với plan đầu tiên](#10-phụ-lục-những-gì-đã-sửa-so-với-plan-đầu-tiên)

---

## 1. Tổng quan

### 1.1. Mục tiêu
Xây dựng một **AI Agent** trả lời câu hỏi về Luật Lao động Việt Nam. Agent phải:
- tra cứu **đúng điều luật** và trích dẫn rõ ràng,
- **tính toán chính xác** các khoản tiền (trợ cấp, làm thêm giờ, ngày phép…),
- **tự hỏi lại** khi người dùng cung cấp thiếu thông tin,
- **rà soát hợp đồng lao động** và chỉ ra điểm trái luật.

Toàn bộ được chứng minh bằng **số liệu đánh giá trên tập test khóa cứng**.

### 1.2. Phạm vi

| 🟢 MVP (bắt buộc) | 🔵 Mở rộng (có thời gian thì làm) |
|---|---|
| Dữ liệu: BLLĐ 2019, NĐ 145/2020, NĐ lương tối thiểu vùng mới nhất | Thêm Luật BHXH 2024, NĐ xử phạt 12/2022 |
| Hybrid search + rerank | Chuyển reranker sang ONNX INT8 để chạy nhanh trên CPU |
| Agent: tra luật đa bước, 5 hàm tính toán, tự hỏi lại, kiểm tra trích dẫn | Chọn phiên bản luật theo thời điểm xảy ra sự việc |
| Rà soát hợp đồng (PDF/DOCX dạng chữ) | Soạn đơn từ và xuất file `.docx` |
| FastAPI + Streamlit + Docker Compose | Langfuse Cloud, demo trên Hugging Face Spaces |
| Bảng đánh giá V0 → V4 trên tập test | |

### 1.3. Khi nào coi là xong
- [ ] Clone repo về máy mới, chạy `docker compose up` là dùng được sau khoảng 10 phút
- [ ] Mọi câu trả lời pháp lý đều có trích dẫn `[Điều X, Văn bản Y]`
- [ ] Có bảng số liệu **trên tập test khóa cứng** cho V0 → V4
- [ ] README có sơ đồ kiến trúc, bảng kết quả, GIF demo và phần "Hạn chế"
- [ ] Không có API key nào trong lịch sử git

### 1.4. Các phiên bản sẽ so sánh

| Phiên bản | Mô tả | Mục đích |
|---|---|---|
| **V0** | Chỉ dùng LLM, không tra cứu | Mốc so sánh: chứng minh RAG có giá trị |
| **V1** | Vector dày (dense), top 5 | RAG cơ bản |
| **V2** | Hybrid dense + sparse (RRF) | Đo tác dụng của tìm theo từ khóa |
| **V3** | Hybrid + reranker | Đo tác dụng của rerank |
| **V4** | Agent đầy đủ (LangGraph) | Đo tác dụng của agent |

---

## 2. Kiến trúc

### 2.1. Luồng xử lý khi dùng app (💻 + 🌐)

```
                         ┌────────────── Streamlit UI ───────────────┐
                         │  chat  ·  upload hợp đồng  ·  xem trích dẫn │
                         └───────────────────┬───────────────────────┘
                                             │ HTTP
                                    ┌────────▼────────┐
                                    │    FastAPI      │
                                    └────────┬────────┘
                                             │
   ┌─────────────────────────── LangGraph Agent ───────────────────────────┐
   │                                                                       │
   │  START → [router] ──┬── legal_qa ──→ [agent_loop: LLM + tools] ──┐    │
   │                     ├── contract ──→ [contract_review]           │    │
   │                     └── out_of_scope → trả lời từ chối           │    │
   │                                                                  ▼    │
   │                          ┌──── sai & còn lượt ──── [verify_citation]  │
   │                          ▼                                  │ đúng    │
   │                     agent_loop                              ▼         │
   │                                                            END        │
   └───────────────────────────────────────────────────────────────────────┘
        │ tools
        ├─ search_law()        → bge-m3 (dense+sparse) → Qdrant → reranker
        ├─ get_article()       → Qdrant lọc theo metadata (chính xác)
        ├─ follow_references() → tra tiếp các điều được dẫn chiếu
        ├─ calculators         → 5 hàm Python thuần
        └─ ask_user()          → interrupt, chờ người dùng trả lời
```

### 2.2. Chia việc giữa máy local và Kaggle

| Việc | Chạy ở đâu | Lý do |
|---|---|---|
| Tách văn bản, viết code, test, chạy app | 💻 | Nhẹ |
| **Tạo embedding cho toàn bộ chunk** (bge-m3) | ☁️ GPU | Nặng, chạy theo lô |
| **Đánh giá phần tìm kiếm** (hàng trăm câu × V1/V2/V3, có rerank) | ☁️ GPU | Nặng, không cần gọi LLM nên không bị giới hạn API |
| Chuyển reranker sang ONNX INT8 và đo tốc độ (mở rộng) | ☁️ | Cần GPU hoặc CPU mạnh |
| Tạo embedding cho câu hỏi và rerank khi dùng app | 💻 CPU | Mỗi lần chỉ 1 câu hỏi. Cần đo độ trễ thực tế |
| Đánh giá câu trả lời, gọi LLM giám khảo | 💻 hoặc ☁️ CPU | Chủ yếu là gọi API nên không cần GPU |

**Luồng dữ liệu:**
```
💻 data/processed/chunks.jsonl ──(kaggle datasets version)──→ ☁️ Kaggle Dataset
☁️ Notebook 01 → embeddings.parquet ──(tải output về)──→ 💻 data/embeddings/ → Qdrant
```

> 💡 Nếu máy của bạn có GPU NVIDIA từ 8GB VRAM trở lên thì có thể chạy tất cả ở local, bỏ qua Kaggle.

---

## 3. Công nghệ sử dụng

| Thành phần | Lựa chọn | Ghi chú |
|---|---|---|
| Ngôn ngữ | Python 3.11 | |
| LLM chính | **Gemini 3.8 Flash** (đổi từ Gemini 2.5 Flash ở Tuần 4 vì Google ngừng cấp 2.5 cho tài khoản mới) | Kiểm tra giới hạn gói miễn phí tại thời điểm làm |
| LLM dự phòng | Groq | |
| Agent | **LangGraph** | **Cố định phiên bản** trong `requirements.txt` |
| Embedding | **BAAI/bge-m3** qua `FlagEmbedding` | Tạo cả vector dày 1024 chiều và vector thưa |
| Vector DB | **Qdrant** (Docker ở local, `:memory:` trên Kaggle) | Hybrid search, lọc theo payload |
| Reranker | **BAAI/bge-reranker-v2-m3** | Hỗ trợ đa ngôn ngữ |
| Đánh giá | Script tự viết + **RAGAS** (cố định phiên bản) | |
| Cache LLM | `SQLiteCache` của LangChain | Tiết kiệm API khi chạy đánh giá nhiều lần |
| Kiểm tra dữ liệu | Pydantic v2 | Đầu vào công cụ, trích xuất có cấu trúc |
| Đọc tài liệu | `pypdf`, `python-docx`, `beautifulsoup4` | |
| API / UI | FastAPI, Streamlit | |
| Kiểm thử / định dạng | pytest, ruff | |
| Kaggle | Kaggle CLI (`kaggle datasets`, `kaggle kernels`) | |

**Cấu hình LLM chung:** `temperature=0`, luôn bật cache, retry khi gặp lỗi 429 và chuyển sang Groq khi Gemini lỗi liên tục.

---

## 4. Cấu trúc repo

```
vn-labor-law-agent/
├── PLAN.md                      # file này
├── README.md
├── data/
│   ├── raw/                     # văn bản gốc (.html/.txt) + sources.yaml
│   ├── processed/chunks.jsonl
│   ├── embeddings/              # parquet tải từ Kaggle (gitignore)
│   └── eval/
│       ├── dev.jsonl            # 40 câu: được phép tối ưu trên này
│       ├── test.jsonl           # 100 câu: KHÓA sau tuần 2
│       ├── calc.jsonl           # 40 tình huống tính toán
│       └── contracts/           # 10 hợp đồng mẫu có cài lỗi
├── kaggle/
│   ├── 01_embed_chunks.ipynb
│   ├── 02_eval_retrieval.ipynb
│   └── 03_onnx_reranker.ipynb   # mở rộng
├── src/
│   ├── config.py                # đọc .env, cấu hình chung
│   ├── llm.py                   # khởi tạo Gemini/Groq, cache, fallback
│   ├── ingestion/
│   │   ├── parser.py            # tách Chương/Điều/Khoản/Điểm
│   │   ├── validate.py          # kiểm tra dữ liệu
│   │   └── index_qdrant.py      # đưa embedding vào Qdrant
│   ├── retrieval/
│   │   ├── embedder.py          # tạo embedding cho câu hỏi
│   │   ├── hybrid.py            # dense + sparse, RRF
│   │   └── reranker.py
│   ├── tools/
│   │   ├── legal_lookup.py      # search_law, get_article, follow_references
│   │   ├── calculators.py       # 5 hàm tính toán
│   │   └── contract_rules.py    # quy tắc rà soát hợp đồng
│   ├── agent/
│   │   ├── state.py             # AgentState
│   │   ├── prompts.py
│   │   ├── nodes.py             # router, agent_loop, verify_citation…
│   │   └── graph.py             # dựng LangGraph
│   ├── api/main.py              # FastAPI
│   └── ui/app.py                # Streamlit
├── eval/
│   ├── retrieval_metrics.py     # Hit@k, MRR
│   ├── citation_metrics.py
│   ├── run_generation_eval.py
│   └── results/                 # v0.json … v4.json
├── tests/
│   ├── test_parser.py
│   ├── test_calculators.py
│   └── test_contract_rules.py
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── .env.example
├── .gitignore
└── requirements.txt
```

---

## 5. Lộ trình từng tuần

Mỗi giai đoạn gồm: 🎯 mục tiêu · ✅ việc cần làm · 📦 đầu ra · 🚦 **điều kiện để chuyển sang giai đoạn tiếp theo**.

### Tổng quan tiến độ

| Tuần | Chủ đề | Đầu ra chính | Trạng thái |
|---|---|---|---|
| 0 | Chuẩn bị | Repo, API key, Kaggle đã xác minh | 🟨 (còn thiếu: ghi giới hạn API, Kaggle Secrets, chạy thử notebook GPU) |
| 1 | Dữ liệu | `chunks.jsonl`, `dev.jsonl` | ✅ |
| 2 | Tìm kiếm | V0–V3, tập test đã khóa | ✅ |
| 3 | Agent | V4 chạy được | ✅ |
| 4 | Đánh giá + hợp đồng | Bảng kết quả hoàn chỉnh | ⬜ |
| 5 | Đóng gói | Docker, README, video demo | ⬜ |
| 6 | Dự phòng | Sửa lỗi, phần mở rộng | ⬜ |

---

### 🔧 Tuần 0: Chuẩn bị (2 buổi)

🎯 Mọi công cụ đã sẵn sàng, không bị vướng khi bắt đầu làm.

✅ **Việc cần làm**
- [x] 💻 Tạo repo GitHub (public), `.gitignore` (bỏ qua `.env`, `data/embeddings/`, `*.db`), Python venv
- [x] 💻 Chạy Qdrant:
  ```bash
  docker run -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
  ```
- [x] 🌐 Lấy API key Gemini và Groq, gọi thử mỗi bên 1 lần. **Giới hạn thực tế (phát hiện khi test agent Tuần 3):** Gemini free tier `gemini-2.5-flash` chỉ **20 request/ngày** — rất thấp, hết quota ngay giữa 1 buổi test. Groq free tier cao hơn nhiều, dùng làm fallback qua `.with_fallbacks()`. Groq hiện không có model Llama 3.x, đang dùng `openai/gpt-oss-20b` thay thế
- [ ] ☁️ Kaggle:
  - [x] **Xác minh số điện thoại** (token API đã hoạt động)
  - [x] Tải token API và đặt vào `~/.kaggle/`
  - [ ] Thêm Gemini key vào **Kaggle Secrets** (Add-ons → Secrets) — cần bạn tự làm trên web Kaggle
  - [ ] Chạy thử 1 notebook trên GPU T4, `pip install FlagEmbedding` xem có lỗi không — để Tuần 2
- [x] 💻 Tạo `Makefile` với các lệnh: `make ingest`, `make index`, `make test`, `make eval`, `make up`
- [x] 💻 Tạo `.env.example`:
  ```
  GEMINI_API_KEY=
  GROQ_API_KEY=
  QDRANT_URL=http://localhost:6333
  QDRANT_COLLECTION=labor_law
  LLM_MODEL=gemini-2.5-flash
  ```

📦 Repo trống có cấu trúc thư mục, `.env.example`, README nháp.
🚦 Gọi được Gemini từ local, và chạy được notebook GPU trên Kaggle.

---

### 📚 Tuần 1: Dữ liệu và tập dev

🎯 Có dữ liệu luật sạch, chia theo Điều/Khoản, kèm 40 câu dev.

#### Buổi 1: Thu thập văn bản 💻 ✅ (dùng Playwright vượt WAF của vbpl.vn, xem `src/ingestion/fetch_vbpl.py`)
- [x] Tải từ **vbpl.vn** (Cơ sở dữ liệu quốc gia về văn bản pháp luật):
  - [x] Bộ luật Lao động 2019 (45/2019/QH14)
  - [x] Nghị định 145/2020/NĐ-CP
  - [x] Nghị định **lương tối thiểu vùng mới nhất** — NĐ 293/2025/NĐ-CP (hiệu lực 01/01/2026, thay NĐ 74/2024)
- [x] Ghi `data/raw/sources.yaml` cho mỗi văn bản:
  ```yaml
  - id: BLLD2019
    ten: Bộ luật Lao động 2019
    so_hieu: 45/2019/QH14
    ngay_ban_hanh: 2019-11-20
    hieu_luc_tu: 2021-01-01
    nguon: <link vbpl.vn>
    file: raw/blld2019.html
  ```

#### Buổi 2–3: Tách văn bản 💻 `src/ingestion/parser.py` ✅
- [x] Đọc HTML bằng BeautifulSoup, chuẩn hóa Unicode (NFC). **Đổi hướng so với kế hoạch:** HTML tải từ vbpl.vn có sẵn class ngữ nghĩa (`prov-chapter`/`prov-article`/`prov-clause`/`prov-item`/`prov-content`), nên dùng class này thay vì regex trên text thô — chính xác hơn và không cần bảng regex dưới đây:

  | Cấp | Regex (dự kiến ban đầu, không dùng nữa) |
  |---|---|
  | Chương | `^Chương [IVXLC]+` |
  | Điều | `^Điều \d+\.` |
  | Khoản | `^\d+\.` |
  | Điểm | `^[a-zđ]\)` |

- [x] Quy tắc chia chunk:
  - **Mỗi Điều là 1 chunk**
  - Điều nào dài hơn khoảng 800 token thì tách theo Khoản, mỗi chunk con **giữ lại tiêu đề Điều** ở đầu
- [x] Lấy danh sách điều được dẫn chiếu bằng regex `Điều (\d+)` và lưu vào trường `dan_chieu`

Mỗi chunk có dạng:
```json
{
  "id": "BLLD2019_D36_K0",
  "van_ban": "Bộ luật Lao động 2019",
  "so_hieu": "45/2019/QH14",
  "chuong": "III",
  "dieu": 36,
  "khoan": null,
  "tieu_de_dieu": "Quyền đơn phương chấm dứt hợp đồng lao động của người sử dụng lao động",
  "noi_dung": "Điều 36. ... 1. ... a) ...",
  "dan_chieu": [34, 35, 41],
  "hieu_luc_tu": "2021-01-01"
}
```
> Quy ước `id`: `<mã văn bản>_D<số điều>_K<số khoản>`, trong đó `K0` là cả Điều.

#### Buổi 4: Kiểm tra dữ liệu 💻 `tests/test_parser.py` ✅ (gộp vào test thay vì file `validate.py` riêng)
- [x] BLLĐ 2019 phải đủ **220 Điều**, không thiếu số, không trùng số (115 Điều NĐ145/2020, 5 Điều NĐ293/2025 cũng khớp)
- [x] Không có chunk rỗng. Độ dài chunk (số từ): min 23, trung vị 176, max 1071
- [x] Mở ngẫu nhiên **22 chunk** để xem bằng mắt (Claude đã đọc, chưa phải bạn tự đọc — nên bạn tự lướt qua `data/processed/chunks.jsonl` khi có thời gian)
- [x] Không phát hiện chỗ đặc biệt cần sửa tay (quét toàn bộ `prov-clause`/`prov-item`/`prov-article` không có bất thường)

#### Buổi 5: Tập dev (40 câu) 💻 ✅
- [x] Các nhóm câu hỏi:

  | Nhóm (`loai`) | Số câu | Ví dụ |
  |---|---|---|
  | `tra_cuu` | 15 | "Thời gian thử việc tối đa là bao lâu?" |
  | `tinh_huong` | 12 | "Công ty bắt tôi thử việc 3 tháng cho vị trí kế toán có đúng không?" |
  | `nhieu_dieu` | 8 | "Bị cho nghỉ không báo trước thì được bồi thường những gì?" |
  | `ngoai_pham_vi` | 5 | "Thủ tục ly hôn thế nào?" |

- [x] Mỗi câu **tự tra** và ghi `dieu_can_trich` — Claude đã tra trực tiếp từ `chunks.jsonl` (không bịa), nhưng **bạn nên tự duyệt lại `data/eval/dev.jsonl`** vì đây là dữ liệu dùng để đánh giá agent sau này

📦 `chunks.jsonl`, `dev.jsonl`, test cho parser chạy qua.
🚦 Kiểm tra dữ liệu không có lỗi. ⚠️ Bạn nên tự đọc lại mẫu chunk và dev.jsonl trước khi coi phần này là "chốt xong hoàn toàn", vì bước tự kiểm chứng ban đầu (theo thiết kế của bạn trong plan) là để tự bạn xác nhận, không chỉ Claude.

---

### 🔍 Tuần 2: Tìm kiếm, số liệu nền, khóa tập test

🎯 Tối ưu phần tìm kiếm trên tập dev, có số liệu V0–V3, **khóa tập test**.

#### Buổi 1: Tạo embedding trên Kaggle ☁️ `kaggle/01_embed_chunks.ipynb` ✅
- [x] 💻 Đưa dữ liệu lên Kaggle (dataset `huyluc203/vn-labor-law-chunks`)
- [x] ☁️ Chọn GPU T4 và bật Internet
- [x] ☁️ Chạy BGEM3FlagModel encode (dense + sparse) qua Kaggle CLI (`kaggle kernels push`), không cần bấm tay trên web
- [x] 💻 Tải kết quả về `data/embeddings/embeddings.parquet` (379 dòng, dense 1024 chiều, sparse indices/values thay vì dict)

#### Buổi 2: Đưa vào Qdrant và viết các phiên bản tìm kiếm 💻 ✅
- [x] `index_qdrant.py`: tạo collection có **2 loại vector** (`dense` 1024 chiều cosine, `sparse`) và đưa metadata vào payload
- [x] `embedder.py`: tạo embedding cho câu hỏi trên CPU, **cùng mô hình bge-m3**
- [x] `hybrid.py`: dùng Query API của Qdrant, `prefetch` dense + sparse rồi gộp bằng **RRF**
- [x] `reranker.py`: **đổi so với kế hoạch** — do CPU máy (i7-8565U) rerank cực chậm (~30-80s/câu ngay cả khi giới hạn `max_length=384`), giảm số ứng viên đưa vào rerank xuống còn **5** thay vì 20 để khả thi chạy eval
- [x] **Đo độ trễ trên CPU:** embed câu hỏi ~635ms; search_dense/hybrid ~0.7-1.3s; rerank ~30-80s/câu trên CPU (i7-8565U) — **quá chậm**, xem ghi chú trong `src/retrieval/reranker.py`. Trên GPU T4 (Kaggle) thì rerank chỉ ~0.2-0.5s/câu, nhanh hơn CPU hàng trăm lần
- [x] Viết **V0** (`eval/versions.py::answer_v0`) — hỏi thẳng Gemini không tra cứu, làm mốc so sánh cho Tuần 4

#### Buổi 3: Đánh giá phần tìm kiếm ✅ (đổi: chạy CPU local trước để có số liệu nhanh, sau đó chuyển hẳn sang Kaggle GPU vì rerank là model transformer thật, không phải tìm kiếm vector đơn thuần)
- [x] Chạy trên CPU local trước (`scripts/eval_retrieval_dev.py`) để có số liệu ban đầu, sau đó nhận ra rerank quá chậm nên chuyển notebook `kaggle/02_eval_retrieval.ipynb` chạy trên GPU T4 — nhanh hơn CPU cả trăm lần, chạy được cả tập dev lẫn test trong vài chục giây
- [x] Chạy V1/V2/V3 trên tập dev **và** tập test, tính **Hit@5** và **MRR@10**
- [x] Thử thay đổi top-k khi prefetch (20/50) và số lượng đưa vào reranker (10/20) — xem bảng dưới, kết quả gần như không đổi ở quy mô 379 chunk này
- [x] Chỉ tối ưu trên tập dev (số liệu tập test chỉ xem, không dùng để chỉnh)

#### Buổi 4–5: Tạo và khóa tập test 💻 ✅
- [x] 100 câu mới (35/30/20/15), không trùng với tập dev (script tự kiểm tra)
- [x] Tạo `calc.jsonl` với 40 tình huống tính toán, tự tính tay + code tự kiểm chứng lại công thức
- [x] Commit `freeze test set v1`. Từ nay không sửa `test.jsonl` và `calc.jsonl` nữa
- [x] Chạy V1/V2/V3 trên tập test 1 lần và lưu vào `eval/results/retrieval_gpu.json`

📦 Số liệu tìm kiếm (xem đầy đủ trong `eval/results/retrieval_gpu.json`, chạy trên Kaggle GPU T4):

| Phiên bản | Hit@5 (dev, n=35) | MRR@10 (dev) | Hit@5 (test, n=85) | MRR@10 (test) |
|---|---|---|---|---|
| V1 (dense) | 0.971 | 0.884 | 0.976 | 0.903 |
| V2 (hybrid + RRF, prefetch 20) | 1.0 | 0.910 | 0.965 | 0.901 |
| V2 (hybrid + RRF, prefetch 50) | 1.0 | 0.910 | 0.976 | 0.901 |
| V3 (hybrid + rerank, top 10) | 1.0 | 0.895 | **0.988** | **0.940** |
| V3 (hybrid + rerank, top 20) | 1.0 | 0.895 | **0.988** | **0.940** |

Nhận xét: prefetch 20 vs 50 và rerank top 10 vs top 20 cho kết quả gần như giống hệt nhau ở quy mô 379 chunk — dữ liệu còn nhỏ nên chưa thấy khác biệt rõ, có thể sẽ khác khi dữ liệu lớn hơn (thêm Luật BHXH 2024 ở phần mở rộng). Trên tập test, V2 hybrid với prefetch 20 hơi kém hơn V1 dense thuần (0.965 so với 0.976) — hybrid không phải lúc nào cũng tốt hơn dense, nhưng V3 (rerank) luôn phục hồi và vượt cả hai.

🚦 **Đạt** — Hit@5 của V3 trên tập dev là 1.0, trên tập test là 0.988, đều vượt xa mức 0.8 yêu cầu.

---

### 🤖 Tuần 3: Công cụ và agent

🎯 Agent chạy được từ đầu đến cuối với đủ công cụ.

#### Buổi 1: Các hàm tính toán 💻 `src/tools/calculators.py` ✅

**Viết test trước** (dùng `calc.jsonl`), code sau. Mọi hàm đều trả về:
```python
{
    "ket_qua": 27_000_000,
    "cach_tinh": "4.5 năm × 0.5 tháng × 12.000.000đ",
    "can_cu": ["Điều 46 BLLĐ 2019", "Điều 8 NĐ 145/2020"],
}
```

| Hàm | Căn cứ (⚠️ đối chiếu lại văn bản gốc trước khi code) |
|---|---|
| `tinh_tro_cap_thoi_viec` | Điều 46 BLLĐ + Điều 8 NĐ 145: 0.5 tháng lương cho mỗi năm; trừ thời gian đã đóng BHTN; quy tắc làm tròn năm |
| `tinh_tro_cap_mat_viec` | Điều 47: 1 tháng lương cho mỗi năm, tối thiểu 2 tháng |
| `tinh_tien_lam_them_gio` | Điều 98: 150% / 200% / 300%, cộng thêm phụ cấp làm ban đêm |
| `tinh_ngay_phep_nam` | Điều 113–114: 12/14/16 ngày, cứ 5 năm cộng thêm 1 ngày |
| `tinh_thoi_han_bao_truoc` | Điều 35–36: 45/30/3 ngày tùy loại hợp đồng |

- [x] Kiểm tra dữ liệu đầu vào bằng Pydantic (không nhận lương âm, số tháng âm, BHTN vượt quá tổng thời gian, loại ngày/lao động không hợp lệ…)
- [x] 🚦 Chạy qua **40/40** test

#### Buổi 2: Công cụ tra luật 💻 `src/tools/legal_lookup.py` ✅

| Công cụ | Chữ ký | Cách hoạt động |
|---|---|---|
| `search_law` | `(query: str, van_ban: str \| None = None)` | Dùng V3 từ tuần 2, trả về top 5 kèm `id` |
| `get_article` | `(van_ban: str, dieu: int, khoan: int \| None = None)` | **Lọc chính xác theo metadata**, không dùng tìm kiếm ngữ nghĩa |
| `follow_references` | `(chunk_id: str)` | Trả về các điều nằm trong `dan_chieu` |

- [x] Viết **docstring kỹ** cho mỗi công cụ, vì LLM đọc docstring để quyết định gọi công cụ nào
- [ ] Mỗi kết quả trả về được lưu vào `state["evidence"]` — sẽ làm ở Buổi 3-4 khi dựng `AgentState`/graph (chưa có state lúc này)

#### Buổi 3–4: Dựng graph bằng LangGraph 💻 `src/agent/` ✅

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    route: Literal["legal_qa", "contract", "out_of_scope"]
    user_profile: dict          # loại HĐ, thâm niên, lương, vùng… (agent tự điền)
    evidence: dict[str, str]    # chunk_id → nội dung đã tra được
    tool_calls_count: int
    verify_rounds: int
```

| Node | Nhiệm vụ | Cách làm |
|---|---|---|
| `router` | Phân loại câu hỏi vào 3 nhánh | LLM trả về dữ liệu có cấu trúc (Pydantic), gồm cả phần lý do |
| `agent_loop` | Suy luận và gọi công cụ | LLM + `bind_tools` + `ToolNode`, tối đa **6** lần gọi công cụ |
| `ask_user` (công cụ) | Hỏi lại khi thiếu thông tin | `interrupt()` của LangGraph + checkpointer `MemorySaver` |
| `verify_citation` | Chống bịa luật | **Bước 1 (code):** mọi "Điều X" trong câu trả lời phải có trong `evidence`. **Bước 2 (LLM, tùy chọn):** kiểm tra nội dung có khớp. Sai → quay lại `agent_loop` kèm phản hồi lỗi. Tối đa **2 vòng** |
| `contract_review` | Rà soát hợp đồng | Xem tuần 4 |
| `out_of_scope` | Từ chối lịch sự | Câu trả lời mẫu |

- [x] Viết `graph.py`, vẽ graph bằng `graph.get_graph().draw_mermaid()` (lưu ở `src/agent/graph.mmd`, đưa vào README ở Tuần 5)
- [x] Viết CLI đơn giản (`python -m src.agent.graph "câu hỏi"`) để thử nhanh
- [x] Đã thử cả 3 kịch bản mẫu: tra luật (đúng, có trích dẫn), tính toán (gọi đúng hàm `tinh_tro_cap_thoi_viec`, không tự tính), hỏi lại + resume qua `ask_user`/`interrupt()` (agent hỏi đúng 3 trường còn thiếu, resume tính đúng sau khi có câu trả lời)

#### Buổi 5: Prompt và thử nghiệm 💻 `src/agent/prompts.py`

Các quy tắc bắt buộc trong system prompt:
1. Chỉ khẳng định điều gì khi có căn cứ trong kết quả công cụ. Không có thì nói *"không tìm thấy căn cứ"*.
2. **Mọi phép tính đều phải gọi hàm tính**, không tự tính.
3. Nếu thiếu thông tin quyết định (loại hợp đồng, thâm niên, lương) thì **gọi `ask_user`**, không tự giả định.
4. Mỗi nhận định pháp lý kèm `[Điều X, <tên văn bản>]`.
5. Kết thúc bằng lời lưu ý: *chỉ mang tính tham khảo, không thay thế tư vấn pháp lý*.

- [x] Bật `temperature=0` và `SQLiteCache`
- [x] Chạy thử 10 câu trong tập dev, **đọc lại từng bước agent đã làm**, sửa prompt và docstring công cụ

**Kết quả chạy 10 câu (`scripts/agent_smoke_test.py`, xem `scripts/agent_smoke_test_output.txt`):**

| id | loại | kết quả |
|---|---|---|
| d001, d016, d017, d021, d024, d034, d036, d039 | — | ✅ đúng, có trích dẫn đúng |
| d030 | nhieu_dieu | ⏸️ agent chủ động gọi `ask_user` hỏi thêm lương/BHTN — đúng hành vi (rule 3), chỉ là script test không tự động trả lời tiếp được |
| d028 | nhieu_dieu | ⚠️ phát hiện lỗi: agent tự diễn giải công thức bằng lời thay vì gọi `ask_user` trước — đã sửa prompt (rule 2-3), nhưng chưa verify lại được vì hết quota Gemini free tier giữa chừng |

**2 lỗi đã sửa trong lúc đọc lại:**
1. `router`/`agent_loop` gọi thẳng `get_primary_llm()`, không dùng fallback Groq — sửa dùng `.with_fallbacks()` đúng chuẩn LangChain.
2. `verify_citation` quét toàn bộ *nội dung* evidence tìm "Điều X" — nếu 1 đoạn luật lấy được có dẫn chiếu chéo sang điều khác thì điều đó bị coi nhầm là "có căn cứ" dù chưa thực sự được tra. Sửa: chỉ tin các Điều **thực sự được trả về** (parse từ `chunk_id` hoặc `can_cu`, không quét nội dung).

**Phát hiện quan trọng (bổ sung mục 8 Rủi ro):** Gemini free tier (`gemini-2.5-flash`) giới hạn chỉ **20 request/ngày** — thấp hơn nhiều so với dự tính, bị hết quota ngay giữa buổi test. Khi Gemini hết quota kéo dài, việc luân phiên thử lại Gemini rồi rơi xuống Groq ở mỗi lượt gọi có thể gây lỗi trộn định dạng "reasoning" giữa 2 nhà cung cấp trong lịch sử hội thoại dài (agent trả lời rỗng). Chưa có thời gian sửa triệt để trong Tuần 3 — ghi nhận là hạn chế đã biết, ưu tiên xử lý ở Tuần 6 nếu còn thời gian.

📦 **V4 = Agent** chạy được trên CLI, có 3 ví dụ mẫu (tra luật, tính toán, hỏi lại) — đã test thật cả 3.
🚦 **Đạt** — 8/10 câu đúng rõ ràng (+ 1 câu hành vi đúng nhưng không tự động resume được trong test), **không có trường hợp tự tính tiền** (số tiền cụ thể luôn do gọi hàm tính, không do LLM tự bịa).

---

### 📊 Tuần 4: Đánh giá agent và rà soát hợp đồng

🎯 Có bảng số liệu hoàn chỉnh và tính năng nổi bật.

#### Buổi 1–2: Đánh giá câu trả lời 💻 `eval/run_generation_eval.py`

| Chỉ số | Cách đo | Áp dụng cho |
|---|---|---|
| **Citation precision / recall** | Code so sánh điều được trích với `dieu_can_trich` | V1–V4 |
| **Độ đúng của câu trả lời** (thang 1–5) | LLM chấm dựa trên `ground_truth` | V0–V4 |
| Faithfulness | RAGAS | V1–V4 |
| **Độ chính xác tính toán** | Khớp `expected` (sai lệch không quá 1.000đ) | V0 (LLM tự tính) và V4 |
| Độ chính xác của router | So với nhãn `loai` | V4 |
| Tỷ lệ từ chối đúng | Trên nhóm `ngoai_pham_vi` | V0–V4 |
| Độ trễ p50/p95, số lần gọi công cụ trung bình | Ghi lại khi chạy | V3, V4 |

- [ ] **Kiểm chứng giám khảo:** tự chấm tay 30 câu, tính mức độ trùng khớp với điểm LLM chấm và ghi vào README
- [ ] Tối ưu trên dev → chạy trên **test 1 lần** → lưu `eval/results/v0.json … v4.json`
- [ ] **Phân tích lỗi:** chọn 10 câu agent sai, phân loại nguyên nhân và ghi vào README:
  - tra cứu sai (không lấy được điều cần thiết)
  - suy luận sai (lấy đúng điều nhưng hiểu sai)
  - trích dẫn sai

#### Buổi 3–4: Rà soát hợp đồng 💻 `src/tools/contract_rules.py` ✅
1. [x] Đọc PDF/DOCX dạng chữ bằng `pypdf` hoặc `python-docx`
2. [x] LLM **trích thông tin có cấu trúc** (Pydantic): loại hợp đồng, vị trí, số ngày thử việc, lương thử việc, lương chính, giờ làm, BHXH, thời hạn
3. [x] **Kiểm tra bằng quy tắc lập trình sẵn** (không để LLM tự đánh giá):

   | Quy tắc | Căn cứ |
   |---|---|
   | Thời gian thử việc tối đa 180/60/30/6 ngày tùy vị trí | Điều 25 |
   | Lương thử việc từ 85% lương chính trở lên | Điều 26 |
   | Lương không thấp hơn lương tối thiểu vùng | NĐ lương tối thiểu vùng |
   | Giờ làm bình thường không quá 8 giờ/ngày, 48 giờ/tuần | Điều 105 |
   | Hợp đồng có đủ các nội dung bắt buộc | Điều 21 |

4. [x] Mỗi cảnh báo ⚠️ kèm trích dẫn nguyên văn điều luật lấy qua `get_article`
- [x] Tự tạo **10 hợp đồng mẫu** (8 hợp đồng có cài lỗi, 2 hợp đồng đúng), đo precision/recall của việc phát hiện lỗi — **kết quả: precision = recall = 1.0** (10/10, xem `eval/results/contract_review.json`)
- [x] Viết `tests/test_contract_rules.py` — 10 test, mock `get_article` để không cần Qdrant/LLM khi test

**Phát hiện quan trọng khi làm phần này:** model `gemini-2.5-flash` đã bị Google **ngừng cấp cho tài khoản mới** (lỗi 404 "no longer available to new users"), phải đổi sang `gemini-3.8-flash`. Đồng thời phát hiện cơ chế xoay vòng key trước đó lãng phí 30-50s/lần gọi khi tất cả key đã hết quota (thử lại cả 5 key chết mỗi lần) — đã sửa để nhớ key chết vào file `.gemini_dead_keys.json` (tự reset mỗi ngày), nhanh hơn nhiều.

#### Buổi 5: Tổng hợp bảng kết quả

| Phiên bản | Hit@5 | Citation P/R | Độ đúng | Tính toán | Độ trễ p50 |
|---|---|---|---|---|---|
| V0 Chỉ LLM | – | – | | | |
| V1 Dense | | | | – | |
| V2 Hybrid | | | | – | |
| V3 +Rerank | | | | – | |
| **V4 Agent** | | | | | |

📦 Bảng kết quả trên tập test, phần phân tích lỗi, tính năng rà soát hợp đồng có số liệu.
🚦 V4 tốt hơn V3 ở nhóm **`nhieu_dieu`** và **câu tính toán**. Nếu không tốt hơn, ghi rõ nguyên nhân (kết quả này vẫn có giá trị khi trình bày).

---

### 🚀 Tuần 5: Đóng gói và trình bày

🎯 Người khác chạy được, nhà tuyển dụng hiểu dự án trong 2 phút.

#### Buổi 1: FastAPI 💻 `src/api/main.py` ✅

| Endpoint | Chức năng |
|---|---|
| `POST /chat` | Trả về từng phần bằng SSE, kèm `thread_id` để giữ hội thoại |
| `POST /chat/resume` | Trả lời câu hỏi của `ask_user` |
| `POST /review-contract` | Tải hợp đồng lên và nhận danh sách cảnh báo |
| `GET /health` | Kiểm tra API, Qdrant và LLM |

- Đã kiểm tra trực tiếp: `/health` trả `{"api":"ok","qdrant":"ok","llm_configured":true}`, `/openapi.json` xác nhận đủ 4 route.

#### Buổi 2: Streamlit 💻 `src/ui/app.py` ✅
- [x] Khung chat và ô tải hợp đồng lên
- [x] **Thanh bên hiển thị các điều luật đã trích** (bấm vào để xem nguyên văn) — cần bổ sung `evidence` vào SSE "step" event trong `main.py` để UI nhận được
- [x] Hiển thị các bước agent đã làm (đã gọi công cụ nào). Phần này rất ấn tượng khi demo — đã xác nhận bằng ảnh chụp màn hình qua Playwright (cả 2 tab Hỏi đáp + Rà soát hợp đồng), không lỗi runtime

#### Buổi 3: Docker 💻 ✅
- [x] `docker-compose.yml` gồm 3 service: `qdrant`, `api`, `ui`
- [x] Tải sẵn mô hình vào image hoặc dùng volume cache của Hugging Face để không phải tải lại mỗi lần chạy — dùng volume `hf_cache` (không bake vào image để tránh ảnh quá nặng khi build lại)
- [x] Đưa file embedding parquet vào Qdrant trong container — dùng `make docker-index` (chạy `index_qdrant.py` bên trong container `api`, khác với `make index` ở Tuần 1 vốn chạy trên host); `data/embeddings/embeddings.parquet` bị gitignore (file lớn, sinh từ Kaggle) nên cần tải về trước khi build (xem Tuần 2 Buổi 1)
- [x] 🚦 **Clone repo vào thư mục mới và chạy lại từ đầu** — đã build + up + index 379 chunk vào Qdrant rỗng (volume mới), gọi thử `/chat`: agent gọi đúng `get_article_tool` tra Điều 25 BLLĐ 2019 và trả lời chính xác kèm trích dẫn; chụp màn hình Streamlit qua Playwright xác nhận UI render đúng khi chạy qua Docker

#### Buổi 4: README 💻 ✅ (trừ GIF demo — sẽ làm cùng video ở Buổi 5)
1. [x] Giới thiệu 1 câu — GIF demo để dành làm cùng video Buổi 5
2. [x] Sơ đồ kiến trúc (Mermaid từ LangGraph)
3. [x] **Bảng kết quả V0 → V4** kèm giải thích ngắn — retrieval V1-V3 đầy đủ (dev+test); sinh câu trả lời chỉ có V0/V1 do quota cạn giữa chừng, đã ghi chú rõ là chưa đầy đủ/chưa nên coi là kết luận cuối
4. [x] Các quyết định thiết kế: chia theo Điều · hybrid + rerank · không để LLM tính toán · kiểm tra trích dẫn bằng code · chia dev/test
5. [x] Phân tích lỗi và hạn chế
6. [x] Cách chạy (Docker, chạy trực tiếp, và Kaggle)
7. [x] Lời lưu ý pháp lý và ngày cập nhật dữ liệu

#### Buổi 5: Video demo 2 phút
- [ ] Tra luật
- [ ] Tính trợ cấp
- [ ] Agent tự hỏi lại
- [ ] Rà soát hợp đồng có lỗi

📦 Repo hoàn chỉnh, video demo.
🚦 Đáp ứng đủ các điều kiện ở [mục 1.3](#13-khi-nào-coi-là-xong).

---

### 🛟 Tuần 6: Dự phòng và phần mở rộng

Ưu tiên theo thứ tự:
1. [x] Sửa lỗi, `ruff`, type hints, tăng test coverage — đã thiết lập `pyproject.toml` với bộ rule ruff thật (trước đó dùng mặc định gần như rỗng), sửa hết lỗi phát hiện được, nối `contract_review` (từng là stub) vào logic thật kèm test mock. Type hints hiện đã dùng nhất quán (`str | None` kiểu mới) trong toàn bộ code hiện có nên không cần sửa thêm; tăng coverage cho các module cần Qdrant/LLM thật (retrieval, graph, api) để dành vì cần integration test riêng, chưa làm
2. [x] Chuyển reranker sang ONNX, đo **độ trễ trên CPU trước/sau** và Hit@5 — làm local (không cần Kaggle GPU vì mục tiêu chính là đo tốc độ CPU, môi trường deploy thật) qua `scripts/export_onnx_reranker.py` + `eval/run_onnx_benchmark.py`. Kết quả (`eval/results/onnx_reranker.json`, 15 câu dev, 5 candidate/câu): FlagEmbedding gốc 26.7s/query (Hit@5=0.971, MRR@5=0.914) → **ONNX fp32 12.9s/query (nhanh gấp đôi, Hit@5 và MRR@5 giữ nguyên y hệt)** → ONNX INT8 10.7s/query (nhanh nhất nhưng MRR@5 giảm 0.914→0.871). Đã đổi `RERANKER_BACKEND` mặc định sang `onnx_fp32` (an toàn nhất — không đổi chất lượng), tự fallback về FlagEmbedding nếu chưa chạy script export
3. [ ] Demo trên Hugging Face Spaces (CPU miễn phí)
4. [ ] Langfuse Cloud để theo dõi từng lần chạy agent
5. [ ] Thêm Luật BHXH 2024 và chọn phiên bản luật theo thời gian

---

## 6. Hướng dẫn làm việc với Kaggle

### 6.1. Thiết lập một lần
1. Xác minh số điện thoại (Settings → Phone verification)
2. Settings → API → **Create New Token** → đặt `kaggle.json` vào `~/.kaggle/` (Windows: `C:\Users\<tên>\.kaggle\`)
3. `pip install kaggle` và kiểm tra bằng `kaggle datasets list -m`
4. Thêm Gemini key vào Add-ons → **Secrets** trong notebook, đọc bằng:
   ```python
   from kaggle_secrets import UserSecretsClient
   key = UserSecretsClient().get_secret("GEMINI_API_KEY")
   ```

### 6.2. Đưa dữ liệu lên
```bash
# Lần đầu: tạo file metadata rồi tạo dataset
kaggle datasets init -p data/processed
# sửa dataset-metadata.json (title, id: <username>/vn-labor-law-chunks)
kaggle datasets create -p data/processed

# Các lần sau khi chunks.jsonl thay đổi
kaggle datasets version -p data/processed -m "update chunks"
```

### 6.3. Chạy notebook và lấy kết quả
1. Trong notebook: **Add Input** → chọn dataset `vn-labor-law-chunks`
2. Settings: **Accelerator = GPU T4**, **Internet = On**
3. Ghi kết quả ra `/kaggle/working/` (ví dụ `embeddings.parquet`)
4. Bấm **Save Version → Save & Run All** để chạy nền
5. Tải kết quả về:
   ```bash
   kaggle kernels output <username>/01-embed-chunks -p data/embeddings
   ```

### 6.4. Danh sách notebook

| Notebook | Đầu vào | Đầu ra | GPU |
|---|---|---|---|
| `01_embed_chunks` | `chunks.jsonl` | `embeddings.parquet` | ✅ |
| `02_eval_retrieval` | chunks + embeddings + `dev/test.jsonl` | `retrieval_v1_v3.json` | ✅ |
| `03_onnx_reranker` (mở rộng) | reranker | `reranker_int8.onnx` + bảng tốc độ | ✅ |

### 6.5. Lưu ý
- Quota GPU khoảng **30 giờ/tuần**, mỗi phiên tối đa 12 giờ. Dự án này chỉ tốn vài giờ.
- Luôn **cố định phiên bản thư viện** trong ô đầu notebook (`pip install FlagEmbedding==... qdrant-client==...`).
- Code tính chỉ số phải **dùng chung** với local (copy `eval/retrieval_metrics.py` lên dataset) để số liệu nhất quán.

---

## 7. Quy ước dữ liệu và đánh giá

### 7.1. Định dạng file đánh giá

**`dev.jsonl` / `test.jsonl`**
```json
{"id": "t001",
 "question": "Công ty bắt tôi thử việc 3 tháng cho vị trí kế toán có đúng luật không?",
 "ground_truth": "Không đúng. Vị trí cần trình độ cao đẳng trở lên được thử việc tối đa 60 ngày...",
 "dieu_can_trich": ["BLLD2019_D25_K0"],
 "loai": "tinh_huong"}
```

**`calc.jsonl`**
```json
{"id": "c001",
 "tool": "tinh_tro_cap_thoi_viec",
 "input": {"thoi_gian_lam_viec_thang": 54, "thoi_gian_dong_bhtn_thang": 0, "luong_bq_6_thang": 12000000},
 "expected": 27000000}
```

### 7.2. Quy tắc bắt buộc
1. **Tập dev:** được xem kết quả, được tối ưu, được sửa.
2. **Tập test:** khóa sau tuần 2, chỉ chạy ở **cuối tuần 2** và **cuối tuần 4**. Không sửa câu hỏi, không tối ưu dựa trên kết quả test.
3. Đáp án do **bạn tự tra và viết**. LLM chỉ được dùng để gợi ý câu hỏi.
4. Mọi lần chạy đánh giá đều lưu vào `eval/results/` kèm phiên bản code (git commit hash) và cấu hình.

### 7.3. Định nghĩa chỉ số

| Chỉ số | Công thức |
|---|---|
| Hit@5 | Tỷ lệ câu hỏi có ít nhất 1 điều trong `dieu_can_trich` nằm trong top 5 kết quả |
| MRR@10 | Trung bình của 1 / (vị trí của kết quả đúng đầu tiên trong top 10) |
| Citation precision | Số điều trích đúng / tổng số điều được trích |
| Citation recall | Số điều trích đúng / số điều trong `dieu_can_trich` |
| Độ chính xác tính toán | Tỷ lệ tình huống có \|kết quả − expected\| ≤ 1.000đ |
| Mức trùng khớp của giám khảo | Tỷ lệ câu có điểm LLM chấm lệch không quá 1 điểm so với điểm bạn chấm |

---

## 8. Rủi ro và cách xử lý

| Rủi ro | Dấu hiệu | Cách xử lý |
|---|---|---|
| Văn bản luật khó tách | Đếm không đủ 220 Điều | Sửa tay các chỗ đặc biệt, ghi lại trong `validate.py` |
| Gemini miễn phí bị giới hạn | Lỗi 429 (thực tế: chỉ 20 request/ngày cho `gemini-2.5-flash`, xác nhận ở Tuần 3) | Cache, chạy đánh giá theo lô nhỏ, dự phòng bằng Groq qua `.with_fallbacks()` |
| Trộn Gemini/Groq khi Gemini hết quota kéo dài gây lỗi trộn định dạng "reasoning" giữa 2 provider | Agent trả lời rỗng sau nhiều vòng gọi liên tiếp | Chưa sửa triệt để (Tuần 3); cần thêm: nếu Gemini lỗi liên tục trong 1 hội thoại thì ép dùng hẳn Groq cho cả hội thoại đó thay vì thử lại Gemini mỗi lần |
| Kaggle hết quota GPU | Không chọn được GPU | Công việc ở đây chỉ tốn vài giờ. Nếu hết thì dùng Colab |
| Reranker chạy chậm trên CPU | p50 trên 3 giây | Rerank top 10 thay vì 20, hoặc làm bản ONNX INT8 |
| Agent lặp vô hạn hoặc gọi quá nhiều công cụ | Số lần gọi công cụ cao | Giới hạn cứng 6 lần gọi và 2 vòng kiểm tra |
| Lỡ tối ưu trên tập test | Số liệu tốt bất thường | Chỉ chạy test ở cuối tuần 2 và tuần 4 |
| Luật thay đổi | Có nghị định mới | Ghi rõ trong README *"Dữ liệu cập nhật đến ngày …"* |
| Thư viện thay đổi API (LangGraph, RAGAS) | Code mẫu trên mạng không chạy | Cố định phiên bản, đọc tài liệu đúng phiên bản |
| **Trễ tiến độ** | Cuối tuần 3 agent chưa chạy | Bỏ rà soát hợp đồng. **Tuyệt đối không bỏ phần đánh giá và tập test** |

---

## 9. Đưa vào CV và chuẩn bị phỏng vấn

### 9.1. Mẫu mô tả trong CV
> **AI Agent tư vấn Luật Lao động Việt Nam** · GitHub · Demo
> - Xây dựng agent bằng **LangGraph** với 6 công cụ: tra cứu điều luật nhiều bước, 5 hàm tính trợ cấp/làm thêm giờ, tự hỏi lại người dùng khi thiếu thông tin; kiểm tra trích dẫn để chống bịa luật
> - Tối ưu tìm kiếm bằng **hybrid search bge-m3 (dense + sparse) + reranker**: Hit@5 **X → Y** trên 100 câu test tự xây dựng; citation precision **Z%**
> - Tách phần tính toán thành công cụ có kiểm thử: độ chính xác **A%**, so với **B%** khi để LLM tự tính
> - Rà soát hợp đồng lao động bằng trích xuất có cấu trúc kết hợp quy tắc pháp lý: phát hiện đúng **C/D** lỗi cài sẵn
> - **Công nghệ:** LangGraph, Qdrant, bge-m3, Gemini, FastAPI, Docker, Kaggle GPU

### 9.2. Câu hỏi phỏng vấn nên chuẩn bị
1. Vì sao chia chunk theo Điều mà không theo độ dài cố định?
2. Hybrid search và RRF hoạt động thế nào? Vì sao cần reranker?
3. Agent của bạn khác pipeline ở điểm nào?
4. Làm sao chống việc LLM bịa luật? Kiểm tra trích dẫn bằng code có những hạn chế gì?
5. Vì sao chia dev/test? Bạn kiểm chứng LLM giám khảo thế nào?
6. Vì sao không để LLM tự tính tiền?
7. Nếu có 1000 người dùng đồng thời thì bạn cần thay đổi gì?
8. Khi luật thay đổi, hệ thống cập nhật thế nào?

---

## 10. Phụ lục: Những gì đã sửa so với plan đầu tiên

| # | Vấn đề trong plan đầu tiên | Mức độ | Đã sửa thành |
|---|---|---|---|
| 1 | Quá tải: 4 tuần × 7 ngày × 3–4 tiếng, quá nhiều tính năng | 🔴 | 5 tuần + 1 tuần dự phòng, khoảng 20 tiếng/tuần; tách MVP và mở rộng |
| 2 | Dùng chung bộ đánh giá để vừa tối ưu vừa báo cáo | 🔴 | Chia **dev** (tối ưu) và **test** (khóa cứng) |
| 3 | Không có mốc "LLM không dùng RAG" | 🔴 | Thêm **V0** |
| 4 | Chưa tính đến Kaggle | 🔴 | Mục 2.2 và mục 6: 3 notebook, luồng dữ liệu local ↔ Kaggle |
| 5 | Chưa tính mô hình phải chạy trên CPU khi dùng app | 🟠 | Đo độ trễ CPU; mở rộng: reranker ONNX INT8 |
| 6 | BM25 + `underthesea` trùng vai trò với vector thưa của bge-m3 | 🟡 | Chỉ dùng vector thưa của bge-m3 |
| 7 | "Hỏi lại" là luồng cố định, không phải agent tự quyết | 🟠 | Chuyển thành công cụ `ask_user` + `interrupt()` |
| 8 | Kiểm tra trích dẫn hoàn toàn bằng LLM | 🟡 | Kiểm tra bằng code trước, LLM chỉ kiểm tra nội dung khi cần |
| 9 | Không kiểm chứng LLM giám khảo | 🟠 | Tự chấm 30 câu và báo cáo mức trùng khớp |
| 10 | Thiếu cache, temperature, cố định phiên bản; Langfuse tự cài nặng | 🟡 | Bổ sung đủ; Langfuse Cloud chuyển sang phần mở rộng |

---

> ⚠️ **Lưu ý:** Các số điều luật và quy tắc tính toán trong file này là để định hướng. Trước khi code, **đối chiếu lại với văn bản gốc trên vbpl.vn**, đặc biệt là nghị định lương tối thiểu vùng vì mức lương được điều chỉnh định kỳ.
