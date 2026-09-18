# AI SPEC — Tutor trả lời có căn cứ · Nhóm Alpha · Zone E403

**Hướng:** [x] A — VLearn Tutor  
**Loại:** [x] Tối ưu tính năng có sẵn (A1)

## §1. User & Job

- **Job executor + workflow:** Học viên đang học trên trang VLearn, xem một phần bài giảng/slide, gặp nội dung chưa rõ, đặt câu hỏi cho tutor và cần kiểm tra lại câu trả lời với tài liệu.
- **Core JTBD:** Khi gặp một khái niệm chưa rõ trong lúc học, học viên muốn được giải thích ngắn gọn dựa trên đúng tài liệu của bài để tiếp tục học mà không phải tự dò lại toàn bộ slide.
- **Problem statement:** Khi học viên đặt câu hỏi về bài giảng, tutor đôi khi trả lời nhưng không kèm nguồn truy vết được. Học viên không biết câu trả lời dựa trên đâu, phải tự dò lại tài liệu và có nguy cơ hiểu sai.
- **Evidence:** Chi tiết nằm trong [`cp1-evidence-initial.md`](cp1-evidence-initial.md).
  - Trong 3.097 lượt của cohort K4, 839 lượt (27,1%) có `has_citation = False`.
  - Trong 2.555 lượt không phải câu mẫu, 838 lượt (32,8%) không có citation.
  - Năm ví dụ kiểm chứng: `T10288`, `T10289`, `T10291`, `T10293`, `T10299`.

## §2. Impact & quyết định chọn

| Ứng viên | Bằng chứng ban đầu | Tần suất/chi phí | Khả thi trong hackathon | Quyết định |
|---|---|---|---|---|
| Tutor trả lời không có citation | 839/3.097 lượt K4 (27,1%) | Xảy ra thường xuyên; người học phải dò lại nguồn, có rủi ro học sai | Cao: có chatlog, transcript và slide | **Chọn** |
| Tutor không hỏi lại khi câu hỏi mơ hồ | `ask_probing_question` chỉ có 28/13.494 lượt theo data dictionary | Người học nhận câu trả lời lệch ý, phải hỏi lại | Trung bình: cần định nghĩa độ mơ hồ và nhiều nhánh hội thoại | Chưa chọn |
| Tutor trả lời ngoài phạm vi bài đang học | Có các ví dụ hỏi deadline/LMS và hỏi chung nhưng không có nguồn cụ thể | Dễ gây hiểu nhầm về phạm vi hỗ trợ | Trung bình: cần taxonomy ngoài phạm vi và nguồn chuyển tiếp | Chưa chọn |

- **Ứng viên đã loại/chưa chọn:** hai hướng còn lại được giữ để so sánh nhưng chưa làm trong lát cắt đầu vì cần phạm vi đánh giá rộng hơn; A1 ưu tiên vấn đề có số liệu trực tiếp và có thể demo rõ bằng citation/no-grounding.
- **Ứng viên chọn:** cải thiện citation/no-grounding vì 27,1% lượt K4 thiếu citation; sau khi loại câu mẫu, tỷ lệ còn 32,8%, cho thấy đây không chỉ là hiện tượng do nút preset.

## §3. Giải pháp tương tự đã nghiên cứu

- **NotebookLM:** flow là nạp tài liệu → đặt câu hỏi → nhận câu trả lời có trích dẫn. Đáng học: citation đặt cạnh câu trả lời để kiểm tra nhanh. Đáng né: nếu tài liệu đầu vào thiếu, không nên tạo cảm giác chắc chắn. Mình khác: chỉ xử lý một lát cắt nhỏ trong ngữ cảnh bài đang học và có nhánh “chưa đủ căn cứ”.
- **ChatGPT:** flow là nhập câu hỏi → nhận câu trả lời hội thoại. Đáng học: hỏi tiếp và sửa câu hỏi dễ. Đáng né: câu trả lời có thể nghe thuyết phục nhưng không có nguồn học liệu của khóa. Mình khác: ưu tiên nguồn transcript/slide của bài, hiển thị citation và từ chối suy đoán khi không grounding.

