# AI SPEC — Tutor trả lời có căn cứ · Nhóm Alpha · Zone1 E403

**Hướng:** [x] A — VLearn Tutor  
**Loại:** [x] Tối ưu tính năng có sẵn (A1)

## §1. User & Job
- Job executor + workflow (đính kèm worksheet JTBD / ảnh sơ đồ): Học viên K4 đang học trên VLearn, vừa bôi đen một đoạn hoặc đang mở một phần bài học → tự gõ câu hỏi → đọc câu trả lời → đối chiếu lại tài liệu nếu không thấy căn cứ.
- Core JTBD (không tên sản phẩm/AI trong câu): Làm rõ đúng nội dung đang học để tiếp tục bài mà không phải tự dò lại nhiều trang.
- Problem statement (KHÔNG chữ AI): Khi hỏi để làm rõ nội dung đang mở, học viên có thể nhận câu trả lời không có trang nguồn hoặc câu trả lời được đưa ra dù ngữ cảnh chưa đủ; họ không biết dựa vào đâu để kiểm tra, phải tự dò lại và có nguy cơ học sai.
- Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo):
  - Số liệu mining / kết quả khảo sát (n = ?, % xác nhận): Mining 13.494 lượt của 1.617 học viên. Có 3.781 lượt không citation (28,0%; 933 học viên). Sau khi tách `is_preset`, 3.609/10.427 câu tự gõ không citation (34,6%) so với 172/3.067 câu mẫu (5,6%). Riêng K4: 838/2.555 câu tự gõ không citation (32,8%; 191/448 học viên). Trong 536 câu tự gõ K4 dài ≤20 ký tự, chỉ 3 lượt dùng `ask_probing_question`; trung vị câu trả lời là 783 ký tự và 174 lượt dài trên 1.000 ký tự. Phương pháp, quy tắc đếm và giới hạn ghi tại `evidence-log.md`.
  - ≥5 quote/ví dụ nguyên văn + nguồn:
    - `T10506`: “tóm tắt bài lab này” → tutor mô tả toàn bộ Lab 01 và khẳng định “Hiện tại em đang ở checkpoint 2” nhưng không citation; rating down.
    - `T11507`: “21-25” → “đây là nội dung từ trang 21 đến trang 25...” với câu trả lời 2.170 ký tự nhưng không citation.
    - `T13246`: “Tiếp đi” → tutor tự chọn chủ đề để tiếp tục và trả lời 1.454 ký tự, không hỏi lại, không citation.
    - `T11633`: “chi tiết” → tutor giải thích toàn bộ sổ tay 1.442 ký tự, không hỏi mục nào cần chi tiết, không citation.
    - `T11534`: “actor” → tutor đưa định nghĩa 774 ký tự nhưng không có trang để học viên kiểm tra.
    - Đối chứng tốt `T11883`: “mcp la j” → tutor nói nội dung không có trong tài liệu và đề nghị cung cấp thêm ngữ cảnh. Đây là hành vi prototype cần chuẩn hóa.

## §2. Impact & quyết định chọn
- Bảng impact ≥3 ứng viên (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi):

  | Ứng viên | Bao nhiêu người gặp | Tần suất trong log | Mỗi lần tốn gì | Build nổi trong hackathon? | Quyết định |
  |---|---:|---:|---|---|---|
  | A. Grounding gate cho câu tự gõ: đủ nguồn mới trả lời | 901/1.617 HV toàn bộ; 191/448 HV K4 | 3.609/10.427 câu tự gõ không citation (34,6%); K4 838/2.555 (32,8%) | Phải tự dò nguồn; có rủi ro học sai. Số phút chưa đo từ log | Có: kiểm tra retrieval, output contract, citation và fallback | **Chọn** |
  | B. Hỏi làm rõ cho input ngắn/mơ hồ | 785 HV toàn bộ; 212 HV K4 | 2.482 câu tự gõ ≤20 ký tự; chỉ 6 lượt probing. K4 536 lượt, chỉ 3 probing | Có thể nhận câu trả lời sai ý và phải hỏi lại; thời gian chưa đo | Có: ambiguity gate + một câu hỏi ngược | Gộp như failure path của A, không làm feature riêng |
  | C. Tối ưu riêng nút câu hỏi mẫu | 847 HV toàn bộ; 207 HV K4 | 3.067/13.494 lượt (22,7%); K4 542/3.097 | Chưa có bằng chứng pain trực tiếp; câu mẫu đã có citation 94,4% toàn bộ và 99,8% ở K4 | Có | Loại |

