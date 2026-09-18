import React, {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { createRoot } from "react-dom/client";
import { Document, Page, pdfjs } from "react-pdf";
import "./index.css";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString();

const TRACE_STEPS = [
  "Input Guard",
  "Retrieval Agent",
  "Evidence Gate",
  "Tutor Response Agent",
  "Citation Verifier",
];

const EMPTY_VIEWER = {
  mode: "empty",
  title: "Trình xem tài liệu",
  meta: "Bấm citation trong câu trả lời để mở đúng slide hoặc đoạn transcript.",
  badge: "Chưa chọn",
};

function uid(prefix) {
  return `${prefix}-${crypto.randomUUID()}`;
}

function SendIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="m4 4 16 8-16 8 3-8-3-8Z" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M7 12h13" strokeLinecap="round" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="m6 6 12 12M18 6 6 18" strokeLinecap="round" />
    </svg>
  );
}

function ThumbIcon({ down = false }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className={`h-4 w-4 ${down ? "rotate-180" : ""}`}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path d="M7 10v10H4a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2h3Zm0 10h9.3a2 2 0 0 0 1.9-1.4l2-6A2 2 0 0 0 18.3 10H14l.7-3.4A2.2 2.2 0 0 0 12.5 4L7 10v10Z" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function LoadingDots() {
  return (
    <span className="inline-flex h-6 items-center gap-1" role="status" aria-label="Tutor đang soạn câu trả lời">
      {[0, 1, 2].map((dot) => (
        <span
          key={dot}
          className="h-1.5 w-1.5 animate-typing-dot rounded-full bg-primary"
          style={{ animationDelay: `${dot * 140}ms` }}
        />
      ))}
    </span>
  );
}

function AppHeader({ activeView, onViewChange }) {
  return (
    <header className="flex h-[66px] items-center gap-3 border-b-[3px] border-emerald-400 bg-ink px-4 text-white lg:px-[4vw]">
      <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-emerald-400 font-black text-ink">V</span>
      <span className="text-lg font-extrabold">VLearn</span>
      <span className="ml-auto hidden text-sm text-indigo-100 sm:block">K4 · AI in Action</span>
      <nav className="flex gap-1" aria-label="Chế độ xem">
        {[
          ["student", "Học viên"],
          ["ta", "Giảng viên & TA"],
        ].map(([value, label]) => (
          <button
            key={value}
            type="button"
            onClick={() => onViewChange(value)}
            className={`cursor-pointer rounded-lg px-2.5 py-2 text-sm font-bold transition-colors duration-200 ${
              activeView === value ? "bg-indigo-900 text-white" : "text-indigo-100 hover:bg-indigo-950/70"
            }`}
          >
            {label}
          </button>
        ))}
      </nav>
    </header>
  );
}

function useElementWidth(ref) {
  const [width, setWidth] = useState(0);

  useLayoutEffect(() => {
    if (!ref.current) return undefined;
    const update = () => setWidth(ref.current?.clientWidth ?? 0);
    update();
    const observer = new ResizeObserver(update);
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [ref]);

  return width;
}

function PdfCanvas({ source }) {
  const containerRef = useRef(null);
  const containerWidth = useElementWidth(containerRef);
  const [baseViewportWidth, setBaseViewportWidth] = useState(0);
  const [numPages, setNumPages] = useState(0);
  const [error, setError] = useState("");
  const [activePage, setActivePage] = useState(source.page || 1);

  const pageNumber = Math.max(1, Math.min(activePage, numPages || activePage));
  const scale = baseViewportWidth ? Math.max(containerWidth, 1) / baseViewportWidth : 1;

  const loadPageViewport = useCallback(async (pdf) => {
    setNumPages(pdf.numPages);
    const targetPage = Math.max(1, Math.min(source.page || 1, pdf.numPages));
    const page = await pdf.getPage(targetPage);
    setBaseViewportWidth(page.getViewport({ scale: 1 }).width);
    setError("");
  }, [source.page]);

  useEffect(() => {
    setBaseViewportWidth(0);
    setError("");
    setNumPages(0);
    setActivePage(source.page || 1);
  }, [source.url, source.page]);

  const changePage = (nextPage) => {
    const upperBound = numPages || 1;
    setActivePage(Math.max(1, Math.min(Number(nextPage) || 1, upperBound)));
  };

  return (
    <div className="flex h-full w-full flex-col overflow-hidden bg-slate-100">
      <div className="flex shrink-0 items-center justify-between gap-2 border-b border-slate-200 bg-white px-3 py-2 text-xs text-slate-600">
        <span className="hidden sm:block">Dùng nút để xem các trang khác của slide.</span>
        <div className="ml-auto flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => changePage(pageNumber - 1)}
            disabled={pageNumber <= 1}
            className="secondary-button !px-2 !py-1 disabled:cursor-not-allowed"
            aria-label="Trang trước"
          >
            ←
          </button>
          <label className="flex items-center gap-1 whitespace-nowrap">
            Trang
            <input
              type="number"
              min="1"
              max={numPages || undefined}
              value={pageNumber}
              onChange={(event) => setActivePage(event.target.value)}
              onBlur={(event) => changePage(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.currentTarget.blur();
                }
              }}
              className="w-12 rounded border border-slate-300 px-1 py-1 text-center text-xs text-ink"
              aria-label="Số trang slide"
            />
            <span>/ {numPages || "…"}</span>
          </label>
          <button
            type="button"
            onClick={() => changePage(pageNumber + 1)}
            disabled={!numPages || pageNumber >= numPages}
            className="secondary-button !px-2 !py-1 disabled:cursor-not-allowed"
            aria-label="Trang sau"
          >
            →
          </button>
        </div>
      </div>
      <div className="min-h-0 flex-1 overflow-auto scroll-smooth p-5">
        <div ref={containerRef} className="min-h-full w-full">
        <div key={`${source.url}-${pageNumber}`} className="mx-auto w-fit animate-pdf-in">
          <Document
            key={`${source.url}-${source.page}`}
            file={source.url}
            onLoadSuccess={loadPageViewport}
            onLoadError={(reason) => setError(reason?.message || "Không thể tải PDF.")}
            loading={<div className="p-8 text-sm font-semibold text-slate-600">Đang tải PDF…</div>}
            error={<div className="p-8 text-sm font-semibold text-red-700">{error || "Không thể tải PDF."}</div>}
          >
            {baseViewportWidth > 0 && (
              <Page
                pageNumber={pageNumber}
                scale={scale}
                renderTextLayer={false}
                renderAnnotationLayer={false}
                loading={<div className="p-8 text-sm text-slate-600">Đang dựng trang {pageNumber}…</div>}
              />
            )}
          </Document>
        </div>
      </div>
      </div>
    </div>
  );
}

function TranscriptView({ source }) {
  const segmentRef = useRef(null);

  useEffect(() => {
    segmentRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [source.segmentId]);

  return (
    <div className="h-full overflow-auto scroll-smooth bg-slate-50 p-5">
      <article className="mx-auto max-w-3xl rounded-xl border border-slate-200 bg-white p-5 text-[15px] leading-7 text-slate-700 shadow-sm">
        <div className="mb-4 text-xs font-extrabold uppercase tracking-[0.12em] text-primary">Transcript bài giảng</div>
        <mark
          ref={segmentRef}
          id={source.segmentId || undefined}
          className="block scroll-m-8 rounded-lg border-l-4 border-amber-400 bg-amber-100/80 px-4 py-3 text-slate-800"
        >
          <strong className="mb-2 block text-sm text-ink">{source.badge}</strong>
          <span className="whitespace-pre-wrap">{source.text}</span>
        </mark>
      </article>
    </div>
  );
}

function SourceViewer({ viewer, isOpen, onClose }) {
  return (
    <aside aria-hidden={!isOpen} className="panel flex h-full min-h-[420px] min-w-0 flex-col lg:min-h-0">
      <header className="flex min-h-[73px] items-center justify-between gap-3 border-b border-slate-200 px-4 py-3.5">
        <div className="min-w-0">
          <strong className="block truncate text-sm text-ink">{viewer.title}</strong>
          <small className="mt-0.5 block line-clamp-2 text-xs text-slate-600">{viewer.meta}</small>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <span className="rounded-md bg-indigo-50 px-2 py-1 text-xs font-extrabold text-primary">{viewer.badge}</span>
          <button
            type="button"
            onClick={onClose}
            tabIndex={isOpen ? 0 : -1}
            className="grid h-8 w-8 cursor-pointer place-items-center rounded-lg border border-slate-200 bg-white text-slate-600 transition-colors duration-200 hover:border-indigo-300 hover:bg-indigo-50 hover:text-primary"
            aria-label="Đóng trình xem tài liệu"
            title="Đóng tài liệu"
          >
            <CloseIcon />
          </button>
        </div>
      </header>
      <div className="min-h-0 flex-1 overflow-hidden">
        {viewer.mode === "empty" && (
          <div className="grid h-full place-items-center p-8 text-center text-sm leading-6 text-slate-600">
            <p className="max-w-sm">
              Nguồn trích dẫn sẽ mở tại đây. Citation <strong>[trang N]</strong> mở đúng trang PDF; citation <strong>[đoạn Txx-xxx]</strong> mở đúng đoạn transcript.
            </p>
          </div>
        )}
        {viewer.mode === "loading" && (
          <div className="grid h-full place-items-center text-sm font-semibold text-slate-600">Đang mở nguồn…</div>
        )}
        {viewer.mode === "error" && (
          <div className="grid h-full place-items-center p-8 text-center text-sm font-semibold text-red-700">{viewer.error}</div>
        )}
        {viewer.mode === "pdf" && <PdfCanvas source={viewer} />}
        {viewer.mode === "transcript" && <TranscriptView source={viewer} />}
      </div>
    </aside>
  );
}

function Trace({ steps, complete }) {
  const visibleSteps = complete ? TRACE_STEPS : steps;
  if (!visibleSteps?.length) return null;
  return (
    <div className="mt-3 border-t border-slate-200 pt-2 font-mono text-[10px] leading-4 text-slate-500" aria-label="Agent trace">
      {visibleSteps.join(" → ")}
    </div>
  );
}

function AssistantMessage({ message, onCitation, onRate, onWebConsent, disabled }) {
  return (
    <div className="mb-4 flex items-start gap-2.5">
      <span className="grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-emerald-400 text-[10px] font-black text-ink">AI</span>
      <div className="max-w-[91%] rounded-xl rounded-bl-sm border border-slate-200 bg-slate-50 px-3.5 py-3 text-sm text-slate-800">
        <strong className="text-ink">VLearn Tutor</strong>
        <div className="mt-1.5 min-h-6 whitespace-pre-wrap leading-6">
          {message.text || message.loading ? message.text || <LoadingDots /> : "Không nhận được nội dung trả lời."}
          {message.streaming && message.text && <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-primary align-middle" aria-hidden="true" />}
        </div>

        {!!message.citations?.length && (
          <div className="mt-2 flex flex-wrap gap-x-2 gap-y-1">
            {message.citations.map((citation) => (
              <button
                key={citation.source_id}
                type="button"
                onClick={(event) => onCitation(citation, event.currentTarget)}
                className="cursor-pointer font-bold text-primary underline decoration-indigo-300 underline-offset-2 transition-colors duration-200 hover:text-indigo-800"
              >
                {citation.label}
              </button>
            ))}
          </div>
        )}

        {(message.pedagogicalMove || message.state) && (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {message.pedagogicalMove && (
              <span className="rounded-md bg-emerald-100 px-2 py-1 text-[11px] font-extrabold text-emerald-800">{message.pedagogicalMove}</span>
            )}
            {message.state && <span className="text-[11px] font-bold text-slate-500">{message.state}</span>}
          </div>
        )}

        {!!message.citations?.length && (
          <div className="mt-3 space-y-2" aria-label="Nguồn liên quan">
            {message.citations.map((citation) => (
              <button
                type="button"
                key={`source-${citation.source_id}`}
                onClick={(event) => onCitation(citation, event.currentTarget)}
                className="block w-full cursor-pointer rounded-lg border border-slate-200 bg-white px-3 py-2 text-left text-xs leading-5 text-slate-600 transition-colors duration-200 hover:border-indigo-300 hover:bg-indigo-50"
              >
                <strong className="text-ink">{citation.label}</strong>
                <span> · {citation.lecture_title || "Tài liệu học"}</span>
                {citation.excerpt && <span className="mt-0.5 block line-clamp-3">{citation.excerpt}</span>}
              </button>
            ))}
          </div>
        )}

        {message.learningNote && (
          <div className="mt-3 rounded-r-lg border-l-[3px] border-primary bg-indigo-50 px-3 py-2 text-xs leading-5">
            <strong>Lưu ý học tập:</strong> {message.learningNote}
          </div>
        )}

        {message.webSearchAvailable && !message.webDismissed && (
          <div className="mt-3 flex flex-wrap gap-2">
            <button type="button" disabled={disabled} onClick={() => onWebConsent(true)} className="secondary-button border-primary bg-primary text-white hover:bg-indigo-700">
              Tìm nguồn trên web
            </button>
            <button type="button" disabled={disabled} onClick={() => onWebConsent(false, message.id)} className="secondary-button">
              Không, quay lại bài học
            </button>
          </div>
        )}

        {!message.loading && !message.streaming && !message.error && (
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-600">
            <span>Hữu ích?</span>
            <button
              type="button"
              onClick={() => onRate(message, "up")}
              className={`secondary-button ${message.rating === "up" ? "border-emerald-400 bg-emerald-50 text-emerald-800" : ""}`}
              aria-label="Đánh giá hữu ích"
            >
              <ThumbIcon /> Có
            </button>
            <button
              type="button"
              onClick={() => onRate(message, "down")}
              className={`secondary-button ${message.rating === "down" ? "border-emerald-400 bg-emerald-50 text-emerald-800" : ""}`}
              aria-label="Đánh giá chưa hữu ích"
            >
              <ThumbIcon down /> Chưa
            </button>
          </div>
        )}

        <Trace steps={message.traceSteps} complete={message.traceComplete} />
      </div>
    </div>
  );
}

function toAssistantPatch(data) {
  return {
    backendMessageId: data.message_id,
    citations: data.citations || [],
    pedagogicalMove: data.pedagogical_move,
    state: data.state,
    learningNote: data.learning_note,
    webSearchAvailable: Boolean(data.web_search_available),
  };
}

async function consumeSse(response, onDelta) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let metadata = {};

  const consumeEvent = (rawEvent) => {
    const payload = rawEvent
      .split("\n")
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).trimStart())
      .join("\n");
    if (!payload || payload === "[DONE]") return;
    const event = JSON.parse(payload);
    if (event.type === "content_block_delta" && event.delta?.type === "text_delta") {
      onDelta(event.delta.text || "");
    } else if (typeof event.delta === "string") {
      onDelta(event.delta);
    }
    if (event.type === "metadata" || event.type === "result" || event.response) {
      metadata = { ...metadata, ...(event.response || event.data || event) };
    }
  };

  while (true) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    const events = buffer.split(/\r?\n\r?\n/);
    buffer = events.pop() || "";
    events.forEach(consumeEvent);
    if (done) break;
  }
  if (buffer.trim()) consumeEvent(buffer);
  return metadata;
}