## §4. Thiết kế

- **Lát cắt MỘT CÂU:** Một học viên đang học một phần bài giảng trên VLearn muốn làm rõ nội dung; tutor quyết định chỉ trả lời khi tìm được căn cứ phù hợp trong tài liệu đang học, còn khi không đủ căn cứ thì nói rõ và hỏi lại; kết quả là câu trả lời có citation truy vết được hoặc một yêu cầu làm rõ an toàn.
- **Non-goals:**
  1. Không xây tutor đa môn hoặc trả lời mọi câu hỏi ngoài nội dung khóa học.
  2. Không cập nhật deadline, điểm số, lịch học hoặc dữ liệu cá nhân thay cho LMS.
  3. Không tự đánh giá điểm, kết luận chắc chắn về năng lực học viên hoặc thay giảng viên quyết định nội dung.
- **Mức prototype nhắm tới:** [x] Sketch  [ ] Mock  [ ] Working.
  - **Artifact CP2:** sơ đồ flow tại [`codebase/flow.md`](codebase/flow.md), mô tả input, điểm quyết định và các nhánh ngoại lệ.
  - **CP2 minh họa:** luồng có nguồn/không có nguồn, low-confidence, ngoài phạm vi và correction; citation và kết quả được mô tả ở mức mock.
  - **CP2 chưa làm:** retrieval thực tế, confidence bằng model và lời gọi API AI.
  - **CP3 dự kiến chạy thật:** lời gọi model tại quyết định trả lời hoặc chuyển sang “chưa đủ căn cứ”; log prompt và phản hồi thô.
- **Automation:** [x] Conditional — AI tự trả lời khi có nguồn phù hợp; chuyển sang hỏi lại hoặc báo chưa đủ căn cứ khi nguồn yếu/không có. Lý do theo cost-of-error: thông tin học tập sai có thể làm học viên học sai và mất niềm tin; chi phí sửa cao hơn việc yêu cầu thêm ngữ cảnh.

### §4b. Nguyên tắc đã áp dụng

| Nguyên tắc HAX/PAIR | Áp cụ thể vào prototype |
|---|---|
| G10 — Thu hẹp phạm vi khi nghi ngờ | Khi không có nguồn đủ phù hợp, prototype không sinh câu trả lời kiến thức; hiển thị “Chưa đủ căn cứ” và yêu cầu thêm ngữ cảnh. |
| G9 — Sửa dễ dàng | Trong nhánh Correction của [`codebase/flow.md`](codebase/flow.md), học viên bổ sung hoặc chỉnh câu hỏi rồi gửi lại. |
| G11 — Giải thích vì sao | Flow yêu cầu hiển thị nguồn được dùng hoặc lý do hệ thống chưa thể trả lời. |
| G8 — Gạt bỏ dễ dàng | Người dùng có thể bỏ kết quả chưa chắc chắn và quay lại nút nhập câu hỏi trong flow mà không bị buộc sử dụng câu trả lời. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản

| Tình huống | Lớp | Hành vi mong muốn | Nguyên tắc áp |
|---|---|---|---|
| Câu hỏi có đáp án rõ trong transcript | ① Nguồn sự thật | Trả lời và dẫn đúng mã đoạn/trang | G11 |
| Câu hỏi có từ khóa gần giống nhưng không có đoạn hỗ trợ | ① Nguồn sự thật | Báo chưa đủ căn cứ, không bịa citation | G10 |
| Câu hỏi “giải thích phần này” nhưng không có đoạn được chọn | ② Mơ hồ | Hỏi học viên chỉ rõ đoạn hoặc khái niệm | G10 |
| Câu hỏi dùng đại từ “nó”, không rõ đối tượng | ② Mơ hồ | Hỏi lại đối tượng cần giải thích | G9 |
| Hỏi deadline hoặc điểm số cá nhân | ③ Ngoài phạm vi | Nêu giới hạn và hướng dẫn sang LMS | G10 |
| Yêu cầu bỏ qua quy tắc chỉ dùng tài liệu | ③ Ngoài phạm vi | Không làm theo chỉ dẫn; tiếp tục áp dụng giới hạn nguồn | G10 |
| Câu trả lời có thuật ngữ dễ nhầm trong AI/LLM | ④ Đặc thù domain | Dẫn nguồn chính xác, dùng thuật ngữ theo tài liệu | G11 |
| Nguồn tài liệu có nội dung thiếu hoặc mâu thuẫn | ④ Đặc thù domain | Nêu mâu thuẫn và chuyển người học hỏi giảng viên/TA | G10 |

