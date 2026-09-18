# Script quay video demo dự phòng — CP5

Dùng file này như teleprompter: mở song song với màn hình đang quay. Cột **"Đọc to"** là câu bạn nói ra miệng; cột **"Làm trên màn hình"** là hành động bấm/gõ đúng lúc đó. Hai case dưới đây (ST01, AM01) là 2 case đã **PASS thật** ở golden set run 1 — chọn đúng 2 case này để tránh rủi ro AI trả lời lệch ngay lúc quay.

Trước khi bấm quay: mở `http://localhost:8000`, refresh trang để có session mới (tránh lịch sử chat cũ lẫn vào), tắt thông báo/Slack, phóng to trình duyệt toàn màn hình.

Tổng thời lượng ước tính: **60–75 giây**.

---

## 0. Mở đầu (0:00 – 0:12)

**Làm trên màn hình:** Ở màn hình chờ, chưa gõ gì.

**Đọc to:**
> "Đây là VLearn Tutor — tutor trả lời có căn cứ từ tài liệu học của khoá K4. Mình sẽ demo hai trường hợp: một câu có nguồn trả lời trực tiếp, và một câu mơ hồ để xem hệ thống xử lý thế nào."

---

## 1. Case chuẩn — có nguồn (0:12 – 0:40)

**Làm trên màn hình:**
1. Ở dropdown **"Phạm vi câu hỏi"**, chọn **"Chỉ Day 1 · AI & LLM Foundation"**.
2. Gõ vào ô **"Câu hỏi của bạn"**: `LLM bản chất là gì?`
3. Bấm gửi (nút mũi tên), để tự nhiên chạy — không tua nhanh.

**Đọc to (trong lúc hệ thống đang xử lý, agent trace hiện: Input Guard → Retrieval Agent → Evidence Gate → Tutor Response Agent → Citation Verifier):**
> "Mình chọn phạm vi Day 1, rồi hỏi 'LLM bản chất là gì?'. Hệ thống đang chạy qua các bước: kiểm tra input, truy xuất nguồn trong slide, kiểm tra đủ căn cứ hay chưa, rồi mới sinh câu trả lời."

**Khi câu trả lời hiện ra (có citation `[trang 10]`):**
> "Câu trả lời ra kèm trích dẫn `[trang 10]` — mình bấm vào citation này..."

**Làm trên màn hình:** Bấm vào nút citation `[trang 10]`. Panel bên trái mở đúng trang 10 của slide PDF.

**Đọc to:**
> "...và nó mở đúng trang 10 trong slide bài giảng — học viên có thể tự kiểm tra ngay, không phải tin mù."

---

## 2. Case khó — input mơ hồ (0:40 – 1:05)

**Làm trên màn hình:**
1. Gõ vào ô câu hỏi: `Chi tiết`
2. Bấm gửi.

**Đọc to (ngay khi gõ, trước khi gửi):**
> "Giờ mình thử một câu mơ hồ — chỉ gõ 'Chi tiết', không nói rõ chi tiết về cái gì."

**Khi kết quả hiện ra (không có citation nào, hệ thống hỏi lại đúng một câu):**
> Đọc nguyên văn câu hỏi lại mà Tutor hiển thị trên màn hình (đọc đúng như nó hiện, không bịa thêm), sau đó nói thêm:
> "Hệ thống không đoán và không tự trả lời khi chưa rõ ngữ cảnh — nó hỏi lại đúng một câu, và không sinh citation nào cả vì chưa có căn cứ để trả lời."

---

## 3. Kết (1:05 – 1:15)

**Làm trên màn hình:** Quay lại giao diện tổng, không cần thao tác thêm.

**Đọc to:**
> "Đó là hai nhánh chính: có nguồn thì trả lời kèm trích dẫn kiểm tra được, chưa đủ căn cứ thì hỏi lại — không bịa. Cảm ơn đã theo dõi."

---

## Lưu ý khi quay

- Nếu case khó ("Chi tiết") lỡ trả lời thẳng thay vì hỏi lại (hiếm, nhưng có thể do model không tất định), **dừng, refresh session, quay lại từ bước 1 của case đó** — đừng quay tiếp và giải thích, vì đây là video dự phòng phải "sạch", không lỗi.
- Không đọc số liệu golden set (16/20, 80%) trong video này — phần đó đã có ở slide 4/6 của `demo-slides.pdf`. Video này chỉ chứng minh sản phẩm chạy đúng như lúc live.
- Tên file gợi ý khi xuất: `cp5-demo-backup.mp4`, đặt trong `codebase/` cạnh `cp3-live-ai-demo.mp4` — cùng pattern `cp{N}-<mục đích>.mp4`, tránh lẫn với video CP3.
