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
| LLM chính | **Gemini 2.5 Flash** | Kiểm tra giới hạn gói miễn phí tại thời điểm làm |
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
| 0 | Chuẩn bị | Repo, API key, Kaggle đã xác minh | ⬜ |
| 1 | Dữ liệu | `chunks.jsonl`, `dev.jsonl` | ⬜ |
| 2 | Tìm kiếm | V0–V3, tập test đã khóa | ⬜ |
| 3 | Agent | V4 chạy được | ⬜ |
| 4 | Đánh giá + hợp đồng | Bảng kết quả hoàn chỉnh | ⬜ |
| 5 | Đóng gói | Docker, README, video demo | ⬜ |
| 6 | Dự phòng | Sửa lỗi, phần mở rộng | ⬜ |

---

### 🔧 Tuần 0: Chuẩn bị (2 buổi)

🎯 Mọi công cụ đã sẵn sàng, không bị vướng khi bắt đầu làm.

✅ **Việc cần làm**
- [ ] 💻 Tạo repo GitHub (public), `.gitignore` (bỏ qua `.env`, `data/embeddings/`, `*.db`), Python venv
- [ ] 💻 Chạy Qdrant:
  ```bash
  docker run -p 6333:6333 -v qdrant_data:/qdrant/storage qdrant/qdrant
  ```
- [ ] 🌐 Lấy API key Gemini và Groq, gọi thử mỗi bên 1 lần, **ghi lại giới hạn** số lần gọi mỗi phút và mỗi ngày
- [ ] ☁️ Kaggle:
  - [ ] **Xác minh số điện thoại** (bắt buộc để bật GPU và Internet cho notebook)
  - [ ] Tải `kaggle.json` (Settings → API → Create New Token) và đặt vào `~/.kaggle/`
  - [ ] Thêm Gemini key vào **Kaggle Secrets** (Add-ons → Secrets)
  - [ ] Chạy thử 1 notebook trên GPU T4, `pip install FlagEmbedding` xem có lỗi không
- [ ] 💻 Tạo `Makefile` với các lệnh: `make ingest`, `make index`, `make test`, `make eval`, `make up`
- [ ] 💻 Tạo `.env.example`:
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

#### Buổi 1: Thu thập văn bản 💻
- [ ] Tải từ **vbpl.vn** (Cơ sở dữ liệu quốc gia về văn bản pháp luật):
  - [ ] Bộ luật Lao động 2019 (45/2019/QH14)
  - [ ] Nghị định 145/2020/NĐ-CP
  - [ ] Nghị định **lương tối thiểu vùng mới nhất** (tra số hiệu trên vbpl.vn)
- [ ] Ghi `data/raw/sources.yaml` cho mỗi văn bản:
  ```yaml
  - id: BLLD2019
    ten: Bộ luật Lao động 2019
    so_hieu: 45/2019/QH14
    ngay_ban_hanh: 2019-11-20
    hieu_luc_tu: 2021-01-01
    nguon: <link vbpl.vn>
    file: raw/blld2019.html
  ```

#### Buổi 2–3: Tách văn bản 💻 `src/ingestion/parser.py`
- [ ] Đọc HTML bằng BeautifulSoup, chuyển sang text, chuẩn hóa khoảng trắng và Unicode (NFC)
- [ ] Nhận diện cấu trúc bằng regex:

  | Cấp | Regex |
  |---|---|
  | Chương | `^Chương [IVXLC]+` |
  | Điều | `^Điều \d+\.` |
  | Khoản | `^\d+\.` |
  | Điểm | `^[a-zđ]\)` |

- [ ] Quy tắc chia chunk:
  - **Mỗi Điều là 1 chunk**
  - Điều nào dài hơn khoảng 800 token thì tách theo Khoản, mỗi chunk con **giữ lại tiêu đề Điều** ở đầu
- [ ] Lấy danh sách điều được dẫn chiếu bằng regex `Điều (\d+)` và lưu vào trường `dan_chieu`

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

