from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel, Field
from pymongo import MongoClient, ReturnDocument
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from app.prompts import REPAIR_PROMPT, SYSTEM_PROMPT

LOGGER = logging.getLogger("vlearn.tutor")

CODEBASE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODEBASE_ROOT.parent if CODEBASE_ROOT.name == "codebase" else CODEBASE_ROOT
load_dotenv(PROJECT_ROOT / ".env")

DIMENSION = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))
# Slides are the teaching material a learner sees.  Transcript is valuable
# supporting material, but must not displace a sufficiently relevant slide.
SLIDE_PREFERRED_MIN_SCORE = 0.28
DOC_COLLECTION = "document_chunks"
CHAT_COLLECTION = "chat_session_chunks"
INSIGHT_COLLECTION = "issue_insights"
PEDAGOGICAL_MOVES = [
    "review_concept",
    "extend_concept",
    "check_understanding",
    "connect_prior_knowledge",
    "correct_misconception",
]

DOCUMENT_METADATA: dict[str, tuple[str, str]] = {
    "d1-slide-hackathon": ("D01", "AI & LLM Foundation"),
    "d2-slide-hackathon": ("D02", "Xác định bài toán cho AI"),
    "transcript-01-clean": ("D02", "Day 2 · Xác định bài toán kinh doanh cho AI"),
    "transcript-02-clean": ("D02", "Day 2 · Chỉ số thành công & mức tự động hoá"),
    "transcript-03-clean": ("D02", "Day 2 · Soi bài toán, tự động hoá & ràng buộc"),
    "transcript-04-clean": ("D01", "Day 1 · Foundation: cách LLM hoạt động"),
    "transcript-05-clean": ("SUPPLEMENTAL", "Bài toán · đánh giá · dữ liệu"),
    "transcript-06-clean": ("D01", "Foundation · Transformer & attention"),
}

DOCUMENT_SCOPES: dict[str, list[str]] = {
    "d1-slide-hackathon": ["d1-slide-hackathon", "transcript-04-clean", "transcript-06-clean"],
    "d2-slide-hackathon": ["d2-slide-hackathon", "transcript-01-clean", "transcript-02-clean", "transcript-03-clean"],
}


class DocumentContext(BaseModel):
    doc_id: str | None = None
    page: int | None = Field(default=None, ge=1)


class ChatRequest(BaseModel):
    session_id: str | None = None
    user_id: str = "demo-student"
    question: str = Field(min_length=1, max_length=4000)
    selected_text: str | None = Field(default=None, max_length=6000)
    document_context: DocumentContext = Field(default_factory=DocumentContext)


class Citation(BaseModel):
    source_id: str
    label: str
    doc_id: str | None = None
    content_type: str | None = None
    lecture_title: str | None = None
    page: int | None = None
    segment_id: str | None = None
    excerpt: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    state: Literal["answered", "needs_clarification", "awaiting_web_consent", "safe_refusal"]
    answer: str
    citations: list[Citation] = []
    pedagogical_move: str
    learning_note: str | None = None
    web_search_available: bool = False
    trace: list[str] = []


class FeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    rating: Literal["up", "down"]
    reason: str | None = Field(default=None, max_length=500)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MongoStore:
    def __init__(self) -> None:
        self.client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"), serverSelectionTimeoutMS=1500)
        self.db = self.client[os.getenv("MONGO_DB", "vlearn")]

    def ping(self) -> bool:
        try:
            self.client.admin.command("ping")
            return True
        except Exception:
            return False

    def recent_messages(self, session_id: str) -> list[dict[str, Any]]:
        return list(self.db.messages.find({"session_id": session_id}, {"_id": 0}).sort("created_at", -1).limit(6))[::-1]

    def save_message(self, session_id: str, user_id: str, role: str, text: str, metadata: dict[str, Any] | None = None) -> str:
        message_id = str(uuid.uuid4())
        self.db.messages.insert_one({
            "message_id": message_id, "session_id": session_id, "user_id": user_id,
            "role": role, "text": text, "metadata": metadata or {}, "created_at": utc_now(),
        })
        self.db.sessions.update_one({"session_id": session_id}, {"$set": {"user_id": user_id, "updated_at": utc_now()}, "$setOnInsert": {"created_at": utc_now()}}, upsert=True)
        return message_id

    def set_pending_web(self, session_id: str, question: str, user_id: str) -> None:
        self.db.sessions.update_one({"session_id": session_id}, {"$set": {"pending_web_question": question, "user_id": user_id, "updated_at": utc_now()}}, upsert=True)

    def consume_pending_web(self, session_id: str) -> dict[str, Any] | None:
        row = self.db.sessions.find_one_and_update({"session_id": session_id, "pending_web_question": {"$exists": True}}, {"$unset": {"pending_web_question": ""}, "$set": {"updated_at": utc_now()}}, return_document=ReturnDocument.BEFORE)
        return row


