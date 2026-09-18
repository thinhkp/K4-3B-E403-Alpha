"""Build Qdrant collections and aggregate K4 chatlog insights.

Run from codebase/ after docker compose up -d and configuring ../.env:
    uv run python scripts/ingest.py
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import Counter
from datetime import timedelta
from pathlib import Path
from typing import Any

CODEBASE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODEBASE_ROOT.parent if CODEBASE_ROOT.name == "codebase" else CODEBASE_ROOT
if str(CODEBASE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODEBASE_ROOT))
import pandas as pd
import pymupdf

from app.main import CHAT_COLLECTION, DOC_COLLECTION, DOCUMENT_METADATA, INSIGHT_COLLECTION, Embedder, MongoStore, VectorStore

PACK = PROJECT_ROOT / "data" / "vlearn-pack"


def point_id(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def semantic_chunks(text: str, maximum: int = 950, overlap: int = 140) -> list[str]:
    """Sentence-first chunks that preserve source line and bullet boundaries."""
    units: list[str] = []
    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()
        if not line:
            continue
        units.extend(part.strip() for part in re.split(r"(?<=[.!?])\s+", line) if part.strip())

    chunks: list[str] = []
    current: list[str] = []
    for unit in units:
        candidate = "\n".join([*current, unit])
        if current and len(candidate) > maximum:
            chunks.append("\n".join(current))
            overlap_units: list[str] = []
            overlap_size = 0
            for previous in reversed(current):
                if overlap_units and overlap_size + len(previous) + 1 > overlap:
                    break
                overlap_units.insert(0, previous)
                overlap_size += len(previous) + 1
            current = [*overlap_units, unit]
        else:
            current.append(unit)
    if current:
        chunks.append("\n".join(current))
    return chunks


def strip_decorative_icons(text: str) -> str:
    """Remove emoji/icon glyphs that convey slide decoration, not language."""
    def keep(character: str) -> bool:
        codepoint = ord(character)
        return not (
            0x1F000 <= codepoint <= 0x1FAFF
            or 0x2600 <= codepoint <= 0x27BF
            or 0x27F0 <= codepoint <= 0x27FF
            or 0x2B00 <= codepoint <= 0x2BFF
            or codepoint in {0x200D, 0xFE0E, 0xFE0F}
        )

    return "".join(character for character in text if keep(character))


def clean_pdf_line(text: str) -> str:
    """Normalize harmless PDF whitespace without guessing missing content."""
    text = strip_decorative_icons(text)
    text = text.replace("\u00ad", "").replace("\u00a0", " ").replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return text


def extract_pdf_pages(pdf: Path) -> list[str]:
    """Extract horizontal text in visual reading order, excluding rotated watermarks."""
    pages: list[str] = []
    with pymupdf.open(pdf) as document:
        for page in document:
            blocks: list[dict[str, Any]] = []
            content = page.get_text("dict", sort=False)
            for block in content.get("blocks", []):
                if block.get("type") != 0:
                    continue
                block_lines: list[str] = []
                for line in block.get("lines", []):
                    direction_x, direction_y = line.get("dir", (1.0, 0.0))
                    # The slide watermark is diagonal. Keep only normal
                    # horizontal reading lines so its letters never enter RAG.
                    if direction_x < 0.98 or abs(direction_y) > 0.02:
                        continue
                    text = clean_pdf_line(" ".join(span.get("text", "") for span in line.get("spans", [])))
                    if text:
                        block_lines.append(text)
                if block_lines:
                    x0, y0, x1, y1 = block["bbox"]
                    text = clean_pdf_line(" ".join(block_lines))
                    if text:
                        blocks.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "text": text})

            # Read one visual column at a time. This prevents labels/icons on
            # the right side from being inserted into a paragraph on the left.
            page_width = max(float(page.rect.width), 1.0)
            for block in blocks:
                block["column"] = min(2, int((block["x0"] / page_width) * 3))
            blocks.sort(key=lambda item: (item["column"], item["y0"], item["x0"]))

            paragraphs: list[dict[str, Any]] = []
            for block in blocks:
                previous = paragraphs[-1] if paragraphs else None
                vertical_gap = block["y0"] - previous["y1"] if previous else 999.0
                same_text_column = previous and previous["column"] == block["column"] and abs(previous["x0"] - block["x0"]) <= 24
                starts_new_bullet = bool(re.match(r"^(?:[•●▪◦]|\d{1,2}[.)])\s*", block["text"]))
                if same_text_column and -2 <= vertical_gap <= 9 and not starts_new_bullet:
                    previous["text"] = f"{previous['text']} {block['text']}"
                    previous["y1"] = max(previous["y1"], block["y1"])
                    previous["x1"] = max(previous["x1"], block["x1"])
                else:
                    paragraphs.append(dict(block))
            # Preserve one entry per physical PDF page so citations stay exact.
            pages.append("\n".join(item["text"] for item in paragraphs).strip())
    return pages


def ingest_documents(vectors: VectorStore) -> int:
    chunks: list[dict[str, Any]] = []
    for pdf in sorted((PACK / "slides").glob("*.pdf")):
        doc_id = pdf.stem
        for page_no, page_text in enumerate(extract_pdf_pages(pdf), start=1):
            if not page_text:
                continue
            for index, text in enumerate(semantic_chunks(page_text), start=1):
                source_id = f"{doc_id}:p{page_no}:c{index}"
                chunks.append({
                    "point_id": point_id(source_id), "source_id": source_id, "doc_id": doc_id,
                    "content_type": "slide", "lecture_code": "D01" if "d1" in doc_id else "D02",
                    "lecture_title": "AI & LLM Foundation" if "d1" in doc_id else "Xác định bài toán cho AI",
                    "document_title": pdf.stem, "page": page_no, "segment_id": None,
                    "chunk_index": index, "citation_label": f"[trang {page_no}]", "source_path": str(pdf.relative_to(PROJECT_ROOT)), "text": text,
                    "extraction_method": "pymupdf-layout-v3",
                })
    for transcript in sorted((PACK / "transcript").glob("*.md")):
        if transcript.stem not in DOCUMENT_METADATA:
            continue
        raw = transcript.read_text(encoding="utf-8")
        lecture_code, lecture_title = DOCUMENT_METADATA[transcript.stem]
        segments = re.split(r"(?=\[T\d{2}-\d{3}\])", raw)
        for block in segments:
            match = re.match(r"\[(T\d{2}-\d{3})\]\s*(.*)", block, re.S)
            if not match:
                continue
            segment_id, content = match.groups()
            for index, text in enumerate(semantic_chunks(content), start=1):
                source_id = f"{segment_id}:c{index}"
                chunks.append({
                    "point_id": point_id(source_id), "source_id": source_id, "doc_id": transcript.stem,
                    "content_type": "transcript", "lecture_code": lecture_code,
                    "lecture_title": lecture_title, "document_title": transcript.stem, "page": None,
                    "segment_id": segment_id, "chunk_index": index, "citation_label": f"[đoạn {segment_id}]",
                    "source_path": str(transcript.relative_to(PROJECT_ROOT)), "text": text,
                })
    vectors.upsert(DOC_COLLECTION, chunks)
    return len(chunks)


TOPICS = {
    "ai-ml-llm": (r"\b(?:ai|machine learning|ml|llm|ngôn ngữ lớn)\b", "Phân biệt AI, ML và LLM", "Nhiều học viên hay nhầm AI, ML và LLM. Hãy phân biệt chúng theo phạm vi và ví dụ."),
    "prompt-context": (r"\b(?:prompt|context|ngữ cảnh|token)\b", "Prompt và context", "Khi đặt prompt, hãy nêu rõ mục tiêu, dữ liệu đầu vào và kết quả bạn muốn nhận."),
    "agent-tool": (r"\b(?:agent|tool|công cụ|function calling)\b", "AI Agent và tool calling", "Hãy tách rõ phần model suy luận với công cụ thực thi khi học về agent."),
    "evaluation": (r"\b(?:eval|đánh giá|golden set|metric|đo lường)\b", "Đánh giá sản phẩm AI", "Đừng chỉ nhìn câu trả lời hay; hãy kiểm tra bằng golden set và tiêu chí đạt rõ ràng."),
    "implementation": (r"\b(?:code|lỗi|error|python|api|docker)\b", "Triển khai kỹ thuật", "Khi gặp lỗi triển khai, hãy ghi lại input, output và bước tái hiện trước khi sửa."),
}


def sessionize(df: pd.DataFrame) -> list[dict[str, Any]]:
    df = df.copy()
    df["asked_at"] = pd.to_datetime(df["asked_at_vn"], errors="coerce")
    df = df.sort_values(["student", "asked_at"])
    rows: list[dict[str, Any]] = []
    for student, group in df.groupby("student", dropna=False):
        session_no, previous, turns = 0, None, []
        for row in group.to_dict("records"):
            asked = row.get("asked_at")
            if previous is None or pd.isna(asked) or pd.isna(previous) or asked - previous > timedelta(minutes=30):
                if turns:
                    rows.append({"student": student, "session_no": session_no, "turns": turns})
                session_no += 1
                turns = []
            turns.append(row)
            previous = asked
        if turns:
            rows.append({"student": student, "session_no": session_no, "turns": turns})
    return rows


def ingest_chatlog(vectors: VectorStore, mongo: MongoStore) -> tuple[int, int]:
    data = pd.read_csv(PACK / "chatlog" / "tutor_turns.csv")
    data = data[(data["cohort_hint"] == "K4") & (~data["is_preset"].astype(bool))].copy()
    sessions = sessionize(data)
    session_chunks: list[dict[str, Any]] = []
    for session in sessions:
        turns = session["turns"]
        body = "\n".join(f"Học viên: {turn['student_question']}\nTutor: {turn['tutor_reply']}" for turn in turns)
        session_id = f"{session['student']}-{session['session_no']}"
        for index, text in enumerate(semantic_chunks(body), start=1):
            source_id = f"chat:{session_id}:c{index}"
            first = turns[0]
            session_chunks.append({"point_id": point_id(source_id), "source_id": source_id, "collection": CHAT_COLLECTION,
                "user_id": str(session["student"]), "session_id": session_id, "cohort_hint": "K4", "lecture_code": first.get("lecture_code"),
                "course_id": first.get("course_id"), "turn_ids": [item.get("turn_id") for item in turns], "content_type": "private_chat_session", "text": text})
    vectors.upsert(CHAT_COLLECTION, session_chunks)

    issues: list[dict[str, Any]] = []
    for (course_id, lecture_code), group in data.groupby(["course_id", "lecture_code"], dropna=False):
        lecture_title = group["lecture_title"].dropna().mode().iloc[0] if not group["lecture_title"].dropna().empty else lecture_code
        total = len(group)
        corpus = group["student_question"].fillna("").str.lower()
        for issue_id, (pattern, title, note) in TOPICS.items():
            mask = corpus.str.contains(pattern, regex=True)
            count = int(mask.sum())
            if count < 3:
                continue
            source_id = f"insight:{course_id}:{lecture_code}:{issue_id}"
            issues.append({"point_id": point_id(source_id), "source_id": source_id, "course_id": course_id, "lecture_code": lecture_code,
                "lecture_title": lecture_title, "issue_id": issue_id, "title": title, "student_note": note,
                "question_count": count, "question_rate": round(count / total, 4), "content_type": "aggregate_insight",
                "text": f"{title}. {note}"})
    vectors.upsert(INSIGHT_COLLECTION, issues)
    mongo.db.issue_stats.delete_many({})
    if issues:
        mongo.db.issue_stats.insert_many([{key: value for key, value in issue.items() if key not in {"point_id", "text"}} for issue in issues])
    return len(session_chunks), len(issues)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index VLearn documents and chat insights.")
    parser.add_argument(
        "--documents-only",
        action="store_true",
        help="Rebuild only slide/transcript chunks; keep chat sessions and insights unchanged.",
    )
    args = parser.parse_args()
    vectors, mongo = VectorStore(Embedder()), MongoStore()
    if not vectors.ping() or not mongo.ping():
        raise SystemExit("Hãy chạy: docker compose up -d")
    if args.documents_only:
        vectors.reset(DOC_COLLECTION)
        document_count = ingest_documents(vectors)
        print(f"Indexed {document_count} clean document chunks; chat sessions and insights were not rebuilt.")
    else:
        for collection in (DOC_COLLECTION, CHAT_COLLECTION, INSIGHT_COLLECTION):
            vectors.reset(collection)
        document_count = ingest_documents(vectors)
        session_count, issue_count = ingest_chatlog(vectors, mongo)
        print(f"Indexed {document_count} document chunks, {session_count} private chat session chunks, {issue_count} aggregate insights.")
