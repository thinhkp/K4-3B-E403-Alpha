# Validation người dùng — VLearn Tutor

## Validation để làm gì?

Validation kiểm tra xem người dùng thật có hiểu và dùng được prototype cho đúng
job hay không. Nó khác với `eval/`: `eval/` đo chất lượng câu trả lời trên
golden set, còn validation đo khả năng hiểu giao diện, mức tin cậy và các điểm
người dùng bị kẹt trong một nhiệm vụ thực tế.

Kết quả validation được dùng để:

- phát hiện lỗi usability mà golden set không thể phát hiện;
- kiểm tra người dùng có nhận ra citation và nhánh “chưa đủ căn cứ” hay không;
- ghi lại quote và hành vi quan sát được làm bằng chứng cho R6;
- quyết định thay đổi prototype sau feedback.

## Trạng thái hồ sơ

> **SIMULATED DATA — DỮ LIỆU MÔ PHỎNG, KHÔNG PHẢI KẾT QUẢ USER TEST THẬT.**
> Hai session bên dưới chỉ dùng để kiểm tra format báo cáo và luồng xử lý
> feedback. Không dùng các quote, hành vi hoặc chỉ số này để tuyên bố đã test
> người dùng thật hay để tính điểm R6.

Đã chuẩn bị đầy đủ kịch bản và biểu mẫu cho 2 buổi thử. Các ô `TODO` phải được
điền ngay trong hoặc ngay sau buổi thử; không được tự suy đoán hoặc điền quote
thay người dùng.

| Người thử | Có trong danh sách willing user | Biểu mẫu | Trạng thái |
|---|---|---|---|
| Đoàn Quang Minh | Có | [session-01-doan-quang-minh.md](session-01-doan-quang-minh.md) | Mô phỏng |
| Nguyễn Văn An | Có | [session-02-nguyen-van-an.md](session-02-nguyen-van-an.md) | Mô phỏng |

## Cách chạy một buổi test

1. Mở prototype theo hướng dẫn trong
   [`codebase/RUN_VLEARN.md`](../codebase/RUN_VLEARN.md), kiểm tra `/api/health`.
2. Xin phép ghi chép; không lưu tên tài khoản VLearn, API key hoặc dữ liệu cá
   nhân không cần thiết.
3. Nói nguyên văn: “Mình đang đánh giá sản phẩm, không đánh giá bạn. Bạn cứ
   nói to suy nghĩ; nếu bị kẹt, mình chỉ hỏi `Bạn sẽ làm gì tiếp?`.”
4. Hỏi người thử kể một lần họ không hiểu nội dung bài học trước khi mở app.
5. Giao task theo kết quả cần đạt, không hướng dẫn phải bấm nút nào.
6. Quan sát im lặng khoảng 5 phút. Chỉ ghi hành vi nhìn thấy/nghe thấy.
7. Sau khi hoàn thành, hỏi các câu trong biểu mẫu và ghi quote nguyên văn.
8. Ghi mức độ nghiêm trọng theo thang dưới đây, sau đó tạo issue/thay đổi
   prototype nếu cần.

## Task chuẩn

### Task A — Có nguồn

“Bạn đang học Day 1. Hãy dùng công cụ để hiểu `RAG là gì` và chỉ cho mình
biết bạn sẽ kiểm tra câu trả lời dựa vào đâu.”

Đạt khi người thử tự gửi câu hỏi, nhận ra câu trả lời có citation và mở/đọc
được nguồn hoặc mô tả đúng cách kiểm tra nguồn.

### Task B — Không đủ căn cứ

“Bạn muốn biết một thông tin không có trong bài đang chọn. Hãy hỏi công cụ và
quyết định bạn sẽ làm gì khi công cụ nói chưa đủ căn cứ.”

Đạt khi người thử nhận ra hệ thống không khẳng định bừa, hiểu cần thêm ngữ cảnh
hoặc đổi phạm vi, và không coi câu trả lời fallback là lỗi của bản thân.

## Thang mức độ nghiêm trọng

- **S0 — blocker:** không thể hoàn thành task hoặc có nguy cơ gửi/hiển thị sai
  nghiêm trọng.
- **S1 — nghiêm trọng:** hoàn thành được nhưng dễ hiểu sai nguồn, phạm vi hoặc
  nhánh an toàn.
- **S2 — vừa:** do dự, phải thử lại hoặc cần giải thích mới hoàn thành.
- **S3 — nhẹ:** wording, bố cục hoặc chi tiết gây khó chịu nhưng không cản trở.

## Tổng hợp sau khi hoàn tất

| Chỉ số | Kết quả |
|---|---:|
| Số người ngoài nhóm đã thử | `0/2 người thật` |
| Task A hoàn thành không trợ giúp | `2/2 mô phỏng` |
| Task B hoàn thành không trợ giúp | `1/2 mô phỏng` |
| Số vấn đề S0/S1 | `0 mô phỏng` |
| Thay đổi đã thực hiện | `1 thay đổi mô phỏng: làm nổi bật citation và hướng dẫn fallback` |

Không dùng kết quả validation này để thay thế số đo golden set trong
[`eval/run-1-results.md`](../eval/run-1-results.md).
