

## Tóm tắt bài lab

Mục tiêu là xây dựng **một tính năng sản phẩm AI nhỏ**, gồm:

1. **AI Spec** đầy đủ từ §1–§9.
2. **Prototype chạy end-to-end**, có ít nhất một lần gọi AI thật.
3. **Golden set tối thiểu 20 case** và kết quả đo định lượng.
4. **Slide demo 6 trang**, video demo dự phòng.
5. Repository GitHub công khai đúng cấu trúc.
6. Mỗi thành viên có reflection cá nhân.

Tài liệu chính cần bám theo:

- `intruc.md`
- `01-challenge-brief.md`
- `02-guide.md`
- `03-ai-spec-template.md`
- `04-rubric.md`

---

# 1. Việc cần làm ngay

## Thành lập nhóm

- Nhóm gồm **3–4 người**.
- Chọn một đội trưởng duy nhất.
- Đội trưởng phải dùng **cùng một mã học viên cho cả CP1–CP5**.
- Mỗi thành viên phải biết rõ phần việc của mình để trả lời khi giám khảo hỏi.

## Chọn track và đề cụ thể

Chỉ chọn **một track** và **một đề**:

| Track | Nội dung | Dữ liệu chính |
|---|---|---|
| A | VLearn Tutor | Chatlog tutor, transcript, slide |
| B | Trợ lý Discord | Tin nhắn Discord, bản tin bot |
| C | Lesson Studio, đề C1–C5 | Transcript, slide, studio pack |
| D | Học tập thích ứng & tương tác | Chatlog, transcript, slide |
| E | Làn mở trong phạm vi AI20k | Tùy dữ liệu và người dùng |

Nên ưu tiên đề có dữ liệu và người dùng dễ tiếp cận. Với thời gian ngắn, **Track A1 hoặc B1 thường dễ chứng minh bằng evidence hơn**.

Chi tiết lựa chọn nằm trong `tracks/README.md`.

---

# 2. Tạo repository GitHub đúng quy định

Không fork và không push toàn bộ repository đề bài lên GitHub.

Tên repository phải đúng dạng:

```text
K4-3B-<phòng>-<tên nhóm>
```

Ví dụ:

```text
K4-3B-E403-ChamCongAI
K4-3B-E402-DiscordBuddy
```

Repository phải:

- Để chế độ **Public**.
- Có thể mở được bằng cửa sổ ẩn danh.
- Được tạo mới hoàn toàn.
- Không commit thư mục dữ liệu gốc `data/`.

Cấu trúc cuối cùng cần có:

```text
K4-3B-<phòng>-<tên nhóm>/
├── README.md
├── spec.md
├── demo-slides.pdf
├── codebase/
├── eval/
├── validation/
└── reflection/
```

Cần sao chép:

- `README.md`, sau đó điền bảng thành viên.
- `03-ai-spec-template.md`, đổi tên thành `spec.md`.
- Mẫu Canvas từ `examples/canvas-cp1.md`, tạo thành `canvas.md`.

---

# 3. Quy định dữ liệu và bảo mật

Dữ liệu trong `data/` chỉ được dùng để:

- Mining bằng chứng.
- Xây golden set.
- Làm context cho prototype.
- Kiểm thử tính năng.

Không được:

- Commit nguyên thư mục `data/` vào repository công khai.
- Đưa dữ liệu ra ngoài khóa học nếu không cần thiết.
- Cố suy ngược danh tính người dùng.
- Dán nguyên văn đoạn dữ liệu dài; chỉ trích ngắn và dẫn mã `turn_id`, `msg_id` hoặc mã transcript.

Quy mô dữ liệu:

- VLearn: khoảng **13.494 lượt hỏi–đáp**, trong đó **3.097 lượt của khóa 4**.
- Discord: **1.092 tin nhắn**, gồm tin người dùng và bot.
- Transcript: 6 transcript có mã đoạn để trích dẫn.
- Slide: 2 bộ slide bài giảng.
- Studio pack: dữ liệu phục vụ Track C.

Đọc thêm `data/README.md`.

---

# 4. CP1 — Canvas và bằng chứng bài toán

## Canvas 7 dòng

Tạo `canvas.md` với 7 dòng:

