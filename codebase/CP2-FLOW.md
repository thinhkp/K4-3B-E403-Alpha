# CP2 — Hành trình tương tác VLearn Grounded Tutor

Prototype chạy ở mức **Working**. Giao diện nằm trong `src/`, bản build trong `dist/`; backend phục vụ luôn giao diện tại `http://localhost:8000`.

```mermaid
flowchart TD
    A[Học viên chọn phạm vi bài học] --> B[Nhập câu hỏi hoặc đoạn bôi đen]
    B --> C{Input Guard}
    C -->|Prompt injection| C1[Safe refusal<br/>Không gọi retrieval hoặc web]
    C -->|Hợp lệ| D{Intent & Context Gate}

    D -->|Chào hỏi / cảm ơn| D1[Trả lời tự nhiên<br/>Không citation]
    D -->|Thiếu đối tượng / ngữ cảnh| D2[Hỏi đúng một câu làm rõ]
    D2 -->|Học viên bổ sung| B
    D -->|Ngoài bài giảng| H[Không có trong bài giảng]
    D -->|Mâu thuẫn Day với dropdown| D3[Yêu cầu đổi phạm vi]
    D3 --> A
    D -->|Câu hỏi học thuật| E[Retrieval Agent<br/>Embedding + Qdrant]

    E --> F{Evidence Gate}
    F -->|Không có nguồn trực tiếp| H
    F -->|Đủ căn cứ| G[OpenAI Tutor Response Agent]
    G --> I{Citation Verifier}
    I -->|Citation sai| I1[Repair đúng một lần]
    I1 -->|Vẫn sai| D2
    I -->|Citation hợp lệ| J[Hiện câu trả lời + citation + learning note phù hợp]
    I1 -->|Đã sửa đúng| J

    J --> K[Học viên bấm citation]
    K --> L[Panel trái mở đúng PDF và trang slide]
    L --> M[Đổi trang / hỏi lại / rating Có-Chưa]
    M -->|Sửa hoặc hỏi tiếp| B

    H --> N{Học viên đồng ý tìm web?}
    N -->|Không| O[Quay lại bài học]
    O --> A
    N -->|Có| P[Tavily Web Search]
    P -->|Thành công| Q[Hiện nguồn ngoài bài giảng và URL]
    P -->|Lỗi sau retry| R[Báo chưa thể tìm web<br/>Không bịa nguồn]
```

## Điểm có thể kiểm trực tiếp trên prototype

- Happy path: hỏi “LLM khác chatbot như thế nào?”, mở citation `[trang 10]`.
- Low-confidence: hỏi “Cái này hoạt động thế nào?”, agent phải hỏi lại và không có citation.
- Failure/no-grounding: hỏi thời tiết, agent phải xin consent trước khi tìm web.
- Correction: đổi dropdown Day 1/Day 2, bổ sung câu hỏi hoặc bấm rating ngay trong cuộc hội thoại.
- Safety: yêu cầu xem system prompt phải trả `safe_refusal` và không gọi tool.