class Embedder:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAI embeddings. Add it to .env before running ingestion.")
        self.client = OpenAI(api_key=self.api_key)

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self.client.embeddings.create(model=self.model, input=texts, dimensions=DIMENSION)
        return [item.embedding for item in sorted(response.data, key=lambda item: item.index)]


class VectorStore:
    def __init__(self, embedder: Embedder) -> None:
        self.client = QdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"), timeout=3)
        self.embedder = embedder

    def ping(self) -> bool:
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False

    def ensure(self, collection: str) -> None:
        if not self.client.collection_exists(collection):
            self.client.create_collection(collection_name=collection, vectors_config=VectorParams(size=DIMENSION, distance=Distance.COSINE))

    def reset(self, collection: str) -> None:
        """Rebuild only generated index collections, never source data."""
        if self.client.collection_exists(collection):
            self.client.delete_collection(collection)
        self.client.create_collection(collection_name=collection, vectors_config=VectorParams(size=DIMENSION, distance=Distance.COSINE))

    def upsert(self, collection: str, chunks: list[dict[str, Any]]) -> None:
        self.ensure(collection)
        # Batch both OpenAI embedding calls and Qdrant writes. This keeps request
        # bodies bounded while avoiding one network call per chunk.
        for start in range(0, len(chunks), 128):
            batch = chunks[start:start + 128]
            embeddings = self.embedder.embed_many([chunk["text"] for chunk in batch])
            points = [
                PointStruct(id=chunk["point_id"], vector=vector, payload=chunk)
                for chunk, vector in zip(batch, embeddings, strict=True)
            ]
            self.client.upsert(collection_name=collection, points=points, wait=True)

    def search_documents(self, question: str, doc_id: str | None, limit: int = 5) -> list[dict[str, Any]]:
        from qdrant_client.http.models import Filter, FieldCondition, MatchAny, MatchValue
        scope_condition = None
        if doc_id:
            scoped_documents = DOCUMENT_SCOPES.get(doc_id)
            doc_match = MatchAny(any=scoped_documents) if scoped_documents else MatchValue(value=doc_id)
            scope_condition = FieldCondition(key="doc_id", match=doc_match)

        query_vector = self.embedder.embed(question)

        # First look at slide chunks. This makes a broad question such as
        # “nội dung Day 1 là gì?” open the relevant teaching slide instead of
        # an incidental transcript introduction. Transcript remains a fallback
        # when the slides genuinely do not cover the question.
        slide_conditions = [FieldCondition(key="content_type", match=MatchValue(value="slide"))]
        if scope_condition:
            slide_conditions.insert(0, scope_condition)
        slide_results = self.client.query_points(
            collection_name=DOC_COLLECTION,
            query=query_vector,
            query_filter=Filter(must=slide_conditions),
            limit=limit,
            with_payload=True,
        ).points

        if slide_results and float(slide_results[0].score) >= SLIDE_PREFERRED_MIN_SCORE:
            results = slide_results
        else:
            query_filter = Filter(must=[scope_condition]) if scope_condition else None
            results = self.client.query_points(
                collection_name=DOC_COLLECTION,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            ).points
        normalized: list[dict[str, Any]] = []
        for point in results:
            payload = dict(point.payload or {})
            metadata = DOCUMENT_METADATA.get(payload.get("doc_id"))
            if metadata:
                payload["lecture_code"], payload["lecture_title"] = metadata
            normalized.append({**payload, "score": float(point.score)})
        return normalized

    def search_insights(self, question: str, lecture_code: str | None) -> list[dict[str, Any]]:
        from qdrant_client.http.models import Filter, FieldCondition, MatchValue
        query_filter = Filter(must=[FieldCondition(key="lecture_code", match=MatchValue(value=lecture_code))]) if lecture_code else None
        try:
            results = self.client.query_points(collection_name=INSIGHT_COLLECTION, query=self.embedder.embed(question), query_filter=query_filter, limit=1, with_payload=True).points
            return [{**dict(point.payload or {}), "score": float(point.score)} for point in results]
        except Exception:
            return []

    def get_document_source(self, source_id: str) -> dict[str, Any] | None:
        from qdrant_client.http.models import Filter, FieldCondition, MatchValue
        records, _ = self.client.scroll(
            collection_name=DOC_COLLECTION,
            scroll_filter=Filter(must=[FieldCondition(key="source_id", match=MatchValue(value=source_id))]),
            limit=1,
            with_payload=True,
            with_vectors=False,
        )
        return dict(records[0].payload or {}) if records else None