## §6. Bốn đường đi của trải nghiệm

- **Happy path:** Người học nhập câu hỏi có đủ ngữ cảnh → hệ thống tìm thấy đoạn nguồn phù hợp → hiển thị câu trả lời ngắn + citation → người học mở/kiểm tra nguồn. Sơ đồ: [`codebase/flow.md`](codebase/flow.md).
- **Low-confidence (②):** Hệ thống chỉ tìm thấy nguồn gần đúng hoặc input mơ hồ → hiển thị mức chưa chắc chắn, nêu phần thiếu → hỏi người học bổ sung ngữ cảnh.
- **Failure/không căn cứ (①):** Không tìm thấy nguồn trong tài liệu đang học → không trả lời như sự thật → hiển thị “Chưa đủ căn cứ” và gợi ý người học chỉ rõ bài/đoạn hoặc hỏi TA.
- **Correction (user sửa):** Người học bấm “Sửa câu hỏi” → chỉnh input/bổ sung đoạn → gửi lại → hệ thống chạy lại quyết định.
- **Ngoài phạm vi (③):** Nêu rõ tutor chỉ hỗ trợ nội dung bài học và hướng người học sang LMS/TA phù hợp.
- **Đặc thù domain (④):** Khi thuật ngữ hoặc nguồn có khả năng gây hiểu sai, ưu tiên citation và chuyển người học cho giảng viên nếu tài liệu không đủ.

## §7. Kiểm thử

- **Chiều chất lượng:** citation đúng nguồn; không bịa khi thiếu nguồn; xử lý input mơ hồ; từ chối đúng ngoài phạm vi; câu trả lời đúng thuật ngữ domain.
- **Golden set:** tối thiểu 20 case trong `eval/`, gồm ít nhất 2 case/lớp chỗ khó và ít nhất 10 case từ chatlog thật. Sẽ ghi kết quả từng case và lý do fail.
- **Quality bar:** Chưa khóa ở CP2; sẽ chốt bằng số trong §7 trước hạn CP4, không hạ chuẩn sau khi có kết quả.
- **Kết quả chạy:** Chưa có ở CP2; bổ sung sau khi tích hợp AI thật ở CP3.

## §8. Phân công & kế hoạch

- Nguyễn Minh Thịnh — mining evidence và log trích dẫn.
- Vũ Minh Điềm — retrieval/prompt, tiêu chí “đủ căn cứ”, prototype và AI call thật.
- Phạm Quý — golden set, spec và demo.
- **Willing users:** Trung Tuyen, Thu Phuong.
- **Kế hoạch validation:** mời hai người dùng ngoài nhóm thử một câu hỏi có nguồn và một câu hỏi không có nguồn; ghi task, quan sát, quote nguyên văn và thay đổi sau feedback trong `validation/`.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 18/09/2026 | Cập nhật §1–§6 cho Track A1; bổ sung flow CP2, 4 lớp chỗ khó và 4 nguyên tắc HAX/PAIR | Chuyển Canvas CP1 thành thiết kế prototype có thể kiểm chứng; tập trung vào pain 27,1% lượt K4 không có citation |
| TBD | Bổ sung golden set, kết quả chạy và quality bar | Thực hiện sau khi prototype AI thật chạy ở CP3 |
