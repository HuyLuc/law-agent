# AI Agent tư vấn Luật Lao động Việt Nam

> 🚧 Đang xây dựng theo [PLAN.md](./PLAN.md). Xem file đó để biết lộ trình đầy đủ, tiến độ và các quyết định thiết kế.

## Mục tiêu

Agent trả lời câu hỏi về Bộ luật Lao động Việt Nam, kèm trích dẫn điều luật, tính toán chính xác các khoản trợ cấp/lương, tự hỏi lại khi thiếu thông tin, và rà soát hợp đồng lao động.

## Trạng thái

Tuần 0 (Chuẩn bị) — xem bảng tiến độ trong [PLAN.md § 5](./PLAN.md#5-lộ-trình-từng-tuần).

## Chạy thử (sẽ cập nhật khi có Docker Compose ở Tuần 5)

```bash
cp .env.example .env   # điền GEMINI_API_KEY, GROQ_API_KEY
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Lời lưu ý pháp lý

Nội dung do agent trả lời chỉ mang tính tham khảo, không thay thế tư vấn pháp lý chuyên nghiệp.
