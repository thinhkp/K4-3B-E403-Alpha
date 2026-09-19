# [SIMULATED] Validation session 02 — Nguyễn Văn An

> Dữ liệu mô phỏng để test format hồ sơ. Không phải quote hoặc quan sát từ
> người dùng thật.

- Vai/ngữ cảnh: Học viên K4
- Ngoài nhóm: Có (theo danh sách willing user; chưa thực hiện buổi thật)
- Có phải willing user đã khai báo ở CP1: **Có**
- Ngày/giờ: `— 2026-09-19`
- Người ghi chép: `SIMULATED`
- Prototype/commit được test: `— prototype VLearn Tutor hiện tại`
- Có lỗi mạng/API trong buổi test: Không mô phỏng lỗi

## Trước khi mở prototype

> “Mình đang đánh giá sản phẩm, không đánh giá bạn. Bạn cứ nói to suy nghĩ.
> Nếu bị kẹt, mình sẽ không chỉ màn hình; mình chỉ hỏi bạn sẽ làm gì tiếp.”

### Câu chuyện thật ban đầu

- Câu hỏi: “Bạn nhớ một lần không hiểu nội dung trên VLearn và phải tự dò lại
  không?”
- Ghi tóm tắt trung tính: Người thử muốn câu trả lời ngắn để biết mình nên đọc
  phần nào tiếp theo.
- Quote nguyên văn (mô phỏng): “Nếu không có nguồn thì nói luôn để mình đổi câu
  hỏi, đừng đoán.”

## Task A — Có nguồn

Giao nguyên văn:

> “Bạn đang học Day 1. Hãy dùng công cụ để hiểu `RAG là gì` và chỉ cho mình
> biết bạn sẽ kiểm tra câu trả lời dựa vào đâu.”

- Bắt đầu lúc: `— 14:00`
- Kết thúc lúc: `— 14:03`
- Hoàn thành không trợ giúp: Có
- Hành vi quan sát được (mô phỏng): Nhập câu hỏi về RAG, đọc phần tóm tắt và
  bấm citation sau khi rà qua câu trả lời.
- Người thử có nhận ra citation không: Có
- Người thử có mở/đối chiếu nguồn không: Có
- Điểm kẹt và câu hỏi hỗ trợ đã dùng: Không
- Mức độ: S3 — muốn phần tóm tắt ngắn hơn

## Task B — Không đủ căn cứ

Giao nguyên văn:

> “Bạn muốn biết một thông tin không có trong bài đang chọn. Hãy hỏi công cụ và
> quyết định bạn sẽ làm gì khi công cụ nói chưa đủ căn cứ.”

- Bắt đầu lúc: `— 14:04`
- Kết thúc lúc: `— 14:08`
- Hoàn thành không trợ giúp: Không — cần một câu nhắc trung tính “Bạn sẽ làm
  gì tiếp?”
- Hành vi quan sát được (mô phỏng): Đọc “chưa đủ căn cứ” nhưng ban đầu chờ hệ
  thống tự đề xuất câu hỏi tiếp theo.
- Người thử có hiểu đây là nhánh an toàn không: Có, sau khi đọc lại thông báo.
- Người thử có biết cần thêm ngữ cảnh/đổi phạm vi không: Có, sau câu nhắc.
- Điểm kẹt và câu hỏi hỗ trợ đã dùng: “Bạn sẽ làm gì tiếp?”
- Mức độ: S2 — chưa thấy hành động tiếp theo ngay lập tức

## Sau khi dùng

- Điều hữu ích nhất: Hệ thống nói rõ khi không có căn cứ.
- Điều khó hiểu nhất: Sau fallback chưa rõ nên nhập lại hay đổi phạm vi.
- Nếu sửa một điều, người thử muốn sửa gì: Thêm hai lựa chọn hành động ngay dưới
  thông báo.
- Quote nguyên văn 1 (mô phỏng): “Thông báo an toàn, nhưng mình chưa biết bấm
  gì tiếp.”
- Quote nguyên văn 2 (mô phỏng): “Có hai nút thì mình sẽ đi tiếp nhanh hơn.”
- Mức độ tin cậy người thử tự nói: 3/5 trước khi đọc lại, 4/5 sau khi được
  nhắc (mô phỏng)

## Thay đổi sau feedback

- Vấn đề: Fallback nêu giới hạn nhưng chưa có hành động tiếp theo đủ rõ.
- Quyết định: Sửa trong mô phỏng.
- Thay đổi cụ thể: Bổ sung hai CTA “Bổ sung ngữ cảnh” và “Đổi phạm vi”.
- File/commit liên quan: `— chưa áp dụng vào code`
- Cách kiểm tra lại: Chạy lại Task B; mục tiêu người thử chọn được một CTA mà
  không cần câu nhắc.