1. Track và đề cụ thể.
2. Job executor: ai, đang ở đâu, đang làm gì.
3. Pain một câu: ai đang làm gì, vướng gì, hậu quả gì.
4. Một hoặc hai bằng chứng ban đầu.
5. Lát cắt một câu.
6. AI tự làm đến đâu, lý do, danh sách willing users.
7. Phân công cụ thể theo tên.

Lát cắt phải đúng format:

> **Một người dùng · một công việc · một quyết định AI · một kết quả**

Ví dụ:

> Học viên đang đọc slide cần làm rõ một đoạn khó; AI quyết định chỉ trả lời khi tìm được nguồn phù hợp; kết quả là câu trả lời có trích dẫn đoạn nguồn hoặc thông báo chưa đủ căn cứ.

## Evidence đạt chuẩn

Có thể dùng một hoặc cả hai cách:

### Chuẩn A — khảo sát

- Ít nhất **20 người ngoài nhóm**.
- Ít nhất **50% xác nhận pain**.
- Ghi đầy đủ câu hỏi và từng câu trả lời nguyên văn.

### Chuẩn B — mining dữ liệu

- Có số đếm cụ thể.
- Có ít nhất **5 ví dụ nguyên văn**.
- Có phương pháp đếm để người khác kiểm tra lại được.
- Dẫn mã hội thoại/tin nhắn/transcript.

Ngoài ra phải có bảng impact ít nhất 3 ứng viên:

```text
Ứng viên | Số người gặp | Tần suất | Chi phí mỗi lần | Khả thi | Chọn/loại | Lý do
```

---

# 5. CP2 — Thiết kế luồng trải nghiệm

Cần tạo một trong các loại sau:

- Prototype click được trên Figma/Canva.
- Trang HTML/CSS/JS đơn giản.
- Sơ đồ flow.
- Video quay một vòng tương tác.

Flow cần thể hiện:

1. Người dùng nhập dữ liệu.
2. Hệ thống xử lý.
3. Điểm gọi AI.
4. Kết quả bình thường.
5. Kết quả low-confidence.
6. Không tìm thấy nguồn.
7. Ngoài phạm vi.
8. Người dùng sửa kết quả.

Trong `spec.md` phải mô tả bốn đường đi:

- **Happy path**: AI tự tin cao.
- **Low-confidence**: AI không chắc.
- **Failure/no-grounding**: không tìm thấy căn cứ.
- **Correction**: người dùng sửa kết quả.

Cần áp dụng ít nhất **4 nguyên tắc HAX/PAIR**, trong đó bắt buộc có:

- **G10 — Thu hẹp phạm vi khi nghi ngờ.**

Ngoài ra nên có ít nhất một trong:

- G8 — Gạt bỏ dễ dàng.
- G9 — Sửa dễ dàng.
- G11 — Giải thích vì sao.

Mỗi nguyên tắc phải chỉ rõ được nó nằm ở đâu trong prototype.

---

# 6. CP3 — Prototype AI thật và kiểm thử lần đầu

## Prototype

Trong thư mục `codebase/` cần có:

- Mã nguồn chạy được.
- Ít nhất một lời gọi mô hình AI thật tại quyết định trung tâm.
- Không hardcode toàn bộ câu trả lời.
- Có log/trace gồm:
  - Input hoặc prompt gửi vào model.
  - Phản hồi thô của model.
  - Kết quả sau xử lý nếu có.
- Ghi rõ phần nào là mock và phần nào chạy thật.

Prototype phải chạy end-to-end theo lát cắt đã khai báo.

## Golden set

Trong `eval/` tạo file `.json` hoặc `.csv` có ít nhất **20 case**:

- Tối thiểu 2 case cho mỗi lớp chỗ khó.
- Khoảng 8–10 case thông thường.
- Khoảng 2–4 case hiếm hoặc nguy hiểm.
- Ít nhất 10 case lấy từ chatlog/Discord thật.
- Tất cả case phải được phân loại theo 4 lớp:

1. Nguồn sự thật.
2. Mơ hồ hoặc thiếu thông tin.
3. Ngoài phạm vi hoặc thẩm quyền.
4. Đặc thù domain.

Sau đó cần chạy toàn bộ golden set và ghi:

- Tổng số case.
- Số case đạt.
- Số case thất bại.
- Tỷ lệ phần trăm.
- Nguyên nhân từng case thất bại.
- Bảng kết quả trong `eval/`.