- Ứng viên ĐÃ LOẠI + vì sao: Không chọn tối ưu riêng câu mẫu vì phải tách `is_preset` trước khi kết luận nhu cầu; nhóm này có tỷ lệ citation tốt hơn nhiều và chưa có bằng chứng người học đau. Không tách “hỏi làm rõ” thành feature riêng vì nó là đường xử lý khi grounding gate nhận thấy input chưa đủ.
- Ứng viên CHỌN + vì sao (bằng số): Chọn grounding gate cho câu tự gõ. Đây là nhóm 10.427 lượt, trong đó 3.609 lượt (34,6%) không có citation; riêng K4 là 838/2.555 (32,8%). Một quyết định “đủ căn cứ / chưa đủ căn cứ” đồng thời xử lý được rủi ro factuality và input mơ hồ, phù hợp mức automation **conditional** vì sai kiến thức có cost-of-error cao.

## §3. Giải pháp tương tự đã nghiên cứu

- **NotebookLM:** flow là nạp tài liệu → đặt câu hỏi → nhận câu trả lời có trích dẫn. Đáng học: citation đặt cạnh câu trả lời để kiểm tra nhanh. Đáng né: nếu tài liệu đầu vào thiếu, không nên tạo cảm giác chắc chắn. Mình khác: chỉ xử lý một lát cắt nhỏ trong ngữ cảnh bài đang học và có nhánh “chưa đủ căn cứ”.
- **ChatGPT:** flow là nhập câu hỏi → nhận câu trả lời hội thoại. Đáng học: hỏi tiếp và sửa câu hỏi dễ. Đáng né: câu trả lời có thể nghe thuyết phục nhưng không có nguồn học liệu của khóa. Mình khác: ưu tiên nguồn transcript/slide của bài, hiển thị citation và từ chối suy đoán khi không grounding.