function revealFallbackText(text, onChunk) {
  const words = text.match(/\S+\s*/g) || [];
  const chunks = [];
  for (let index = 0; index < words.length; index += 3) chunks.push(words.slice(index, index + 3).join(""));
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion || chunks.length === 0) {
    onChunk(text);
    return Promise.resolve();
  }
  return new Promise((resolve) => {
    let index = 0;
    const timer = window.setInterval(() => {
      onChunk(chunks[index]);
      index += 1;
      if (index >= chunks.length) {
        window.clearInterval(timer);
        resolve();
      }
    }, 42);
  });
}

function ChatPanel({ onCitation, notify }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [scope, setScope] = useState("");
  const [busy, setBusy] = useState(false);
  const inputRef = useRef(null);
  const messagesRef = useRef(null);
  const pinnedToBottomRef = useRef(true);
  const sessionRef = useRef(sessionStorage.getItem("vlearn-session") || null);

  const patchMessage = useCallback((id, patch) => {
    setMessages((current) => current.map((message) => (
      message.id === id
        ? { ...message, ...(typeof patch === "function" ? patch(message) : patch) }
        : message
    )));
  }, []);

  useLayoutEffect(() => {
    if (!pinnedToBottomRef.current || !messagesRef.current) return;
    messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
  }, [messages]);

  const handleScroll = () => {
    const node = messagesRef.current;
    if (!node) return;
    pinnedToBottomRef.current = node.scrollHeight - node.scrollTop - node.clientHeight < 72;
  };

  const runRequest = useCallback(async ({ userText, requestUrl, requestBody }) => {
    const userId = uid("user");
    const assistantId = uid("assistant");
    pinnedToBottomRef.current = true;
    setMessages((current) => [
      ...current,
      { id: userId, role: "user", text: userText },
      { id: assistantId, role: "assistant", text: "", loading: true, streaming: false, traceSteps: [TRACE_STEPS[0]], traceComplete: false },
    ]);
    setBusy(true);

    let traceIndex = 1;
    const traceTimer = window.setInterval(() => {
      if (traceIndex >= TRACE_STEPS.length) return;
      const next = TRACE_STEPS.slice(0, traceIndex + 1);
      traceIndex += 1;
      patchMessage(assistantId, { traceSteps: next });
    }, 520);

    try {
      const response = await fetch(requestUrl, {
        method: "POST",
        headers: requestBody ? { "Content-Type": "application/json" } : undefined,
        body: requestBody ? JSON.stringify(requestBody) : undefined,
      });
      if (!response.ok) {
        let detail = "Tutor không phản hồi.";
        try {
          const errorBody = await response.json();
          detail = errorBody.detail || detail;
        } catch {
          // The response can be plain text when a proxy fails.
        }
        throw new Error(detail);
      }

      const contentType = response.headers.get("content-type") || "";
      if (contentType.includes("text/event-stream") && response.body) {
        patchMessage(assistantId, { loading: false, streaming: true });
        const data = await consumeSse(response, (delta) => {
          patchMessage(assistantId, (message) => ({ text: `${message.text}${delta}`, loading: false, streaming: true }));
        });
        if (data.session_id) {
          sessionRef.current = data.session_id;
          sessionStorage.setItem("vlearn-session", data.session_id);
        }
        patchMessage(assistantId, { ...toAssistantPatch(data), loading: false, streaming: false });
      } else {
        const data = await response.json();
        if (data.session_id) {
          sessionRef.current = data.session_id;
          sessionStorage.setItem("vlearn-session", data.session_id);
        }
        patchMessage(assistantId, { ...toAssistantPatch(data), loading: true, streaming: true });
        await revealFallbackText(data.answer || "", (chunk) => {
          patchMessage(assistantId, (message) => ({ text: `${message.text}${chunk}`, loading: false, streaming: true }));
        });
        patchMessage(assistantId, { loading: false, streaming: false });
      }
    } catch (error) {
      patchMessage(assistantId, {
        text: error.message,
        loading: false,
        streaming: false,
        error: true,
        state: "error",
      });
      notify(error.message);
    } finally {
      window.clearInterval(traceTimer);
      patchMessage(assistantId, { traceSteps: TRACE_STEPS, traceComplete: true });
      setBusy(false);
      window.requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [notify, patchMessage]);

  const submit = (event) => {
    event?.preventDefault();
    const question = input.trim();
    if (!question || busy) return;
    setInput("");
    runRequest({
      userText: question,
      requestUrl: "/api/chat",
      requestBody: {
        session_id: sessionRef.current,
        user_id: "demo-student",
        question,
        document_context: { doc_id: scope || null },
      },
    });
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  const rate = async (message, rating) => {
    if (!message.backendMessageId) return;
    try {
      const response = await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionRef.current,
          message_id: message.backendMessageId,
          rating,
        }),
      });
      if (!response.ok) throw new Error("Chưa lưu được đánh giá.");
      patchMessage(message.id, { rating });
      notify("Đã ghi nhận đánh giá.");
    } catch (error) {
      notify(error.message);
    }
  };

  const webConsent = (accepted, messageId) => {
    if (!accepted) {
      patchMessage(messageId, { webDismissed: true });
      inputRef.current?.focus();
      return;
    }
    if (!sessionRef.current || busy) return;
    runRequest({
      userText: "Tìm nguồn ngoài bài giảng",
      requestUrl: `/api/chat/${encodeURIComponent(sessionRef.current)}/web-consent`,
    });
  };

  return (
    <section className="panel flex min-h-[590px] min-w-0 flex-col lg:h-full lg:min-h-0">
      <header className="shrink-0 bg-ink px-4 py-4 text-white">
        <div className="flex items-center gap-2.5">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-emerald-400 text-[10px] font-black text-ink">AI</span>
          <div>
            <strong className="block">VLearn Tutor</strong>
            <small className="block text-xs text-indigo-100">Trả lời có căn cứ từ tài liệu học</small>
          </div>
        </div>
        <div className="mt-3 flex items-center gap-2.5 rounded-xl bg-indigo-950/70 p-2.5">
          <label htmlFor="scope" className="shrink-0 text-xs font-bold text-indigo-100">Phạm vi câu hỏi</label>
          <select
            id="scope"
            value={scope}
            onChange={(event) => setScope(event.target.value)}
            disabled={busy}
            className="min-w-0 flex-1 rounded-lg border border-indigo-700 bg-ink px-2.5 py-2 text-xs text-white"
          >
            <option value="">Toàn bộ dữ liệu bài học</option>
            <option value="d1-slide-hackathon">Chỉ Day 1 · AI & LLM Foundation</option>
            <option value="d2-slide-hackathon">Chỉ Day 2 · Xác định bài toán AI</option>
          </select>
        </div>
      </header>

      <div
        ref={messagesRef}
        onScroll={handleScroll}
        className="min-h-0 flex-1 overflow-y-auto overscroll-contain px-4 py-4"
        aria-live="polite"
      >
        {messages.length === 0 && (
          <div className="mx-auto mt-16 max-w-sm text-center text-sm leading-6 text-slate-600">
            Chọn phạm vi nếu cần rồi đặt câu hỏi. Tutor sẽ truy xuất tài liệu và hiển thị nguồn liên quan.
          </div>
        )}
        {messages.map((message) => (
          message.role === "user" ? (
            <div key={message.id} className="mb-4 flex justify-end">
              <div className="max-w-[86%] rounded-xl rounded-br-sm bg-indigo-100 px-3.5 py-3 text-sm leading-6 text-ink">{message.text}</div>
            </div>
          ) : (
            <AssistantMessage
              key={message.id}
              message={message}
              onCitation={onCitation}
              onRate={rate}
              onWebConsent={webConsent}
              disabled={busy}
            />
          )
        ))}
      </div>

      <form onSubmit={submit} className="shrink-0 border-t border-slate-200 bg-slate-50 px-3.5 py-3">
        <label htmlFor="question" className="mb-1.5 block text-xs font-bold text-slate-600">Câu hỏi của bạn</label>
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            id="question"
            required
            rows={2}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            disabled={busy}
            placeholder="Ví dụ: Context window ảnh hưởng thế nào đến chất lượng câu trả lời?"
            className="max-h-32 min-h-[52px] min-w-0 flex-1 resize-y rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 disabled:cursor-wait disabled:bg-slate-100"
          />
          <button
            type="submit"
            disabled={busy || !input.trim()}
            className="grid h-11 w-11 shrink-0 cursor-pointer place-items-center rounded-xl bg-primary text-white transition-colors duration-200 hover:bg-indigo-700 disabled:cursor-wait disabled:opacity-50"
            aria-label="Gửi câu hỏi"
          >
            <SendIcon />
          </button>
        </div>
      </form>
    </section>
  );
}

