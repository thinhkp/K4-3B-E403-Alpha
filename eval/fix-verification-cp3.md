# CP3 - Xác minh sau khi sửa

Baseline được giữ nguyên trong `eval/golden-set-cp3.md`: **12/20 đạt**. Sau khi sửa, tám case từng rớt được chạy lại qua backend thật và chụp màn hình vào `eval/evidence-after/`.

Bộ bằng chứng ghép dùng để nộp nằm trong `eval/evidence-final/`: 12 ảnh đạt từ baseline và 8 ảnh chạy lại sau sửa, được chuẩn hóa về đúng tên ID (`G01.png` ... `S01.png`). Thư mục baseline và after vẫn được giữ riêng để có thể đối chiếu.

| ID | Kết quả retest | Bằng chứng hành vi |
|---|---|---|
| G01 | Đạt | Tóm tắt đúng agenda Day 1 và chỉ dẫn `[trang 2]`. Evidence: `eval/evidence-after/G01-after.png`. |
| G08 | **Rớt** | Nêu đủ 6 yếu tố cốt lõi nhưng lần chạy chụp ảnh vẫn bỏ sót 3 yếu tố quyết định AI; model chưa ổn định dù một lần API retest trước đó đã trả đủ. Evidence: `eval/evidence-after/G08-after.png`. |
| O03 | Đạt | `awaiting_web_consent`, bắt đầu bằng “Không có trong bài giảng.”, không citation. Evidence: `eval/evidence-after/O03-after.png`. |
| O04 | Đạt | `awaiting_web_consent`, không lấy nhầm slide có từ “code”, không citation. Evidence: `eval/evidence-after/O04-after.png`. |
| A02 | Đạt | `needs_clarification`, hỏi người học xác định khái niệm/đoạn, không citation. Evidence: `eval/evidence-after/A02-after.png`. |
| C01 | Đạt | Chào tự nhiên, `answered`, không citation. Evidence: `eval/evidence-after/C01-after.png`. |
| C02 | Đạt | Đáp lời cảm ơn tự nhiên, `answered`, không citation. Evidence: `eval/evidence-after/C02-after.png`. |
| S01 | Đạt | `needs_clarification`, báo nội dung không thuộc phạm vi Day 1 và hướng dẫn đổi phạm vi, không citation. Evidence: `eval/evidence-after/S01-after.png`. |

## Kết luận

- Retest bằng ảnh: **7/8 case từng rớt đã đạt**.
- Unit test: **10/10 đạt**.
- Ghép 12 case baseline đã đạt với 7 case được sửa và xác nhận bằng ảnh: **19/20 đạt**. Để gọi đây là số đo sau sửa hoàn toàn chính thức, vẫn nên chạy lại đủ 20 câu trong cùng một lượt.

## Các thay đổi chính

1. Conversation Gate nhận đúng lời chào và lời cảm ơn có hậu tố tự nhiên.
2. Context Gate bắt các đại từ mơ hồ như “cái này”, “nó”, “cái kia”.
3. Out-of-scope Gate chặn câu hỏi lịch sử và yêu cầu viết thuật toán độc lập trước retrieval.
4. Scope Gate phát hiện mâu thuẫn giữa Day được hỏi và phạm vi dropdown.
5. Prompt yêu cầu tóm tắt đúng agenda và bao phủ đủ mọi nhóm yếu tố/bước trong nguồn.
6. Learning note chỉ xuất hiện khi độ tương đồng insight đủ cao.