## §4. Thiết kế
- Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả): Một học viên K4 đang học chọn phạm vi bài và đặt một câu hỏi; Orchestrator quyết định câu hỏi có đủ ngữ cảnh và nguồn trực tiếp hay không; học viên nhận câu trả lời có citation mở đúng slide, hoặc một đường lui rõ ràng nếu chưa đủ căn cứ.
- Non-goals (≥3 thứ KHÔNG build): Không tự tìm web khi học viên chưa đồng ý; không tạo/chấm quiz hay thay quyết định của giảng viên; không cá nhân hoá dài hạn hoặc suy luận danh tính/năng lực từ `student`; không đồng bộ đăng nhập và trạng thái học thật với VLearn; không trả lời kiến thức ngoài khoá như một chatbot đa dụng.
- Mức prototype nhắm tới: [ ] Sketch [ ] Mock [x] Working — phần chạy thật: React UI, FastAPI, Qdrant retrieval bằng OpenAI embeddings, MongoDB session/feedback, OpenAI tạo câu trả lời, citation mở đúng trang PDF, Tavily chỉ sau consent và dashboard insight. Phần mô phỏng: tài khoản `demo-student`, dropdown chọn bài thay cho ngữ cảnh VLearn thật và dữ liệu chỉ gồm fixture Day 1–2/transcript mẫu.
- Automation: [ ] augment [x] conditional [ ] automate — AI tự trả lời khi có nguồn trực tiếp và citation kiểm chứng được; khi input mơ hồ, sai phạm vi hoặc không có căn cứ thì hỏi lại/dừng và để học viên quyết định đổi phạm vi hay tìm web. Cost-of-error cao vì câu trả lời sai có thể khiến học viên học sai mà không nhận ra, phải dò lại tài liệu hoặc kéo theo lỗi khi làm quiz; sửa sau đó đắt hơn một lượt hỏi lại.
- §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR, xem guide):
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | **G1 — Làm rõ hệ thống làm được gì** | Header ghi “Trả lời có căn cứ từ tài liệu học”; dropdown “Phạm vi câu hỏi” cho biết agent chỉ dùng toàn bộ khoá, Day 1 hoặc Day 2. |
  | **G2 — Làm rõ nó làm tốt đến đâu** | Mỗi câu học thuật hiện citation, thẻ nguồn và slide tương ứng để học viên tự kiểm; khi không có nguồn, UI nói thẳng “Không có trong bài giảng” thay vì trả lời như chắc chắn. |
  | **G10 — Thu hẹp phạm vi khi nghi ngờ** | Các case “Giải thích đoạn này”, “Cái này hoạt động thế nào?” chuyển sang `needs_clarification` và hỏi đúng một câu; không retrieval hoặc trả lời kiến thức trước khi đủ ngữ cảnh. |
  | **G9 — Sửa dễ dàng** | Ô chat luôn sẵn để học viên bổ sung đoạn/tên slide hoặc hỏi lại; dropdown cho phép đổi phạm vi ngay, và citation có thể bấm để kiểm tra rồi sửa câu hỏi. |
  | **G11 — Giải thích vì sao** | Citation `[trang N]`/`[đoạn Txx-NNN]` và thẻ nguồn giải thích câu trả lời dựa vào đâu; click citation mở chính xác tài liệu/trang ở panel trái. |
  | **PAIR — Errors + Graceful Failure** | Prototype tách riêng ba trạng thái: thiếu ngữ cảnh → hỏi lại; không có nguồn → xin consent web; prompt injection/sai phạm vi → chặn hoặc hướng dẫn đổi phạm vi. Mỗi trạng thái có hành động tiếp theo, không dùng chung một thông báo lỗi. |

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
- **Happy path:** Học viên chọn phạm vi → nhập câu hỏi → Input Guard và Intent/Context Gate cho qua → Retrieval Agent lấy nguồn Qdrant → Evidence Gate xác nhận đủ căn cứ → Tutor trả lời ngắn gọn → Citation Verifier giữ citation hợp lệ → học viên bấm citation và xem đúng trang slide ở panel trái → có thể rating.
- **Low-confidence (②):** Input chỉ có “đoạn này/cái này/nó” hoặc đoạn bôi đen quá ngắn → agent không đoán → trả `needs_clarification` với đúng một câu hỏi yêu cầu khái niệm, đoạn liên quan hoặc tên slide → học viên bổ sung rồi flow chạy lại tối đa hai vòng.
- **Failure/không căn cứ (①):** Không có source trả lời trực tiếp hoặc retrieval lỗi → trả “Không có trong bài giảng. Bạn có muốn mình tìm nguồn trên web không?” → chỉ gọi Tavily khi học viên bấm “Tìm nguồn trên web”; bấm “Không, quay lại bài học” thì kết thúc nhánh mà không gọi web.
- **Correction (user sửa):** Học viên có thể đổi phạm vi, bổ sung ngữ cảnh hoặc hỏi lại ngay trong ô chat; có thể mở citation để đối chiếu slide rồi bấm rating Có/Chưa. Câu sửa được đưa lại từ Context Gate, không buộc tiếp tục theo phán đoán cũ.
- **Khi bị đòi ngoài phạm vi (③):** Câu hỏi thời tiết, Bitcoin, lịch sử hoặc code không thuộc bài được chặn trước retrieval và chuyển sang web-consent. Nếu câu hỏi ghi Day 2 nhưng dropdown đang là Day 1, Scope Gate yêu cầu đổi phạm vi và không lấy nguồn Day 2 trái lựa chọn.
- **Case đặc thù domain (④):** Prompt injection → `safe_refusal`, không retrieval/tool; citation do model tạo nhưng không thuộc nguồn → sửa một lần rồi fallback an toàn; OpenAI/Qdrant/Tavily lỗi → retry có giới hạn rồi thông báo ngắn, tuyệt đối không bịa nội dung hoặc URL.