Cần quay video khoảng **30 giây** cho thấy:

1. Người dùng nhập dữ liệu.
2. Hệ thống gửi request.
3. Model AI thật trả kết quả.

---

# 7. CP4 — Hoàn thiện `spec.md` và khóa quality bar

Đây là phần quan trọng nhất vì phần lớn điểm chấm dựa trên `spec.md`.

## Nội dung bắt buộc trong §1–§9

### §1–§2: User, pain, evidence và impact

- Job executor.
- Workflow hiện tại.
- Core JTBD không chứa chữ “AI”.
- Problem statement không chứa chữ “AI”.
- Evidence chuẩn A/B.
- Ít nhất 5 quote/ví dụ nguyên văn.
- Bảng impact ít nhất 3 ứng viên.
- Lý do chọn và loại từng ứng viên.

### §3–§4: Giải pháp và thiết kế

- Phân tích ít nhất 2 sản phẩm tương tự.
- Với mỗi sản phẩm:
  - Flow của họ.
  - Điều đáng học.
  - Điều đáng tránh.
  - Sản phẩm của nhóm khác gì.
- Lát cắt một câu.
- Ít nhất 3 non-goals.
- Mức prototype: Sketch, Mock hoặc Working.
- Automation: Augment, Conditional hoặc Automate.
- Lý do phải dựa trên **cost-of-error**, không chỉ “vì tiện”.
- Bảng ít nhất 4 nguyên tắc HAX/PAIR và vị trí áp dụng.

### §5–§6: Lỗi và các nhánh trải nghiệm

- Đủ 4 lớp chỗ khó.
- Ít nhất 8 kịch bản.
- Mỗi kịch bản có:
  - Tình huống.
  - Lớp lỗi.
  - Hành vi mong muốn.
  - Nguyên tắc áp dụng.
- Mô tả happy path, low-confidence, failure/no-grounding và correction.

### §7: Đo lường

- Các chiều chất lượng.
- Định nghĩa kiểm chứng được.
- Liên kết đến golden set trong `eval/`.
- Quality bar viết bằng số, ví dụ:

```text
Đạt khi ≥80% case có câu trả lời đúng và có citation truy vết được,
đồng thời 100% case ngoài phạm vi bị từ chối an toàn.
```

- Chốt quality bar trước khi biết kết quả chạy.
- Sau khi khóa không được hạ chuẩn.
- Ghi trung thực các chức năng/case chưa hoàn thiện.

### §8–§9: Phân công và thay đổi

- Phân công có tên cho:
  - Evidence.
  - Prompt.
  - Code.
  - Golden set.
  - Demo.
  - Validation.
- Danh sách ít nhất 2 willing users.
- Kế hoạch validation.
- Changelog các thay đổi.

---

# 8. CP5 — Validation, slide và video dự phòng

## Validation người dùng — bonus tối đa 8 điểm

Không bắt buộc nhưng giúp đạt tối đa 100 điểm thay vì 92.

Mời ít nhất 2 người ngoài nhóm dùng prototype. Trong `validation/` ghi:

- Tên/vai người thử.
- Có phải willing user đã khai báo từ CP1 không.
- Task được giao.
- Hành vi quan sát được.
- Quote nguyên văn.
- Mức độ nghiêm trọng.
- Thay đổi đã thực hiện sau feedback.

Nên thực hiện test theo quy trình:

1. Trấn an người thử rằng đang đánh giá sản phẩm, không đánh giá họ.
2. Hỏi một câu chuyện thật trước khi mở sản phẩm.
3. Giao task theo outcome, không chỉ bảo bấm nút nào.
4. Quan sát im lặng khoảng 5 phút.
5. Hỏi lại sau khi dùng.

Nếu người dùng bị kẹt, chỉ dùng các câu:

- “Cứ nói to suy nghĩ nhé.”
- “Bạn sẽ làm gì tiếp?”
- “Bạn nghĩ nó nên hoạt động thế nào?”

Không nên hướng dẫn màn hình hoặc hỏi “Bạn có thích không?”.

## Slide

Tạo đúng **6 trang**, xuất PDF tại thư mục gốc với tên chính xác:

```text
demo-slides.pdf
```

Nội dung:

1. **User & Job**: người dùng, JTBD, con số pain.
2. **Vì sao chọn tính năng**: bảng impact và ứng viên bị loại.
3. **Giải pháp & demo live**: một case chuẩn và một case khó.
4. **Kết quả đo**: tỷ lệ qua golden set so với quality bar.
5. **User thật nói gì**: ít nhất 2 quote và thay đổi đã làm.
6. **Nếu có thêm một tuần**: việc ưu tiên tiếp theo và bài học lớn nhất.

Mỗi slide cần có ít nhất một:

- Con số.
- Quote có nguồn.
- Kết quả đo.

## Video dự phòng

Quay video demo dự phòng giống phần sẽ trình bày trên sân khấu. Video CP5 khác video CP3:

- CP3: chứng minh AI thật chạy được.
- CP5: video backup để chiếu nếu live demo gặp sự cố mạng/API.

---

# 9. CP6 — Thuyết trình

Không nộp thêm artifact tại CP6.

Cần chuẩn bị:

- 5–7 phút trình bày tùy vòng.
- Demo trực tiếp.
- Một case bình thường.
- Một case lỗi/chỗ khó.
- Tỷ lệ kết quả so với quality bar.
- Mỗi thành viên nói ít nhất một phần.
- Sẵn sàng trả lời:
  - Vì sao chọn Augment, Conditional hoặc Automate?
  - Failure nguy hiểm nhất là gì?
  - Phần bạn phụ trách là gì?

Giám khảo có thể đưa một case lạ để chạy tại chỗ.

---

# 10. Hạn nộp theo lịch lớp 3B

Theo tài liệu:

| Mốc | Nội dung | Hạn |
|---|---|---|
| CP1 | Canvas + repo công khai | 19:30 ngày 17/9 |
| CP2 | Flow/prototype bấm được | 21:00 ngày 17/9 |
| CP3 | Video 30 giây + kết quả đo | 16:00 ngày 18/9 |
| CP4 | Chốt `spec.md` và quality bar | 21:00 ngày 18/9 |
| CP5 | PDF slide + video dự phòng | 22:30 ngày 18/9 |
| CP6 | Thuyết trình | 09:00 ngày 19/9 |

Theo thời điểm hiện tại **22:50 ngày 17/9**, hạn CP1 và CP2 đã qua. Nếu nhóm chưa nộp hai mốc này, nên báo ngay cho coach/trợ giảng để xác nhận phương án xử lý; đồng thời ưu tiên hoàn thành CP3, vì CP3 là nền tảng cho `codebase/`, `eval/` và `spec.md`.

---

# 11. Kế hoạch thực hiện đề xuất từ bây giờ

## Tối 17/9

- Chốt nhóm, đội trưởng, track và đề.
- Tạo repo Public đúng tên.
- Tạo `README.md`, `spec.md`, `canvas.md`.
- Chốt lát cắt một câu.
- Bắt đầu mining 30–50 mẫu dữ liệu.
- Tạo flow prototype tối thiểu.
- Khai báo ít nhất 2 willing users.

## Sáng 18/9

- Hoàn thiện evidence và bảng impact.
- Viết prototype trong `codebase/`.
- Tích hợp AI API thật.
- Ghi log prompt và response.
- Tạo golden set 20 case.
- Chạy lượt đo đầu tiên.
- Quay video CP3.

## Chiều/tối 18/9

- Hoàn thiện toàn bộ `spec.md` §1–§9.
- Khóa quality bar trước 21:00.
- Test ít nhất 2 người ngoài nhóm.
- Cập nhật `validation/` và changelog.
- Làm slide 6 trang.
- Quay video dự phòng.
- Kiểm tra cấu trúc repository và nộp CP5 trước 22:30.

## Trước khi đi thi

- Mỗi thành viên tạo một file trong `reflection/`.
- Kiểm tra repo mở được ở chế độ ẩn danh.
- Kiểm tra `demo-slides.pdf` có đúng 6 trang.
- Kiểm tra prototype không cần can thiệp thủ công.
- Chuẩn bị dữ liệu demo, case lỗi và phương án khi API/mạng hỏng.
- Tất cả thành viên tự nộp cùng một link repo trên VLearn.
- Đội trưởng nộp CP1–CP5 bằng cùng một mã học viên.