class SafetyAgent:
    """Treat all user and retrieved content as data, never as executable instructions."""
    pattern = re.compile(r"bỏ qua.*hướng dẫn|ignore previous|system[_ ]override|system prompt|reveal.*prompt", re.I | re.S)

    def inspect(self, question: str, selected_text: str) -> bool:
        return bool(self.pattern.search(question) or self.pattern.search(selected_text))


class IntentContextAgent:
    # Keep small-talk out of retrieval.  Optional polite suffixes are common in
    # Vietnamese, so matching only the bare words "chào"/"cảm ơn" is too narrow.
    greeting_pattern = re.compile(
        r"^\s*(?:(?:xin\s+)?chào(?:\s+(?:bạn|thầy|cô|tutor|mọi\s+người))?"
        r"|hello(?:\s+(?:bạn|tutor))?|hi(?:\s+(?:bạn|tutor))?"
        r"|cảm\s+ơn(?:\s+(?:bạn|nhé|nha|nhiều|tutor))?"
        r"|thanks(?:\s+(?:you|tutor))?)\s*[!.?]*\s*$",
        re.I,
    )
    gratitude_pattern = re.compile(r"^\s*(?:cảm\s+ơn|thanks)(?:\s+(?:bạn|nhé|nha|nhiều|you|tutor))?\s*[!.?]*\s*$", re.I)
    out_of_scope_pattern = re.compile(
        r"\b(bitcoin|crypto|chứng khoán|cổ phiếu|thời tiết|bóng đá|tỷ giá|mua coin|điện biên phủ)\b"
        r"|(?:kể\s+lại|diễn\s+biến|lịch\s+sử).{0,60}(?:trận|chiến\s+tranh)"
        r"|(?:viết|cài\s+đặt|implement).{0,80}(?:hàm\s+(?:python|java|javascript)|thuật\s+toán|quicksort|mergesort)",
        re.I | re.S,
    )
    broad_lookup_pattern = re.compile(r"\b(tìm (?:nội dung|thông tin)|tổng quan|cho (?:mình )?biết về|nội dung về)\b", re.I)

    def classify(self, question: str, selected_text: str) -> Literal["greeting", "ambiguous", "out_of_scope", "academic"]:
        if self.greeting_pattern.match(question):
            return "greeting"
        if self.out_of_scope_pattern.search(question):
            return "out_of_scope"
        generic_reference = re.search(
            r"^(?:(?:hãy|giúp mình|bạn)?\s*giải thích\s*)?(?:cái|phần|đoạn|nội dung)?\s*(?:này|đó|kia)\s*[?.! ]*$",
            question,
            re.I,
        )
        vague_deictic = not selected_text and re.search(
            r"\b(?:cái|phần|đoạn|nội dung)\s+(?:này|đó|kia)\b|^\s*nó\b",
            question,
            re.I,
        )
        if len(question.strip()) < 3 or generic_reference or vague_deictic or (selected_text and len(selected_text) < 12 and re.search(r"đoạn|giải thích|này", question, re.I)):
            return "ambiguous"
        return "academic"


class RetrievalAgent:
    def __init__(self, vectors: VectorStore) -> None:
        self.vectors = vectors

    @staticmethod
    def explicit_scope(question: str) -> str | None:
        normalized = question.casefold()
        if re.search(r"\bday\s*2\b|\bngày\s*2\b|\bd\s*0?2\b", normalized):
            return "d2-slide-hackathon"
        if re.search(r"\bday\s*1\b|\bngày\s*1\b|\bd\s*0?1\b", normalized):
            return "d1-slide-hackathon"
        return None

    @classmethod
    def resolve_scope(cls, question: str, selected_scope: str | None) -> str | None:
        """Respect an explicit dropdown choice; infer Day 1/2 only for all-data search."""
        return selected_scope or cls.explicit_scope(question)

    @classmethod
    def has_scope_conflict(cls, question: str, selected_scope: str | None) -> bool:
        requested_scope = cls.explicit_scope(question)
        return bool(selected_scope and requested_scope and requested_scope != selected_scope)

    def retrieve(self, query: str, doc_id: str | None) -> list[dict[str, Any]]:
        return self.vectors.search_documents(query, doc_id)


