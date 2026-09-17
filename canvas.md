# Canvas CP1 — VLearn Tutor trả lời có căn cứ

**Đội trưởng:** Nguyễn Minh Thịnh · **Mã học viên:** 2A202602556

| # | Dòng | Nội dung |
|---|---|---|
| 1 | Track + đề | **A · VLearn Tutor — trả lời có căn cứ từ tài liệu.** |
| 2 | Job executor (ai · đang ở đâu · làm gì) | Học viên K4 đang học trên VLearn, vừa bôi đen một đoạn hoặc đang mở một phần bài học và tự gõ câu hỏi để hiểu tiếp. |
| 3 | Pain một câu (ai – đang làm gì – vướng đâu – hậu quả) | Khi hỏi để làm rõ nội dung đang mở, học viên có thể nhận câu trả lời không có trang nguồn hoặc tutor vẫn trả lời khi ngữ cảnh chưa đủ; học viên không biết dựa vào đâu để kiểm tra nên phải tự dò lại và có nguy cơ học sai. |
| 4 | 1–2 bằng chứng đầu | **Toàn bộ log:** 3.781/13.494 lượt không có citation (28,0%; 933 HV). Sau khi tách câu mẫu, câu tự gõ không citation là 3.609/10.427 (34,6%) so với 172/3.067 câu mẫu (5,6%). **K4:** 838/2.555 câu tự gõ không citation (32,8%; 191 HV); trong 536 câu tự gõ ≤20 ký tự chỉ 3 lượt dùng `ask_probing_question`, độ dài trả lời trung vị 783 ký tự. *Cách đếm:* lọc `has_citation`, tách `is_preset`, bỏ tiền tố ngữ cảnh rồi đo phần tự gõ. *Mã minh họa:* `T10506`, `T11507`, `T13246`, `T11633`, `T11534`; log đầy đủ tại `evidence-log.md`. |
| 5 | Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả) | Một học viên đang đọc tài liệu và hỏi về nội dung đang mở · AI quyết định **nguồn hiện có đã đủ căn cứ hay chưa** · nếu đủ thì trả lời đúng cỡ kèm `[trang N]`, nếu thiếu thì nói rõ giới hạn và hỏi đúng một câu làm rõ · học viên biết câu nào có thể kiểm tra và phải làm gì tiếp. |
| 6 | AI tự làm đến đâu + 1 dòng lý do · ≥3 willing users ngoài nhóm | **Conditional:** tự truy xuất và trả lời khi có đoạn nguồn phù hợp; không suy đoán khi không tìm được nguồn hoặc input mơ hồ, mà nêu “chưa đủ căn cứ” và yêu cầu thêm ngữ cảnh. *Lý do:* sai kiến thức khiến học viên học sai và mất niềm tin, nên cost-of-error cao hơn một lượt hỏi lại. **Willing users:** Đoàn Quang Minh · Nguyễn Văn An · Trần Ngọc Đăng Khoa. |
| 7 | Phân công có tên | **Nguyễn Minh Thịnh** — đội trưởng, canvas/spec, prompt và tiêu chí “đủ căn cứ” · **Phạm Xuân Quý** — mining evidence, bảng đếm và `turn_id` · **Vũ Minh Điềm** — prototype UI và lời gọi AI thật · **Phan Đại Cương** — golden set, user test, demo và changelog. |