## §7. Kiểm thử

- **Chiều chất lượng và cách chấm:**
  - **Citation đúng nguồn:** đạt khi citation trỏ đúng transcript/slide và đoạn nguồn thực sự hỗ trợ câu trả lời; chấm đạt/không đạt theo từng case.
  - **Không bịa khi thiếu nguồn:** đạt khi hệ thống không khẳng định nội dung và không sinh citation khi không có nguồn hỗ trợ.
  - **Xử lý input mơ hồ:** đạt khi hệ thống hỏi lại thay vì tự chọn một diễn giải.
  - **Ngoài phạm vi:** đạt khi hệ thống từ chối yêu cầu ngoài phạm vi và hướng dẫn người học tới LMS/TA phù hợp.
  - **Đúng thuật ngữ domain:** đạt khi câu trả lời dùng đúng thuật ngữ theo nguồn được trích dẫn, không tự mâu thuẫn với tài liệu.
- **Golden set:** [`eval/golden-set.json`](eval/golden-set.json) gồm 20 case: ít nhất 2 case cho mỗi lớp chỗ khó, 8–10 case thường, 2–4 case hiếm/nguy hiểm và tối thiểu 10 case gắn với `turn_id` từ chatlog thật. Mỗi case có input, nguồn kỳ vọng, lớp chỗ khó và hành vi kỳ vọng.
- **Quality bar (đã chốt cho CP4):** **Đạt khi ≥80% tổng số case trong golden set có câu trả lời đúng và citation truy vết được; đồng thời 100% case không có nguồn phù hợp phải từ chối an toàn, không bịa nội dung hoặc citation.** Quality bar này được giữ nguyên, không điều chỉnh theo kết quả chạy.
- **Kết quả chạy:** [`eval/run-1-results.md`](eval/run-1-results.md) đã liệt kê đủ 20 case; hiện cả 20 case là `NOT_RUN` vì chưa có output từ prototype AI thật. Sau CP3 phải thay bằng output thực tế, PASS/FAIL, tỷ lệ đạt và nguyên nhân thất bại; không xem `NOT_RUN` là kết quả đạt.

## §8. Phân công & kế hoạch

- Nguyễn Minh Thịnh — mining evidence và log trích dẫn.
- Vũ Minh Điềm — retrieval/prompt, tiêu chí “đủ căn cứ”, prototype và AI call thật.
- Phạm Quý — golden set, spec và demo.
- **Willing users:** Đoàn Quang Minh, Nguyễn Văn An, Trần Ngọc Đăng Khoa, Trung Tuyến, Thu Phương.
- **Kế hoạch validation:** mời hai người dùng ngoài nhóm thử một câu hỏi có nguồn và một câu hỏi không có nguồn; ghi task, quan sát, quote nguyên văn và thay đổi sau feedback trong [`validation/README.md`](validation/README.md). Biểu mẫu cho Đoàn Quang Minh và Nguyễn Văn An đã được chuẩn bị tại `validation/`; kết quả chỉ được đánh dấu hoàn tất sau khi có buổi thử thật.

## §9. Changelog

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 18/09/2026 | Cập nhật §1–§6 cho Track A1; bổ sung flow CP2, 4 lớp chỗ khó và 4 nguyên tắc HAX/PAIR | Chuyển Canvas CP1 thành thiết kế prototype có thể kiểm chứng; tập trung vào pain 27,1% lượt K4 không có citation |
| 18/09/2026 | Chốt các chiều chất lượng và quality bar tại §7 | Đóng băng tiêu chí đạt trước khi có kết quả chạy, tránh hạ chuẩn theo số đo |
| Sau CP3 | Bổ sung golden set, kết quả từng case và phân tích lỗi | Ghi nhận trung thực sau khi tích hợp AI thật; không thay đổi quality bar đã chốt |
