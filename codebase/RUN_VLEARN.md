# Chạy VLearn Grounded Tutor tại máy

Từ root của repo, chạy `cd codebase`. Tất cả lệnh dưới đây chạy trong thư mục `codebase/`; dữ liệu nằm ở `../data/` và khóa API nằm trong `../.env`.

1. Nếu chưa có file môi trường, chạy `Copy-Item .env.example ../.env`, rồi tự điền `OPENAI_API_KEY` và `TAVILY_API_KEY`. Không commit `.env`.
2. Tạo/cập nhật môi trường ảo: `uv sync`.
3. Chạy database cục bộ: `docker compose up -d`.

4. Lần đầu, tạo semantic chunks, embeddings Qdrant và insight K4: `uv run python scripts/ingest.py`.
   Khi chỉ thay đổi cách đọc slide/tài liệu, chạy nhanh: `uv run python scripts/ingest.py --documents-only`.
5. Chạy web app: `uv run python -m uvicorn app.main:app --reload`.
6. Mở `http://localhost:8000`.

Khi sửa frontend, chạy `npm install` rồi `npm run build` trước bước 5 để cập nhật `dist/`.

Kiểm tra dịch vụ tại `http://localhost:8000/api/health`. Qdrant chạy cổng `6333`; MongoDB chạy cổng `27017`.

Luồng Agent: Orchestrator → Safety → Intent/Context → Qdrant Retrieval → Evidence Gate → OpenAI Tutor → Citation Verifier → Learning Insight. Tavily chỉ được gọi sau khi học viên bấm đồng ý tìm web.
