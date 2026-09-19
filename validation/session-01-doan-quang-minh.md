# [] Validation session 01 — Đoàn Quang Minh

> Dữ liệu mô phỏng để test format hồ sơ. Không phải quote hoặc quan sát từ
> người dùng thật.

- Vai/ngữ cảnh: Học viên K4
- Ngoài nhóm: Có (theo danh sách willing user; chưa thực hiện buổi thật)
- Có phải willing user đã khai báo ở CP1: **Có**
- Ngày/giờ: ` — 2026-09-19`
- Người ghi chép: ``
- Prototype/commit được test: ` — prototype VLearn Tutor hiện tại`
- Có lỗi mạng/API trong buổi test: Không mô phỏng lỗi

## Trước khi mở prototype

> “Mình đang đánh giá sản phẩm, không đánh giá bạn. Bạn cứ nói to suy nghĩ.
> Nếu bị kẹt, mình sẽ không chỉ màn hình; mình chỉ hỏi bạn sẽ làm gì tiếp.”

### Câu chuyện thật ban đầu

- Câu hỏi: “Bạn nhớ một lần không hiểu nội dung trên VLearn và phải tự dò lại
  không?”
- Ghi tóm tắt trung tính: Người thử thường muốn biết câu trả lời lấy từ slide nào
  trước khi tin nội dung.
- Quote nguyên văn (mô phỏng): “Có số trang thì mình yên tâm hơn vì còn mở ra
  kiểm tra được.”

## Task A — Có nguồn

Giao nguyên văn:

> “Bạn đang học Day 1. Hãy dùng công cụ để hiểu `RAG là gì` và chỉ cho mình
> biết bạn sẽ kiểm tra câu trả lời dựa vào đâu.”

- Bắt đầu lúc: ` — 10:00`
- Kết thúc lúc: ` — 10:03`
- Hoàn thành không trợ giúp: Có
- Hành vi quan sát được (mô phỏng): Chọn Day 1, nhập câu hỏi, đọc câu trả lời,
  nhận ra thẻ citation và mở nguồn để kiểm tra.
- Người thử có nhận ra citation không: Có
- Người thử có mở/đối chiếu nguồn không: Có
- Điểm kẹt và câu hỏi hỗ trợ đã dùng: Dừng ngắn ở thẻ nguồn, tự đọc tiếp;
  không cần hỗ trợ.
- Mức độ: S3 — hơi chậm khi tìm liên kết nguồn

## Task B — Không đủ căn cứ

Giao nguyên văn:

> “Bạn muốn biết một thông tin không có trong bài đang chọn. Hãy hỏi công cụ và
> quyết định bạn sẽ làm gì khi công cụ nói chưa đủ căn cứ.”

- Bắt đầu lúc: ` — 10:04`
- Kết thúc lúc: ` — 10:06`
- Hoàn thành không trợ giúp: Có
- Hành vi quan sát được (mô phỏng): Nhập câu hỏi ngoài nội dung Day 1, đọc thông
  báo chưa đủ căn cứ và chọn quay lại bổ sung ngữ cảnh.
- Người thử có hiểu đây là nhánh an toàn không: Có
- Người thử có biết cần thêm ngữ cảnh/đổi phạm vi không: Có
- Điểm kẹt và câu hỏi hỗ trợ đã dùng: Không
- Mức độ: S3 — muốn nút “Đổi phạm vi” nổi bật hơn

## Sau khi dùng

- Điều hữu ích nhất: Citation mở được nguồn cụ thể.
- Điều khó hiểu nhất: Nhãn “Phạm vi câu hỏi” chưa nổi bật.
- Nếu sửa một điều, người thử muốn sửa gì: Đưa hành động “Đổi phạm vi” cạnh
  thông báo chưa đủ căn cứ.
- Quote nguyên văn 1 (mô phỏng): “Mình thích là nó không cố trả lời khi không
  có nguồn.”
- Quote nguyên văn 2 (mô phỏng): “Nút đổi phạm vi nên dễ thấy hơn.”
- Mức độ tin cậy người thử tự nói: 4/5 (mô phỏng)

## Thay đổi sau feedback

- Vấn đề: Hành động đổi phạm vi chưa đủ nổi bật.
- Quyết định: Sửa trong mô phỏng.
- Thay đổi cụ thể: Đưa CTA “Đổi phạm vi” vào vùng fallback và giữ citation ở
  cạnh câu trả lời.
- File/commit liên quan: ` — chưa áp dụng vào code`
- Cách kiểm tra lại: Chạy lại Task B và đo thời gian tìm CTA.