function StudentWorkspace({ notify }) {
  const [viewer, setViewer] = useState(EMPTY_VIEWER);
  const [isViewerOpen, setIsViewerOpen] = useState(false);
  const citationTriggerRef = useRef(null);
  const viewerTimerRef = useRef(null);
  const focusTimerRef = useRef(null);

  useEffect(() => () => {
    window.clearTimeout(viewerTimerRef.current);
    window.clearTimeout(focusTimerRef.current);
  }, []);

  const openCitation = useCallback(async (citation, trigger) => {
    citationTriggerRef.current = trigger || null;
    window.clearTimeout(viewerTimerRef.current);
    setIsViewerOpen(true);

    const common = {
      title: "Tài liệu bài học",
      meta: `${citation.lecture_title || "Nguồn trích dẫn"} · ${citation.label}`,
      badge: citation.label,
    };

    if (citation.content_type === "slide" && citation.doc_id && citation.page) {
      const nextViewer = {
        ...common,
        mode: "pdf",
        page: Number(citation.page),
        url: `/api/documents/${encodeURIComponent(citation.doc_id)}`,
      };
      if (isViewerOpen) {
        setViewer(nextViewer);
      } else {
        setViewer({ ...common, mode: "loading" });
        viewerTimerRef.current = window.setTimeout(() => setViewer(nextViewer), 300);
      }
      return;
    }

    setViewer({ ...common, mode: "loading" });
    try {
      const response = await fetch(`/api/sources/${encodeURIComponent(citation.source_id)}`);
      const source = await response.json();
      if (!response.ok) throw new Error(source.detail || "Không mở được nguồn.");
      const sourceCommon = {
        title: source.document_title || "Tài liệu bài học",
        meta: `${source.lecture_title || source.lecture_code || ""} · ${source.citation_label}`,
        badge: source.citation_label,
      };
      if (source.content_type === "slide" && source.doc_id && source.page) {
        setViewer({
          ...sourceCommon,
          mode: "pdf",
          page: Number(source.page),
          url: `/api/documents/${encodeURIComponent(source.doc_id)}`,
        });
      } else {
        setViewer({
          ...sourceCommon,
          mode: "transcript",
          segmentId: source.segment_id,
          text: source.text || "Không có nội dung transcript.",
        });
      }
    } catch (error) {
      setViewer({ ...common, mode: "error", error: error.message });
      notify(error.message);
    }
  }, [isViewerOpen, notify]);

  const closeViewer = useCallback(() => {
    window.clearTimeout(viewerTimerRef.current);
    setIsViewerOpen(false);
    focusTimerRef.current = window.setTimeout(() => citationTriggerRef.current?.focus(), 320);
  }, []);

  return (
    <section className="flex min-h-[660px] flex-col overflow-hidden lg:h-[calc(100vh-154px)] lg:flex-row">
      <div
        className={`min-w-0 overflow-hidden transition-[width,height,margin,opacity,transform] duration-300 ease-out ${
          isViewerOpen
            ? "mb-4 h-[460px] translate-y-0 opacity-100 lg:mb-0 lg:mr-4 lg:h-full lg:w-[calc(50%-0.5rem)] lg:translate-x-0"
            : "pointer-events-none mb-0 h-0 -translate-y-3 opacity-0 lg:mr-0 lg:h-full lg:w-0 lg:-translate-x-4 lg:translate-y-0"
        }`}
      >
        <SourceViewer viewer={viewer} isOpen={isViewerOpen} onClose={closeViewer} />
      </div>
      <div
        className={`min-h-[590px] min-w-0 transition-[width,max-width] duration-300 ease-out ${
          isViewerOpen
            ? "w-full lg:w-[calc(50%-0.5rem)] lg:max-w-none"
            : "mx-auto w-full max-w-3xl"
        }`}
      >
        <ChatPanel onCitation={openCitation} notify={notify} />
      </div>
    </section>
  );
}

