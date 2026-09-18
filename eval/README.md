# CP3 evaluation artifacts

## Bộ nộp chính

- `golden-set-cp3.json`: 20 case máy đọc được, có expected assertions và User Input Grid dimensions.
- `user-input-grid-cp3.md`: ma trận coverage 5 chiều; 7/4/4/5 case cho bốn lớp chỗ khó.
- `run-1-results.json`: response đầy đủ và kết quả chấm tự động của từng case.
- `run-1-results.md`: thống kê 16/20 đạt (80%) và phân tích nguyên nhân bốn case sai.
- `run-1-model-traces.jsonl`: 9 lần gọi OpenAI thật trong run 1, gồm prompt thực tế, raw response và latency; không có API key hoặc user ID.
- Video thao tác thật: `../codebase/cp3-live-ai-demo.mp4`, thời lượng 29,37 giây.

## Provenance và quyền riêng tư

- 13/20 case phát triển từ `data/vlearn-pack/chatlog/tutor_turns.csv`.
- Chỉ lưu `turn_id`, cohort và mô tả biến đổi; không lưu trường `student`.
- Case được chọn sau khi lọc `is_preset = False`; câu hỏi đưa vào test đã bỏ tiền tố ngữ cảnh UI hoặc chuẩn hóa lỗi gõ khi cần.
- CSV gốc không được copy vào `eval/` và không được commit.

## Chạy lại

Khởi động backend tại cổng 8000, sau đó từ `codebase/` chạy:

```powershell
uv run python scripts/run_eval.py
```

Runner tạo mới `eval/run-1-results.json` và `eval/run-1-results.md`. Trace model được append vào `codebase/runtime/model_calls.jsonl`; thư mục `runtime/` bị loại khỏi Git.

## Tài liệu exploratory trước khi khóa golden set

- `golden-set-cp3.md` và các thư mục `evidence*` là lượt kiểm thử tay trước đó, dùng để chưng cất tiêu chí pass/fail.
- `fix-verification-cp3.md` ghi vòng sửa và retest có mục tiêu. Số đo CP3 chính thức của run 1 là số trong `run-1-results.json`.