#### Buổi 4: Kiểm tra dữ liệu 💻 `validate.py` + `tests/test_parser.py`
- [ ] BLLĐ 2019 phải đủ **220 Điều**, không thiếu số, không trùng số
- [ ] Không có chunk rỗng. In ra thống kê độ dài chunk: min, trung vị, max
- [ ] Mở ngẫu nhiên **20 chunk** để xem bằng mắt
- [ ] Sửa thủ công những chỗ đặc biệt và ghi lại trong code (không cố viết regex hoàn hảo)

#### Buổi 5: Tập dev (40 câu) 💻
- [ ] Các nhóm câu hỏi:

  | Nhóm (`loai`) | Số câu | Ví dụ |
  |---|---|---|
  | `tra_cuu` | 15 | "Thời gian thử việc tối đa là bao lâu?" |
  | `tinh_huong` | 12 | "Công ty bắt tôi thử việc 3 tháng cho vị trí kế toán có đúng không?" |
  | `nhieu_dieu` | 8 | "Bị cho nghỉ không báo trước thì được bồi thường những gì?" |
  | `ngoai_pham_vi` | 5 | "Thủ tục ly hôn thế nào?" |

- [ ] Mỗi câu **tự tra** và ghi `dieu_can_trich`. **Không để LLM tự tạo đáp án.**

📦 `chunks.jsonl`, `dev.jsonl`, test cho parser chạy qua.
🚦 Kiểm tra dữ liệu không có lỗi, và bạn đã tự đọc 20 chunk mẫu.

---

### 🔍 Tuần 2: Tìm kiếm, số liệu nền, khóa tập test

🎯 Tối ưu phần tìm kiếm trên tập dev, có số liệu V0–V3, **khóa tập test**.