function Dashboard() {
  const [lecture, setLecture] = useState("");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/dashboard/issues${lecture ? `?lecture_code=${encodeURIComponent(lecture)}` : ""}`);
      const data = await response.json();
      setItems(data.items || []);
    } finally {
      setLoading(false);
    }
  }, [lecture]);

  useEffect(() => { load(); }, [load]);
  const lectureCodes = useMemo(() => [...new Set(items.map((item) => item.lecture_code))].sort(), [items]);
  const questionCount = items.reduce((sum, item) => sum + (item.question_count || 0), 0);

  return (
    <section>
      <div className="panel mb-4 flex items-end gap-3 p-4">
        <label htmlFor="lecture" className="min-w-56 text-xs font-bold text-slate-600">
          Lọc theo bài học
          <select id="lecture" value={lecture} onChange={(event) => setLecture(event.target.value)} className="mt-1 block w-full rounded-lg border border-slate-300 px-2.5 py-2 text-sm">
            <option value="">Tất cả bài</option>
            {lectureCodes.map((code) => <option key={code} value={code}>{code}</option>)}
          </select>
        </label>
        <button type="button" onClick={load} className="secondary-button">Làm mới</button>
      </div>
      <div className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        {[
          ["Chủ đề hiển thị", items.length],
          ["Tổng lượt hỏi trong nhóm", questionCount.toLocaleString("vi-VN")],
          ["Dữ liệu", "K4 freeform tổng hợp"],
        ].map(([label, value]) => (
          <article key={label} className="panel p-4"><small className="text-slate-600">{label}</small><strong className="mt-1 block text-xl text-ink">{value}</strong></article>
        ))}
      </div>
      <div className="panel overflow-auto">
        <table className="w-full border-collapse text-left text-sm">
          <thead><tr className="text-xs uppercase tracking-wide text-slate-500"><th className="p-3">Chủ đề</th><th className="p-3">Bài</th><th className="p-3">Lượt hỏi</th><th className="p-3">Tỷ lệ</th><th className="p-3">Lưu ý</th></tr></thead>
          <tbody>
            {loading && <tr><td colSpan="5" className="border-t border-slate-200 p-4">Đang tải dashboard…</td></tr>}
            {!loading && items.length === 0 && <tr><td colSpan="5" className="border-t border-slate-200 p-4">Chưa có insight.</td></tr>}
            {!loading && items.map((item) => (
              <tr key={`${item.lecture_code}-${item.title}`} className="border-t border-slate-200">
                <td className="p-3 font-bold text-ink">{item.title}</td><td className="p-3">{item.lecture_code}</td><td className="p-3">{Number(item.question_count).toLocaleString("vi-VN")}</td><td className="p-3">{Math.round((item.question_rate || 0) * 100)}%</td><td className="p-3">{item.student_note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function App() {
  const [activeView, setActiveView] = useState("student");
  const [health, setHealth] = useState({ ready: false, text: "Đang kết nối…" });
  const [toast, setToast] = useState("");
  const toastTimerRef = useRef(null);

  const notify = useCallback((message) => {
    setToast(message);
    window.clearTimeout(toastTimerRef.current);
    toastTimerRef.current = window.setTimeout(() => setToast(""), 2400);
  }, []);

  useEffect(() => {
    let active = true;
    fetch("/api/health")
      .then((response) => response.json())
      .then((data) => {
        if (!active) return;
        const ready = Boolean(data.mongo && data.qdrant);
        setHealth({ ready, text: ready ? "MongoDB và Qdrant sẵn sàng" : "Database chưa sẵn sàng" });
      })
      .catch(() => active && setHealth({ ready: false, text: "Không kết nối được backend" }));
    return () => {
      active = false;
      window.clearTimeout(toastTimerRef.current);
    };
  }, []);

  return (
    <>
      <AppHeader activeView={activeView} onViewChange={setActiveView} />
      <main className="mx-auto max-w-[1600px] px-4 pb-6 pt-4 lg:px-[4vw]">
        <section className="mb-4 flex items-end justify-between gap-4">
          <div>
            <div className="text-[11px] font-extrabold uppercase tracking-[0.12em] text-primary">Grounded learning assistant</div>
            <h1 className="mt-1 text-xl font-bold tracking-tight text-ink sm:text-2xl">Hỏi bài. Mở đúng trang nguồn.</h1>
          </div>
          <div className="hidden items-center text-xs font-bold text-slate-600 sm:flex">
            <span className={`mr-1.5 h-2 w-2 rounded-full ${health.ready ? "bg-emerald-500" : "bg-slate-400"}`} />{health.text}
          </div>
        </section>
        {activeView === "student" ? <StudentWorkspace notify={notify} /> : <Dashboard />}
      </main>
      <div
        className={`fixed bottom-5 left-1/2 z-50 -translate-x-1/2 rounded-lg bg-ink px-3.5 py-2.5 text-sm text-white shadow-panel transition-all duration-200 ${toast ? "translate-y-0 opacity-100" : "pointer-events-none translate-y-3 opacity-0"}`}
        role="status"
      >
        {toast}
      </div>
    </>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
