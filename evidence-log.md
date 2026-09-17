# Nhật ký bằng chứng nháp — VLearn Tutor trả lời có căn cứ

## 1. Phạm vi và nguồn

- Nguồn: `data/vlearn-pack/chatlog/tutor_turns.csv`; đối chiếu định nghĩa cột trong `data/vlearn-pack/chatlog/DATA_DICTIONARY.md`.
- Toàn bộ dữ liệu: 13.494 lượt hỏi–đáp, 1.617 học viên, từ 22/07 đến 15/09/2026.
- Lát cắt K4: 3.097 lượt, 448 học viên, từ 09/09/2026.
- Không đưa data pack vào commit. Tệp này chỉ giữ số tổng hợp, `turn_id` và trích đoạn ngắn đã ẩn danh.

## 2. Nhật ký đọc mẫu trước khi đếm

Đã đọc 50 lượt K4 không phải câu mẫu, lấy bằng `sample(n=50, random_state=17)`, sau đó đọc thêm các lượt có câu hỏi rất ngắn, thiếu citation hoặc rating down. Các pattern quan sát được trước khi đặt quy tắc đếm:

1. Câu hỏi tự gõ thường phụ thuộc mạnh vào màn hình hoặc lượt chat trước: “Tiếp đi”, “chi tiết”, “giải thích slide này”.
2. Tutor thường chọn `review_concept` và trả lời ngay, kể cả khi ý định chưa rõ.
3. Một số câu trả lời mô tả nội dung bài học hoặc vị trí checkpoint nhưng không có `[trang N]` để người học đối chiếu.
4. Tutor đôi lúc đã làm đúng: nói nội dung nằm ngoài tài liệu và đề nghị người học cung cấp thêm ngữ cảnh. Hành vi này cần được biến thành quy tắc nhất quán.

## 3. Quy tắc đếm có thể kiểm lại

- **Thiếu citation:** `has_citation == False`. Đây là cờ audit về khả năng kiểm chứng, **không tự động đồng nghĩa với hallucination**.
- **Câu mẫu / câu tự gõ:** tách bằng `is_preset` trước khi kết luận học viên hỏi gì.
- **Câu tự gõ ngắn:** `is_preset == False`; bỏ tiền tố ngữ cảnh trước `)\n`; phần học viên tự gõ dài không quá 20 ký tự. Đây là proxy để tìm input dễ mơ hồ, không phải nhãn mơ hồ chuẩn vàng.
- **Trả lời dài cho câu ngắn:** nhóm trên có `reply_len > 1.000` ký tự.
- **Hỏi làm rõ:** `move_used == "ask_probing_question"`.

## 4. Số liệu thống kê

| Chỉ số | Toàn bộ log | Riêng K4 |
|---|---:|---:|
| Tổng lượt / học viên | 13.494 / 1.617 | 3.097 / 448 |
| Không có citation | 3.781 (28,0%) · 933 HV | 839 (27,1%) · 191 HV |
| Câu tự gõ | 10.427 | 2.555 |
| Câu tự gõ không có citation | 3.609/10.427 (34,6%) · 901 HV | 838/2.555 (32,8%) · 191 HV |
| Câu mẫu không có citation | 172/3.067 (5,6%) | 1/542 (0,2%) |
| Câu tự gõ ngắn ≤20 ký tự | 2.482 (23,8% câu tự gõ) · 785 HV | 536 (21,0%) · 212 HV |
| Trong nhóm câu ngắn: dùng `ask_probing_question` | 6/2.482 (0,24%) | 3/536 (0,56%) |
| Độ dài trả lời trung vị cho câu ngắn | 740 ký tự | 783 ký tự |
| Câu ngắn nhưng trả lời >1.000 ký tự | 841/2.482 (33,9%) · 307 HV | 174/536 (32,5%) · 85 HV |

Toàn bộ 13.494 lượt chỉ có 28 lượt dùng `ask_probing_question` (0,21%); 12.127 lượt dùng `review_concept` (89,9%). Rating chỉ xuất hiện ở 177 lượt (1,3%), nên không dùng rating làm thước đo chính.

## 5. Ví dụ nguyên văn từ chatlog

Các câu dưới đây được giữ nguyên chính tả. Phần trả lời chỉ trích ngắn vài dòng theo quy định không đưa nguyên data pack lên repo công khai.

### T10506 · K4 · không citation · rating down

