# CP2 — Sơ đồ flow Track A1

## Luồng chính

```mermaid
flowchart TD
    A[Hoc vien xem bai giang] --> B[Nhap cau hoi va bai dang hoc]
    B --> C{Cau hoi co thuoc noi dung bai hoc?}

    C -->|Khong| X[Thong bao gioi han ho tro]
    X --> X2[Huong dan kiem tra LMS hoac hoi TA]
    X2 --> Z([Ket thuc])

    C -->|Co the| D{Du ngu canh de hieu cau hoi?}
    D -->|Chua du| E[Hoi lai va yeu cau chon doan hoac khai niem]
    E --> F{Hoc vien bo sung thong tin?}
    F -->|Co| B
    F -->|Khong| Z

    D -->|Du| G[Tim nguon trong transcript hoac slide]
    G --> H{Co nguon phu hop?}

    H -->|Co| I[Tra loi dua tren nguon]
    I --> J[Hien thi citation ma doan hoac trang]
    J --> K{Hoc vien muon sua ket qua?}
    K -->|Co| B
    K -->|Khong| Z

    H -->|Khong| L[Khong suy doan]
    L --> M[Thong bao chua du can cu]
    M --> N[Ye u cau them ngu canh hoac hoi TA]
    N --> F
```

## Đọc sơ đồ theo 5 bước

1. Học viên đang xem bài giảng và nhập câu hỏi.
2. Hệ thống kiểm tra câu hỏi có thuộc phạm vi bài học không.
3. Hệ thống kiểm tra câu hỏi đã đủ ngữ cảnh chưa.
4. Nếu đủ ngữ cảnh, hệ thống tìm nguồn trong transcript/slide.
5. Có nguồn thì trả lời kèm citation; không có nguồn thì báo **Chưa đủ căn cứ**, không tự đoán.

## Các nhánh cần demo

| Nhánh | Input mẫu | Kết quả mong muốn |
|---|---|---|
| Happy path | `LLM là gì?` | Trả lời ngắn + citation, ví dụ `[D02, trang 5]` |
| Low-confidence | `Giải thích phần này` | Hỏi học viên chọn đoạn hoặc nêu khái niệm |
| Failure/no-grounding | `Dự báo thời tiết ngày mai thế nào?` | Báo chưa đủ căn cứ, không bịa câu trả lời |
| Ngoài phạm vi | `Deadline nộp bài là ngày nào?` | Hướng dẫn kiểm tra LMS hoặc hỏi TA |
| Correction | `Nó hoạt động thế nào?` rồi sửa thành `LLM tạo token tiếp theo thế nào?` | Nhận câu hỏi mới và chạy lại flow |

## Phân biệt CP2 và CP3

| Thành phần | CP2 | CP3 |
|---|---|---|
| Hình thức | Sơ đồ flow | Prototype chạy được |
| Retrieval | Mô tả/giả lập | Tích hợp tìm nguồn |
| AI model | Chưa bắt buộc | Gọi model thật |
| Citation | Minh họa | Sinh và kiểm tra từ nguồn |
| Log prompt/response | Chưa bắt buộc | Bắt buộc |

> Đây là sơ đồ CP2. Không cần chạy code ở CP2; chỉ cần trình bày rõ các bước và các nhánh xử lý.