class EvidenceAgent:
    minimum_score = 0.28
    maximum_score_gap = 0.10

    def select(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not candidates:
            return []
        top_score = max(candidate.get("score", 0) for candidate in candidates)
        if top_score < self.minimum_score:
            return []
        cutoff = max(self.minimum_score, top_score - self.maximum_score_gap)
        return [candidate for candidate in candidates if candidate.get("score", 0) >= cutoff]


class CitationAgent:
    def validate(self, citation_ids: list[str], sources: list[dict[str, Any]]) -> list[str]:
        allowed = {source["source_id"] for source in sources}
        return [citation_id for citation_id in citation_ids if citation_id in allowed]


class InsightAgent:
    def __init__(self, vectors: VectorStore) -> None:
        self.vectors = vectors

    def student_note(self, question: str, lecture_code: str | None) -> str | None:
        insights = self.vectors.search_insights(question, lecture_code)
        # A weak semantic neighbour is distracting rather than helpful.  Keep
        # notes only for a genuinely close issue match.
        return insights[0].get("student_note") if insights and insights[0].get("score", 0) >= 0.45 else None


class TutorAgent:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def answer(self, question: str, history: list[dict[str, Any]], sources: list[dict[str, Any]], scope: str | None) -> dict[str, Any]:
        allowed = [source["source_id"] for source in sources]
        source_text = "\n\n".join(f"SOURCE {s['source_id']} ({s['citation_label']}):\n{s['text'][:1800]}" for s in sources)
        schema = {
            "type": "object", "additionalProperties": False,
            "properties": {
                "answer": {"type": "string"}, "citations": {"type": "array", "items": {"type": "string"}},
                "pedagogical_move": {"type": "string", "enum": PEDAGOGICAL_MOVES},
                "needs_clarification": {"type": "boolean"}, "follow_up_question": {"type": ["string", "null"]},
            }, "required": ["answer", "citations", "pedagogical_move", "needs_clarification", "follow_up_question"],
        }
        if self.client:
            for attempt in range(2):
                try:
                    response = self.client.responses.create(
                        model=self.model, store=False, instructions=SYSTEM_PROMPT,
                        input=(
                            f"COURSE_SCOPE: {scope or 'Toàn bộ dữ liệu bài học'}\n\n"
                            f"QUESTION:\n{question}\n\n"
                            f"HISTORY:\n{json.dumps(history[-6:], ensure_ascii=False)}\n\n"
                            f"ALLOWED_SOURCE_IDS: {json.dumps(allowed)}\n\nSOURCES:\n{source_text}"
                        ),
                        text={"format": {"type": "json_schema", "name": "grounded_tutor_response", "strict": True, "schema": schema}},
                        max_output_tokens=700,
                    )
                    return json.loads(response.output_text)
                except Exception as error:
                    LOGGER.warning("OpenAI answer attempt %s failed (%s)", attempt + 1, type(error).__name__)
                    if attempt == 0:
                        time.sleep(0.4)

        # Never expose a raw retrieved chunk as if it were a tutor answer.
        # The orchestrator will make one bounded repair attempt and otherwise
        # return its safe clarification fallback.
        return {
            "answer": "Mình chưa thể diễn giải nguồn thành câu trả lời rõ ràng lúc này.",
            "citations": [],
            "pedagogical_move": "check_understanding",
            "needs_clarification": True,
            "follow_up_question": "Bạn có thể thử gửi lại câu hỏi sau một chút không?",
        }

    def repair_citations(self, result: dict[str, Any], sources: list[dict[str, Any]]) -> dict[str, Any]:
        """One bounded repair attempt; never invent a source when repair fails."""
        if not self.client:
            return result
        schema = {
            "type": "object", "additionalProperties": False,
            "properties": {
                "answer": {"type": "string"}, "citations": {"type": "array", "items": {"type": "string"}},
                "pedagogical_move": {"type": "string", "enum": PEDAGOGICAL_MOVES},
                "needs_clarification": {"type": "boolean"}, "follow_up_question": {"type": ["string", "null"]},
            }, "required": ["answer", "citations", "pedagogical_move", "needs_clarification", "follow_up_question"],
        }
        source_text = "\n\n".join(f"SOURCE {source['source_id']}:\n{source['text'][:1500]}" for source in sources)
        try:
            response = self.client.responses.create(
                model=self.model, store=False, instructions=SYSTEM_PROMPT + "\n\n" + REPAIR_PROMPT,
                input=f"ALLOWED_SOURCE_IDS: {json.dumps([s['source_id'] for s in sources])}\n\nINVALID_RESPONSE: {json.dumps(result, ensure_ascii=False)}\n\nSOURCES:\n{source_text}",
                text={"format": {"type": "json_schema", "name": "repaired_grounded_response", "strict": True, "schema": schema}}, max_output_tokens=700,
            )
            return json.loads(response.output_text)
        except Exception:
            return result


class Orchestrator:
    injection_pattern = SafetyAgent.pattern
    greeting_pattern = IntentContextAgent.greeting_pattern

    def __init__(self, mongo: MongoStore, vectors: VectorStore, tutor: TutorAgent) -> None:
        self.mongo, self.vectors, self.tutor = mongo, vectors, tutor
        self.safety = SafetyAgent()
        self.intent = IntentContextAgent()
        self.retrieval = RetrievalAgent(vectors)
        self.evidence = EvidenceAgent()
        self.citations = CitationAgent()
        self.insights = InsightAgent(vectors)

    def run(self, request: ChatRequest) -> ChatResponse:
        session_id = request.session_id or str(uuid.uuid4())
        question = request.question.strip()
        selected = (request.selected_text or "").strip()
        trace = ["Input Guard"]
        if self.safety.inspect(question, selected):
            message_id = self.mongo.save_message(session_id, request.user_id, "user", question)
            answer = "Mình không làm theo chỉ dẫn trong câu hỏi hoặc đoạn tài liệu. Bạn có thể hỏi nội dung kiến thức của bài đang mở."
            self.mongo.save_message(session_id, request.user_id, "assistant", answer, {"state": "safe_refusal"})
            return ChatResponse(session_id=session_id, message_id=message_id, state="safe_refusal", answer=answer, pedagogical_move="correct_misconception", trace=trace + ["Prompt injection blocked"])
        intent = self.intent.classify(question, selected)
        if intent == "greeting":
            message_id = self.mongo.save_message(session_id, request.user_id, "user", question)
            if self.intent.gratitude_pattern.match(question):
                answer = "Không có gì nhé! Khi cần, bạn cứ chọn đoạn slide hoặc nêu phần đang vướng để mình hỗ trợ."
            else:
                answer = "Chào bạn! Bạn đang vướng phần nào trong bài học? Bạn có thể chọn một đoạn slide rồi hỏi mình."
            self.mongo.save_message(session_id, request.user_id, "assistant", answer, {"state": "answered"})
            return ChatResponse(session_id=session_id, message_id=message_id, state="answered", answer=answer, pedagogical_move="check_understanding", trace=trace + ["Conversation Agent"])
        if intent == "ambiguous":
            message_id = self.mongo.save_message(session_id, request.user_id, "user", question)
            answer = "Bạn đang hỏi về khái niệm nào? Hãy bôi thêm 1–2 câu quanh đoạn đó hoặc cho mình biết tên slide."
            self.mongo.save_message(session_id, request.user_id, "assistant", answer, {"state": "needs_clarification"})
            return ChatResponse(session_id=session_id, message_id=message_id, state="needs_clarification", answer=answer, pedagogical_move="check_understanding", trace=trace + ["Context Agent: need clarification"])
        if intent == "out_of_scope":
            message_id = self.mongo.save_message(session_id, request.user_id, "user", question)
            answer = "Không có trong bài giảng. Bạn có muốn mình tìm nguồn trên web không?"
            self.mongo.set_pending_web(session_id, question, request.user_id)
            self.mongo.save_message(session_id, request.user_id, "assistant", answer, {"state": "awaiting_web_consent"})
            return ChatResponse(session_id=session_id, message_id=message_id, state="awaiting_web_consent", answer=answer, pedagogical_move="extend_concept", web_search_available=True, trace=trace + ["Intent Agent: outside course scope"])
        if self.retrieval.has_scope_conflict(question, request.document_context.doc_id):
            message_id = self.mongo.save_message(session_id, request.user_id, "user", question)
            selected_title = DOCUMENT_METADATA.get(request.document_context.doc_id or "", ("", "phạm vi hiện tại"))[1]
            answer = f"Nội dung này không thuộc {selected_title}. Bạn hãy đổi Phạm vi câu hỏi sang bài được nhắc đến rồi hỏi lại nhé."
            self.mongo.save_message(session_id, request.user_id, "assistant", answer, {"state": "needs_clarification"})
            return ChatResponse(
                session_id=session_id,
                message_id=message_id,
                state="needs_clarification",
                answer=answer,
                pedagogical_move="check_understanding",
                trace=trace + ["Scope Gate: explicit question conflicts with selected course scope"],
            )
        history = self.mongo.recent_messages(session_id)
        message_id = self.mongo.save_message(session_id, request.user_id, "user", question)
        trace.append("Retrieval Agent: Qdrant document_chunks")
        effective_scope = self.retrieval.resolve_scope(question, request.document_context.doc_id)
        if effective_scope and not request.document_context.doc_id:
            trace.append(f"Intent scope: {effective_scope}")
        try:
            sources = self.retrieval.retrieve(question + " " + selected, effective_scope)
        except Exception:
            sources = []
            trace.append("Qdrant unavailable")
        relevant = self.evidence.select(sources)
        if not relevant:
            answer = "Không có trong bài giảng. Bạn có muốn mình tìm nguồn trên web không?"
            self.mongo.set_pending_web(session_id, question, request.user_id)
            self.mongo.save_message(session_id, request.user_id, "assistant", answer, {"state": "awaiting_web_consent"})
            return ChatResponse(session_id=session_id, message_id=message_id, state="awaiting_web_consent", answer=answer, pedagogical_move="extend_concept", web_search_available=True, trace=trace + ["Evidence Gate: insufficient evidence"])
        trace.append("Evidence Gate: sources sufficient")
        result = self.tutor.answer(question, history, relevant, effective_scope)
        allowed = {source["source_id"]: source for source in relevant}
        valid_ids = self.citations.validate(result.get("citations", []), relevant)
        if not valid_ids:
            result = self.tutor.repair_citations(result, relevant)
            valid_ids = self.citations.validate(result.get("citations", []), relevant)
            trace.append("Citation repair attempt")
        if not valid_ids:
            answer = "Mình chưa có căn cứ đủ tin cậy để trả lời chính xác. Bạn có thể chọn thêm đoạn liên quan không?"
            self.mongo.save_message(session_id, request.user_id, "assistant", answer, {"state": "needs_clarification"})
            return ChatResponse(session_id=session_id, message_id=message_id, state="needs_clarification", answer=answer, pedagogical_move="check_understanding", trace=trace + ["Citation Verifier: failed safely"])
        citations = [Citation(source_id=sid, label=allowed[sid]["citation_label"], doc_id=allowed[sid].get("doc_id"), content_type=allowed[sid].get("content_type"), lecture_title=allowed[sid].get("lecture_title"), page=allowed[sid].get("page"), segment_id=allowed[sid].get("segment_id"), excerpt=allowed[sid].get("text", "")[:240]) for sid in valid_ids]
        note = None
        note = self.insights.student_note(question, relevant[0].get("lecture_code"))
        answer = result.get("follow_up_question") if result.get("needs_clarification") and result.get("follow_up_question") else result.get("answer")
        state: Literal["answered", "needs_clarification"] = "needs_clarification" if result.get("needs_clarification") else "answered"
        if state == "answered" and self.intent.broad_lookup_pattern.search(question) and not answer.rstrip().endswith("?"):
            answer = answer.rstrip() + " Bạn muốn mình giải thích sâu hơn phần nào?"
        self.mongo.save_message(session_id, request.user_id, "assistant", answer, {"citations": valid_ids, "state": state})
        move = result.get("pedagogical_move", "review_concept")
        if move not in PEDAGOGICAL_MOVES:
            move = "review_concept"
        return ChatResponse(session_id=session_id, message_id=message_id, state=state, answer=answer, citations=citations, pedagogical_move=move, learning_note=note, trace=trace + ["Tutor Response Agent", "Citation Verifier: passed"])

    async def web_answer(self, session_id: str) -> ChatResponse:
        pending = self.mongo.consume_pending_web(session_id)
        if not pending:
            raise HTTPException(status_code=409, detail="Session không chờ web consent.")
        question = pending["pending_web_question"]
        key = os.getenv("TAVILY_API_KEY")
        if not key:
            raise HTTPException(status_code=503, detail="Tavily chưa được cấu hình trong .env.")
        payload = {"api_key": key, "query": question, "max_results": 4, "search_depth": "basic"}
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                response = await client.post("https://api.tavily.com/search", json=payload)
                response.raise_for_status()
                results = response.json().get("results", [])
        except Exception:
            raise HTTPException(status_code=502, detail="Không thể tìm web lúc này. Vui lòng thử lại sau.")
        lines = [f"- {item.get('title', 'Nguồn web')}: {item.get('url')}" for item in results]
        answer = "Đây là nguồn ngoài bài giảng bạn có thể tham khảo:\\n" + "\\n".join(lines)
        message_id = self.mongo.save_message(session_id, pending.get("user_id", "demo-student"), "assistant", answer, {"external_web": True})
        return ChatResponse(session_id=session_id, message_id=message_id, state="answered", answer=answer, pedagogical_move="extend_concept", trace=["Web Search Agent: Tavily", "External sources labelled"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo = MongoStore()
    vectors = VectorStore(Embedder())
    app.state.mongo = mongo
    app.state.vectors = vectors
    app.state.orchestrator = Orchestrator(mongo, vectors, TutorAgent())
    yield
    mongo.client.close()


app = FastAPI(title="VLearn Grounded Tutor", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8000"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "mongo": app.state.mongo.ping(), "qdrant": app.state.vectors.ping(), "openai_configured": bool(os.getenv("OPENAI_API_KEY")), "tavily_configured": bool(os.getenv("TAVILY_API_KEY"))}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return app.state.orchestrator.run(request)


@app.post("/api/chat/{session_id}/web-consent", response_model=ChatResponse)
async def web_consent(session_id: str) -> ChatResponse:
    return await app.state.orchestrator.web_answer(session_id)


@app.post("/api/feedback")
def feedback(payload: FeedbackRequest) -> dict[str, bool]:
    app.state.mongo.db.feedback.insert_one({**payload.model_dump(), "created_at": utc_now()})
    return {"ok": True}


@app.get("/api/dashboard/issues")
def dashboard(lecture_code: str | None = None) -> dict[str, Any]:
    query: dict[str, Any] = {"lecture_code": lecture_code} if lecture_code else {}
    rows = list(app.state.mongo.db.issue_stats.find(query, {"_id": 0}).sort("question_count", -1).limit(12))
    return {"items": rows}


@app.get("/api/sources/{source_id}")
def get_source(source_id: str) -> dict[str, Any]:
    try:
        source = app.state.vectors.get_document_source(source_id)
    except Exception as error:
        raise HTTPException(status_code=503, detail="Không truy cập được kho tài liệu.") from error
    if not source:
        raise HTTPException(status_code=404, detail="Không tìm thấy nguồn trích dẫn.")
    return {
        "source_id": source["source_id"], "doc_id": source.get("doc_id"), "content_type": source.get("content_type"),
        "document_title": source.get("document_title"), "lecture_title": source.get("lecture_title"),
        "lecture_code": source.get("lecture_code"), "page": source.get("page"), "segment_id": source.get("segment_id"),
        "citation_label": source.get("citation_label"), "text": source.get("text", ""),
    }


@app.get("/api/documents/{document_id}")
def get_document(document_id: str) -> FileResponse:
    allowed = {
        "d1-slide-hackathon": PROJECT_ROOT / "data" / "vlearn-pack" / "slides" / "d1-slide-hackathon.pdf",
        "d2-slide-hackathon": PROJECT_ROOT / "data" / "vlearn-pack" / "slides" / "d2-slide-hackathon.pdf",
    }
    path = allowed.get(document_id)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="Slide không có trong kho dữ liệu.")
    return FileResponse(path, media_type="application/pdf", filename=path.name, content_disposition_type="inline")


app.mount("/", StaticFiles(directory=str(CODEBASE_ROOT / "dist"), html=True), name="static")