- Học viên: “tóm tắt bài lab này”
- Tutor: “Chào [HV], bài Lab 01 này được thiết kế để em làm quen với việc sử dụng LLM API thông qua các bước cụ thể: [...] Hiện tại em đang ở checkpoint 2, mục tiêu là chạy được bộ test baseline trước khi bắt đầu đi vào hiện thực hóa các chức năng trong `template.py`.”
- Ghi nhận: trả lời 929 ký tự, đưa ra nội dung và trạng thái checkpoint nhưng không có nguồn để kiểm tra; đây là một trong ba rating down của K4.

### T11507 · K4 · không citation

- Học viên: “21-25”
- Tutor: “Chào [HV], đây là nội dung từ trang 21 đến trang 25 của tài liệu: **Trang 21: Định Nghĩa** [...] **Trang 22: ReAct Loop: Thought → Action → Observation** [...]”
- Ghi nhận: câu trả lời dài 2.170 ký tự và khẳng định nội dung theo từng trang nhưng không có citation chuẩn `[trang N]`.

### T13246 · K4 · không citation

- Học viên: “Tiếp đi”
- Tutor: “Chào [HV], để tiếp tục phần "Kiến thức trọng tâm" về tư duy sản phẩm AI, chúng ta cần nắm vững một chuyển dịch tư duy quan trọng: **Từ "Tính năng" sang "Giá trị từ dự đoán".**”
- Ghi nhận: input phụ thuộc lịch sử, nhưng tutor không hỏi “tiếp từ phần nào” và trả lời 1.454 ký tự.

### T11633 · K4 · không citation

- Học viên: “chi tiết”
- Tutor: “Chào [HV], phần "Sổ tay từ điển" cung cấp định nghĩa cho các khái niệm nền tảng mà em sẽ sử dụng xuyên suốt quá trình thực hành để mô tả bài toán. Dưới đây là các thuật ngữ chính: [...]”
- Ghi nhận: ý định chưa chỉ ra mục cần giải thích; tutor trả lời 1.442 ký tự thay vì hỏi một câu làm rõ.

### T11534 · K4 · không citation

- Học viên: “actor”
- Tutor: “Trong "Sổ tay từ điển" của buổi học, **Actor** (Người gặp vấn đề) được định nghĩa là người đang thực sự đối mặt với khó khăn hoặc điểm nghẽn trong quy trình.”
- Ghi nhận: nội dung có vẻ phù hợp nhưng học viên không có trang nguồn để tự kiểm tra.

### T11883 · K4 · không citation · đối chứng hành vi tốt

- Học viên: “mcp la j”
- Tutor: “Chào [HV], nội dung bài học hôm nay tại trang 1-46 của tài liệu "Day03_Từ Chatbot Đến Agentic Agent" không đề cập đến khái niệm "MCP". [...] Nếu em đang làm lab và thấy thuật ngữ này trong hướng dẫn, em có thể cho anh biết thêm ngữ cảnh cụ thể để anh hỗ trợ tốt hơn.”
- Ghi nhận: tutor đã nêu giới hạn và gợi ý bước tiếp theo. Prototype nên chuẩn hóa hành vi này thay vì luôn cố trả lời.

## 6. Kết luận tạm thời và giới hạn

- Signal mạnh nhất là khả năng kiểm chứng: 34,6% câu tự gõ không có citation, cao hơn nhiều so với 5,6% câu mẫu. Riêng K4 là 32,8% so với 0,2%.
- Signal thứ hai là thiếu làm rõ: trong 2.482 câu tự gõ ngắn chỉ 6 lượt chọn nước đi hỏi ngược, trong khi 33,9% nhận câu trả lời dài trên 1.000 ký tự.
- Chọn bài toán **grounding gate**: trước khi trả lời, tutor quyết định tài liệu có đủ căn cứ không. Đủ thì trả lời kèm trang; thiếu hoặc mơ hồ thì nêu rõ và hỏi đúng một câu làm rõ.
- Chưa đo được citation đúng trang hay sai trang chỉ từ `has_citation`; cần golden set và kiểm tra nội dung ở CP3–CP4.
- Chưa có phỏng vấn người dùng ở giai đoạn này. Ba willing users đã đồng ý cho vòng validation: Đoàn Quang Minh, Nguyễn Văn An, Trần Ngọc Đăng Khoa.
