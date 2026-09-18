# Evidence ban đầu — Track A1: Tutor trả lời thiếu căn cứ

## Nguồn và phương pháp đếm

- **Nguồn:** `data/vlearn-pack/chatlog/tutor_turns.csv`.
- **Đơn vị đếm:** một dòng tương ứng với một lượt hỏi–đáp giữa học viên và tutor.
- **Phạm vi chính:** các dòng có `cohort_hint = K4`, gồm **3.097 lượt**.
- **Tiêu chí “thiếu căn cứ” trong lượt mining đầu:** `has_citation = False`.
- **Kết quả:** **839/3.097 lượt = 27,1%** không có citation.
- **Kiểm tra loại bỏ ảnh hưởng câu mẫu:** trong 2.555 lượt không phải câu mẫu (`is_preset = False`), **838 lượt = 32,8%** không có citation.
- **Cách kiểm lại:** lọc CSV theo các điều kiện trên, đếm số dòng và chia cho tổng số dòng trong cùng phạm vi. Có thể dùng `turn_id` để mở lại từng ví dụ.

> Chỉ số “không có citation” là bằng chứng về vấn đề truy vết nguồn; nhóm cần bổ sung khảo sát hoặc phỏng vấn người dùng để xác nhận mức độ ảnh hưởng và chi phí thực tế của pain.

## Năm ví dụ nguyên văn có thể kiểm chứng

Các trích đoạn dưới đây được lấy từ phản hồi tutor trong những lượt K4, không phải câu mẫu và có `has_citation = False`. Nội dung đã giữ nguyên trạng thái ẩn danh của data pack.

### 1. `T10288` — D01

- **Câu hỏi:** “phần lab này dùng để làm gì ?”
- **Trích phản hồi tutor:** “Vì hiện tại chưa có nội dung chi tiết của slide bài học, em có thể cho anh biết cụ thể hơn về những công cụ hoặc thư viện em đang làm trong lab này không?”
- **Vấn đề quan sát:** tutor đưa ra giải thích chung nhưng không chỉ ra đoạn/trang nguồn cụ thể.

### 2. `T10289` — D01

- **Câu hỏi:** “tôi phải làm gì ? ở đây”
- **Trích phản hồi tutor:** “Thông thường, quy trình này sẽ bao gồm: 1. **Thiết lập môi trường**... 2. **Chạy test baseline**...”
- **Vấn đề quan sát:** phản hồi dùng kiến thức “thông thường” và hướng dẫn chung, không có citation để học viên đối chiếu với bài đang học.

### 3. `T10291` — D01

- **Câu hỏi:** “Dựa trên tiến độ của mình, mình nên ôn phần nào trước?”
- **Trích phản hồi tutor:** “Vì em đang ở màn tổng quan của Day01, em nên bắt đầu bằng việc nắm vững các khái niệm nền tảng được giới thiệu trong buổi học đầu tiên này.”
- **Vấn đề quan sát:** tutor đưa ra khuyến nghị học tập nhưng không dẫn nguồn hoặc đoạn nội dung làm căn cứ.

### 4. `T10293` — D01

- **Câu hỏi:** “tôi đang có bài tập gì phải hoàn thành, và hạn là bao giờ”
- **Trích phản hồi tutor:** “Thông tin cụ thể về danh mục bài tập và thời hạn nộp bài thường được giảng viên cập nhật trên hệ thống quản lý học tập (LMS) của khoá học.”
- **Vấn đề quan sát:** tutor chuyển người học sang LMS nhưng không nêu được nguồn/mục cụ thể để mở ngay.

### 5. `T10299` — D01

- **Câu hỏi:** “so what I should do”
- **Trích phản hồi tutor:** “Chào [HV], với tư cách là trợ giảng, chị gợi ý em nên bắt đầu bằng việc đọc qua tài liệu hoặc slide bài giảng của **Day01**...”
- **Vấn đề quan sát:** lời khuyên ở mức khái quát, không có đoạn/trang cụ thể để người học kiểm tra hoặc bắt đầu.

## Diễn giải pain cho CP1

Trong các ví dụ trên, tutor vẫn tạo ra phản hồi có vẻ hữu ích nhưng người học không thể kiểm tra nhanh câu trả lời dựa trên nội dung nào. Vì vậy, A1 sẽ tập trung vào **một quyết định duy nhất**: chỉ trả lời như câu trả lời kiến thức khi có căn cứ phù hợp; nếu không có căn cứ thì nói rõ giới hạn và hỏi lại/thông báo hướng tìm kiếm, thay vì suy đoán.

## Việc cần bổ sung sau CP1

- [ ] Hỏi ít nhất 2–3 học viên về một lần gần nhất họ phải tự dò lại tài liệu sau khi hỏi tutor.
- [ ] Nếu có thể, hoàn thiện chuẩn A: khảo sát ít nhất 20 người ngoài nhóm, có câu hỏi và câu trả lời nguyên văn.
- [ ] Khi xây golden set, thêm các câu hỏi ngoài phạm vi, câu hỏi mơ hồ và câu hỏi có prompt injection để kiểm tra tutor không bịa nguồn.
