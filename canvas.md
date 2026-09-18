# Canvas CP1 — Track A1

| # | Dòng | Nội dung |
|---|---|---|
| 1 | Track + đề | **Track A — VLearn Tutor, A1: tối ưu tutor hiện có để không trả lời thiếu căn cứ.** |
| 2 | Job executor (ai · đang ở đâu · làm gì) | **Học viên đang học trên trang VLearn**, ở phần bài giảng hoặc slide, đặt câu hỏi để hiểu nội dung đang xem. |
| 3 | Pain một câu (ai – đang làm gì – vướng đâu – hậu quả) | Khi học viên hỏi về nội dung bài giảng, tutor đôi khi trả lời nhưng **không kèm nguồn truy vết được**, khiến học viên không biết câu trả lời dựa trên đâu, phải tự dò lại tài liệu và có nguy cơ học sai. |
| 4 | 1–2 bằng chứng đầu | Trong 3.097 lượt của cohort K4, **839 lượt (27,1%) có `has_citation = False`**. Cách đếm: lọc `cohort_hint = K4`, sau đó đếm `has_citation = False` trong `data/vlearn-pack/chatlog/tutor_turns.csv`. Trong các câu hỏi không phải câu mẫu, có **838/2.555 lượt (32,8%)** không có citation. Ví dụ kiểm chứng được: `T10288`, `T10289`, `T10291`, `T10293`, `T10299`. |
| 5 | Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả) | **Một học viên đang học một phần bài giảng trên VLearn muốn làm rõ nội dung; tutor quyết định chỉ trả lời khi tìm được căn cứ phù hợp trong tài liệu đang học, còn khi không đủ căn cứ thì nói rõ và hỏi lại; kết quả là câu trả lời có trích dẫn truy vết được hoặc một yêu cầu làm rõ an toàn.** |
| 6 | AI tự làm đến đâu + 1 dòng lý do · willing users | **AI tự** tìm đoạn nguồn phù hợp, trả lời ngắn gọn và gắn mã/trang nguồn; **AI không tự đoán** khi không tìm thấy căn cứ mà chuyển sang thông báo “chưa đủ căn cứ” và hỏi lại. Lý do: câu trả lời không có citation đang chiếm 27,1% lượt K4; câu trả lời học tập không kiểm chứng được có thể làm học viên hiểu sai. **Willing users ngoài nhóm:** Trung Tuyen, Thu Phuong. |
| 7 | Phân công có tên | Nguyễn Minh Thịnh — mining evidence và log trích dẫn · Vũ Minh Điềm — retrieval/prompt và tiêu chí “đủ căn cứ” · Vũ Minh Điềm — prototype và AI call thật · Phạm Quý — golden set, spec và demo. |