#### Buổi 1: Tạo embedding trên Kaggle ☁️ `kaggle/01_embed_chunks.ipynb`
- [ ] 💻 Đưa dữ liệu lên Kaggle (xem [mục 6](#6-hướng-dẫn-làm-việc-với-kaggle))
- [ ] ☁️ Chọn GPU T4 và bật Internet
- [ ] ☁️ Chạy:
  ```python
  from FlagEmbedding import BGEM3FlagModel
  model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
  out = model.encode(texts, batch_size=16, max_length=1024,
                     return_dense=True, return_sparse=True)
  # lưu parquet: id | dense (list[float]) | sparse (dict token_id → weight)
  ```
- [ ] 💻 Tải kết quả về `data/embeddings/`
- ⏱️ Khoảng 1–3 nghìn chunk chỉ mất vài phút trên T4.

#### Buổi 2: Đưa vào Qdrant và viết các phiên bản tìm kiếm 💻
- [ ] `index_qdrant.py`: tạo collection có **2 loại vector** (`dense` 1024 chiều cosine, `sparse`) và đưa metadata vào payload
- [ ] `embedder.py`: tạo embedding cho câu hỏi trên CPU, **cùng mô hình bge-m3**
- [ ] `hybrid.py`: dùng Query API của Qdrant, `prefetch` dense + sparse rồi gộp bằng **RRF**
- [ ] `reranker.py`: lấy top 20 → rerank → giữ top 5
- [ ] **Đo độ trễ trên CPU:** thời gian tạo embedding câu hỏi và thời gian rerank 20 kết quả (ms). Ghi lại để so sánh sau
- [ ] Viết **V0** (chỉ LLM) để làm mốc so sánh

#### Buổi 3: Đánh giá phần tìm kiếm trên Kaggle ☁️ `kaggle/02_eval_retrieval.ipynb`
- [ ] Đưa chunk + embedding vào `QdrantClient(":memory:")` ngay trong notebook, không cần Docker
- [ ] Chạy V1/V2/V3 trên tập dev, tính **Hit@5** và **MRR@10** (dùng lại đúng code `eval/retrieval_metrics.py`)
- [ ] Không cần gọi LLM nên chạy nhanh, không bị giới hạn API
- [ ] Thử thay đổi và ghi lại kết quả từng lần:
  - [ ] kích thước chunk (theo Điều hay theo Khoản)
  - [ ] top-k khi prefetch (20 / 50)
  - [ ] số lượng kết quả đưa vào reranker (10 / 20)
- [ ] **Chỉ tối ưu trên tập dev**

#### Buổi 4–5: Tạo và khóa tập test 💻
- [ ] 100 câu mới, **không trùng với tập dev**:

  | `tra_cuu` | `tinh_huong` | `nhieu_dieu` | `ngoai_pham_vi` |
  |---|---|---|---|
  | 35 | 30 | 20 | 15 |

- [ ] Tạo `calc.jsonl` với 40 tình huống tính toán, **tự tính tay đáp án** (8 tình huống cho mỗi hàm)
- [ ] Commit với nội dung `freeze test set v1`. **Không sửa `test.jsonl` và `calc.jsonl` nữa**
- [ ] Chạy V1/V2/V3 trên tập test **1 lần** và lưu vào `eval/results/`

📦 Bảng số liệu tìm kiếm V1–V3, số đo độ trễ trên CPU, tập test đã khóa.
🚦 Hit@5 của V3 trên tập dev đạt từ **0.8** trở lên. Nếu chưa đạt thì xem lại cách chia chunk trước khi làm agent.

---

### 🤖 Tuần 3: Công cụ và agent

🎯 Agent chạy được từ đầu đến cuối với đủ công cụ.

#### Buổi 1: Các hàm tính toán 💻 `src/tools/calculators.py`

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

- [ ] Kiểm tra dữ liệu đầu vào bằng Pydantic (không nhận lương âm, số tháng âm…)
- [ ] 🚦 Chạy qua **40/40** test

#### Buổi 2: Công cụ tra luật 💻 `src/tools/legal_lookup.py`

| Công cụ | Chữ ký | Cách hoạt động |
|---|---|---|
| `search_law` | `(query: str, van_ban: str \| None = None)` | Dùng V3 từ tuần 2, trả về top 5 kèm `id` |
| `get_article` | `(van_ban: str, dieu: int, khoan: int \| None = None)` | **Lọc chính xác theo metadata**, không dùng tìm kiếm ngữ nghĩa |
| `follow_references` | `(chunk_id: str)` | Trả về các điều nằm trong `dan_chieu` |

- [ ] Viết **docstring kỹ** cho mỗi công cụ, vì LLM đọc docstring để quyết định gọi công cụ nào
- [ ] Mỗi kết quả trả về được lưu vào `state["evidence"]` để bước kiểm tra trích dẫn dùng lại

#### Buổi 3–4: Dựng graph bằng LangGraph 💻 `src/agent/`

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

- [ ] Viết `graph.py`, vẽ graph bằng `graph.get_graph().draw_mermaid()` để đưa vào README
- [ ] Viết CLI đơn giản (`python -m src.agent.graph "câu hỏi"`) để thử nhanh

#### Buổi 5: Prompt và thử nghiệm 💻 `src/agent/prompts.py`

Các quy tắc bắt buộc trong system prompt:
1. Chỉ khẳng định điều gì khi có căn cứ trong kết quả công cụ. Không có thì nói *"không tìm thấy căn cứ"*.
2. **Mọi phép tính đều phải gọi hàm tính**, không tự tính.
3. Nếu thiếu thông tin quyết định (loại hợp đồng, thâm niên, lương) thì **gọi `ask_user`**, không tự giả định.
4. Mỗi nhận định pháp lý kèm `[Điều X, <tên văn bản>]`.
5. Kết thúc bằng lời lưu ý: *chỉ mang tính tham khảo, không thay thế tư vấn pháp lý*.

- [ ] Bật `temperature=0` và `SQLiteCache`
- [ ] Chạy thử 10 câu trong tập dev, **đọc lại từng bước agent đã làm**, sửa prompt và docstring công cụ

📦 **V4 = Agent** chạy được trên CLI, có 3 ví dụ mẫu (tra luật, tính toán, hỏi lại).
🚦 Agent xử lý đúng ít nhất **8/10** câu thử, và **không có trường hợp tự tính tiền**.

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

#### Buổi 3–4: Rà soát hợp đồng 💻 `src/tools/contract_rules.py`
1. [ ] Đọc PDF/DOCX dạng chữ bằng `pypdf` hoặc `python-docx`
2. [ ] LLM **trích thông tin có cấu trúc** (Pydantic): loại hợp đồng, vị trí, số ngày thử việc, lương thử việc, lương chính, giờ làm, BHXH, thời hạn
3. [ ] **Kiểm tra bằng quy tắc lập trình sẵn** (không để LLM tự đánh giá):

   | Quy tắc | Căn cứ |
   |---|---|
   | Thời gian thử việc tối đa 180/60/30/6 ngày tùy vị trí | Điều 25 |
   | Lương thử việc từ 85% lương chính trở lên | Điều 26 |
   | Lương không thấp hơn lương tối thiểu vùng | NĐ lương tối thiểu vùng |
   | Giờ làm bình thường không quá 8 giờ/ngày, 48 giờ/tuần | Điều 105 |
   | Hợp đồng có đủ các nội dung bắt buộc | Điều 21 |

4. [ ] Mỗi cảnh báo ⚠️ kèm trích dẫn nguyên văn điều luật lấy qua `get_article`
- [ ] Tự tạo **10 hợp đồng mẫu** (8 hợp đồng có cài lỗi, 2 hợp đồng đúng), đo precision/recall của việc phát hiện lỗi
- [ ] Viết `tests/test_contract_rules.py`

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

#### Buổi 1: FastAPI 💻 `src/api/main.py`

| Endpoint | Chức năng |
|---|---|
| `POST /chat` | Trả về từng phần bằng SSE, kèm `thread_id` để giữ hội thoại |
| `POST /chat/resume` | Trả lời câu hỏi của `ask_user` |
| `POST /review-contract` | Tải hợp đồng lên và nhận danh sách cảnh báo |
| `GET /health` | Kiểm tra API, Qdrant và LLM |

#### Buổi 2: Streamlit 💻 `src/ui/app.py`
- [ ] Khung chat và ô tải hợp đồng lên
- [ ] **Thanh bên hiển thị các điều luật đã trích** (bấm vào để xem nguyên văn)
- [ ] Hiển thị các bước agent đã làm (đã gọi công cụ nào). Phần này rất ấn tượng khi demo

#### Buổi 3: Docker 💻
- [ ] `docker-compose.yml` gồm 3 service: `qdrant`, `api`, `ui`
- [ ] Tải sẵn mô hình vào image hoặc dùng volume cache của Hugging Face để không phải tải lại mỗi lần chạy
- [ ] `make ingest`: đưa file embedding parquet vào Qdrant
- [ ] 🚦 **Clone repo vào thư mục mới và chạy lại từ đầu**

#### Buổi 4: README 💻
1. [ ] Giới thiệu 1 câu + GIF demo
2. [ ] Sơ đồ kiến trúc (Mermaid từ LangGraph)
3. [ ] **Bảng kết quả V0 → V4** kèm giải thích ngắn
4. [ ] Các quyết định thiết kế: chia theo Điều · hybrid + rerank · không để LLM tính toán · kiểm tra trích dẫn bằng code · chia dev/test
5. [ ] Phân tích lỗi và hạn chế
6. [ ] Cách chạy (Docker và Kaggle)
7. [ ] Lời lưu ý pháp lý và ngày cập nhật dữ liệu

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
1. [ ] Sửa lỗi, `ruff`, type hints, tăng test coverage
2. [ ] ☁️ `03_onnx_reranker.ipynb`: chuyển reranker sang ONNX INT8, đo **độ trễ trên CPU trước/sau** và Hit@5 (đảm bảo không giảm nhiều)
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
| Gemini miễn phí bị giới hạn | Lỗi 429 | Cache, chạy đánh giá theo lô nhỏ, dự phòng bằng Groq |
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
