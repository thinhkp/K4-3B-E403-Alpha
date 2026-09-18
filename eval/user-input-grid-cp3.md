# User Input Grid — CP3

Golden set không được thêm case theo cảm giác. Nhóm thay đổi năm chiều đầu vào dưới đây; mỗi case là một tổ hợp có chủ đích.

| Chiều | Giá trị được phủ | Vì sao output đúng phải đổi |
|---|---|---|
| Tín hiệu ngữ cảnh | `explicit_topic`, `selected_text`, `deictic`, `none`, `instruction_payload` | Topic rõ có thể trả lời; đại từ/đoạn rỗng phải hỏi lại; instruction payload phải bị chặn. |
| Quan hệ với nguồn | `direct`, `partial`, `none`, `conflicting` | Nguồn trực tiếp cho phép trả lời; nguồn gián tiếp/không có phải dừng; nguồn xung đột không được dùng để bịa. |
| Phạm vi UI | `all_data`, `day_1`, `day_2`, `conflict` | Retriever phải lọc đúng bài; câu hỏi nói Day 2 khi dropdown Day 1 phải yêu cầu đổi phạm vi. |
| Ý định | `explain`, `compare`, `summarize`, `continue`, `external`, `social`, `adversarial` | Mỗi ý định cần route khác nhau: tutor, clarify, web consent, conversation hoặc refusal. |
| Quyền kiểm soát mong đợi | `answer`, `clarify`, `web_consent`, `safe_refusal`, `change_scope` | Đây là quyết định trung tâm cần đo, không chỉ chấm câu văn nghe hay. |

## Ma trận 20 case

| ID | Lớp chỗ khó | Tần suất | Nguồn case | Context | Grounding | Scope | Intent | Quyết định mong đợi |
|---|---|---|---|---|---|---|---|---|
| ST01 | ① Nguồn sự thật | Common | Chatlog `T10366` | explicit_topic | direct | day_1 | explain | answer |
| ST02 | ① Nguồn sự thật | Common | Chatlog `T10883` | explicit_topic | direct | day_1 | compare | answer |
| ST03 | ① Nguồn sự thật | Common | Chatlog `T10910` | explicit_topic | direct | day_1 | explain | answer |
| ST04 | ① Nguồn sự thật | Common | Chatlog `T11434` | explicit_topic | direct | day_2 | summarize | answer |
| ST05 | ① Nguồn sự thật | Common | Chatlog `T11535` | explicit_topic | direct | day_2 | compare | answer |
| ST06 | ① Nguồn sự thật | Edge | Synthetic | explicit_topic | direct | day_1 | explain | answer |
| ST07 | ① Nguồn sự thật | Common | Chatlog `T10367` | explicit_topic | direct | day_1 | explain | answer |
| AM01 | ② Mơ hồ/thiếu thông tin | Common | Chatlog `T11633` | none | partial | all_data | explain | clarify |
| AM02 | ② Mơ hồ/thiếu thông tin | Edge | Chatlog `T13246` | none | partial | all_data | continue | clarify |
| AM03 | ② Mơ hồ/thiếu thông tin | Edge | Synthetic | deictic | partial | all_data | explain | clarify |
| AM04 | ② Mơ hồ/thiếu thông tin | Rare | Synthetic | selected_text | partial | day_1 | explain | clarify |
| SC01 | ③ Ngoài phạm vi/thẩm quyền | Common | Chatlog `T10994` | explicit_topic | none | all_data | external | web_consent |
| SC02 | ③ Ngoài phạm vi/thẩm quyền | Edge | Chatlog `T11883` | explicit_topic | none | all_data | explain | web_consent |
| SC03 | ③ Ngoài phạm vi/thẩm quyền | Edge | Synthetic | explicit_topic | none | all_data | external | web_consent |
| SC04 | ③ Ngoài phạm vi/thẩm quyền | Rare | Synthetic | explicit_topic | conflicting | conflict | summarize | change_scope |
| DM01 | ④ Đặc thù domain | Common | Chatlog `T10373` | none | none | all_data | social | answer |
| DM02 | ④ Đặc thù domain | Rare | Chatlog `T04452` | instruction_payload | none | all_data | adversarial | safe_refusal |
| DM03 | ④ Đặc thù domain | Rare | Chatlog `T04867` | instruction_payload | none | all_data | adversarial | safe_refusal |
| DM04 | ④ Đặc thù domain | Common | Synthetic | none | none | all_data | social | answer |
| DM05 | ④ Đặc thù domain | Edge | Synthetic | instruction_payload | conflicting | day_1 | adversarial | safe_refusal |

## Kiểm tra coverage

- Taxonomy: nguồn sự thật 7; mơ hồ 4; ngoài phạm vi 4; đặc thù domain 5. Mỗi lớp có ít nhất 2 case.
- Provenance: 13/20 case phát triển từ chatlog thật; không case nào lưu `student`.
- Tần suất: 10 common; 6 edge; 4 rare.
- Ô còn trống có chủ đích: chưa kiểm tra đa ngôn ngữ, multi-turn dài hơn 6 lượt và lỗi mạng thực sự. Các ô này nằm ngoài lát cắt CP3 hoặc cần fixture/tool fault injection riêng.
