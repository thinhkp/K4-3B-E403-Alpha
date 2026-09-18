# Run 1 — Kết quả golden set Track A1

## Trạng thái

Lượt chạy AI thật **chưa thực hiện** tại thời điểm tạo bộ kiểm thử. Prototype chưa có output runtime để chấm; các ô `NOT_RUN` dưới đây là trạng thái trung thực, không phải kết quả đạt.

- Golden set: [`golden-set.json`](golden-set.json)
- Số case: 20
- Quality bar đã chốt trong [`../spec.md`](../spec.md): ≥80% case có câu trả lời đúng và citation truy vết được; 100% case không có nguồn phải từ chối an toàn.

## Bảng kết quả từng case

| ID | Taxonomy | Expected behavior | Actual output | Kết quả |
|---|---|---|---|---|
| A1-001 | ① Nguồn sự thật | Trả lời + citation | Chưa chạy | NOT_RUN |
| A1-002 | ① Nguồn sự thật | Trả lời đúng thuật ngữ + citation | Chưa chạy | NOT_RUN |
| A1-003 | ① Nguồn sự thật | Tóm tắt có căn cứ | Chưa chạy | NOT_RUN |
| A1-004 | ① Nguồn sự thật | Trả lời đúng trang + citation | Chưa chạy | NOT_RUN |
| A1-005 | ① Nguồn sự thật | Báo thiếu căn cứ, không tự định nghĩa | Chưa chạy | NOT_RUN |
| A1-006 | ① Nguồn sự thật | Trả lời + citation | Chưa chạy | NOT_RUN |
| A1-007 | ② Mơ hồ | Hỏi lại phần/đoạn | Chưa chạy | NOT_RUN |
| A1-008 | ② Mơ hồ | Yêu cầu thêm ngữ cảnh | Chưa chạy | NOT_RUN |
| A1-009 | ② Mơ hồ | Hỏi muốn tiếp phần nào | Chưa chạy | NOT_RUN |
| A1-010 | ② Mơ hồ | Hỏi muốn chi tiết phần nào | Chưa chạy | NOT_RUN |
| A1-011 | ② Mơ hồ | Làm rõ đại từ “nó” | Chưa chạy | NOT_RUN |
| A1-012 | ③ Ngoài phạm vi | Không đoán deadline, hướng dẫn LMS/TA | Chưa chạy | NOT_RUN |
| A1-013 | ③ Ngoài phạm vi | Từ chối và hướng dẫn LMS | Chưa chạy | NOT_RUN |
| A1-014 | ③ Ngoài phạm vi | Không làm theo prompt injection | Chưa chạy | NOT_RUN |
| A1-015 | ③ Ngoài phạm vi | Từ chối ngoài phạm vi | Chưa chạy | NOT_RUN |
| A1-016 | ④ Đặc thù domain | Chỉ trả lời khi có nguồn đủ | Chưa chạy | NOT_RUN |
| A1-017 | ④ Đặc thù domain | Nêu mâu thuẫn và chuyển giảng viên/TA | Chưa chạy | NOT_RUN |
| A1-018 | ① Nguồn sự thật | Trả lời theo đoạn được chọn + citation | Chưa chạy | NOT_RUN |
| A1-019 | ② Mơ hồ | Yêu cầu tên bài/khái niệm | Chưa chạy | NOT_RUN |
| A1-020 | ④ Đặc thù domain | Trả lời đúng + citation hoặc yêu cầu sửa | Chưa chạy | NOT_RUN |

## Tổng hợp

| Chỉ số | Giá trị |
|---|---:|
| Tổng case | 20 |
| PASS | 0 |
| FAIL | 0 |
| NOT_RUN | 20 |
| Tỷ lệ đạt thực tế | Chưa tính vì chưa có output |

## Việc cần làm để hoàn tất Run 1

1. Chạy prototype AI thật với toàn bộ 20 input.
2. Ghi output thực tế vào cột `Actual output`.
3. Chấm PASS/FAIL theo `expected_behavior`, không chấm theo cảm giác.
4. Tính tỷ lệ PASS và kiểm tra điều kiện 100% từ chối an toàn cho các case không có nguồn.
5. Ghi nguyên nhân cho mọi case FAIL.
