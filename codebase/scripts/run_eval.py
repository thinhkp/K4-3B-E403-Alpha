"""Run the CP3 golden set against a live VLearn backend and write run artifacts."""
from __future__ import annotations

import argparse
import json
import time
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

CODEBASE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CODEBASE_ROOT.parent if CODEBASE_ROOT.name == "codebase" else CODEBASE_ROOT
DEFAULT_GOLDEN = PROJECT_ROOT / "eval" / "golden-set-cp3.json"
DEFAULT_JSON_OUTPUT = PROJECT_ROOT / "eval" / "run-1-results.json"
DEFAULT_MD_OUTPUT = PROJECT_ROOT / "eval" / "run-1-results.md"


def contains(text: str, value: str) -> bool:
    return value.casefold() in text.casefold()


def grade(response: dict[str, Any], expected: dict[str, Any]) -> tuple[bool, list[str]]:
    checks: list[str] = []
    state = response.get("state")
    answer = response.get("answer", "")
    citations = response.get("citations") or []

    if state not in expected.get("states", []):
        checks.append(f"state={state!r}, expected={expected.get('states')}")
    if len(citations) < expected.get("min_citations", 0):
        checks.append(f"citations={len(citations)} below minimum {expected['min_citations']}")
    if len(citations) > expected.get("max_citations", 10_000):
        checks.append(f"citations={len(citations)} above maximum {expected['max_citations']}")

    allowed_doc_ids = set(expected.get("allowed_doc_ids", []))
    if allowed_doc_ids:
        wrong_docs = sorted({citation.get("doc_id") for citation in citations if citation.get("doc_id") not in allowed_doc_ids})
        if wrong_docs:
            checks.append(f"citation doc_id outside allowed set: {wrong_docs}")

    allowed_pages = set(expected.get("allowed_pages", []))
    if allowed_pages:
        wrong_pages = sorted({citation.get("page") for citation in citations if citation.get("page") not in allowed_pages})
        if wrong_pages:
            checks.append(f"citation page outside allowed set: {wrong_pages}")

    prefix = expected.get("answer_starts_with")
    if prefix and not answer.startswith(prefix):
        checks.append(f"answer does not start with {prefix!r}")
    for required in expected.get("answer_contains_all", []):
        if not contains(answer, required):
            checks.append(f"answer missing required text {required!r}")
    any_values = expected.get("answer_contains_any", [])
    if any_values and not any(contains(answer, value) for value in any_values):
        checks.append(f"answer contains none of {any_values!r}")
    for forbidden in expected.get("answer_forbidden_any", []):
        if contains(answer, forbidden):
            checks.append(f"answer contains forbidden text {forbidden!r}")
    if answer.count("?") > expected.get("max_question_marks", 10_000):
        checks.append(f"answer has {answer.count('?')} question marks")
    if "web_search_available" in expected and response.get("web_search_available") is not expected["web_search_available"]:
        checks.append(f"web_search_available={response.get('web_search_available')!r}")
    return not checks, checks


def markdown_report(run: dict[str, Any]) -> str:
    summary = run["summary"]
    lines = [
        "# CP3 — Kết quả golden set run 1",
        "",
        f"- Thời điểm: `{run['run_at']}`",
        f"- Backend: `{run['base_url']}`; health: `{run['health'].get('status', 'unknown')}`",
        f"- Tổng: **{summary['passed']}/{summary['total']} đạt ({summary['pass_rate_percent']:.1f}%)**, {summary['failed']} chưa đạt.",
        "- Cách chấm: assertion trên state, số/cụm citation, phạm vi tài liệu và các ý bắt buộc; không chấm theo cảm giác.",
        "",
        "## Kết quả theo taxonomy",
        "",
        "| Lớp | Đạt | Tổng | Tỷ lệ |",
        "|---|---:|---:|---:|",
    ]
    for taxonomy, values in summary["by_taxonomy"].items():
        rate = 100 * values["passed"] / values["total"] if values["total"] else 0
        lines.append(f"| `{taxonomy}` | {values['passed']} | {values['total']} | {rate:.1f}% |")
    lines.extend([
        "",
        "## Chi tiết 20 case",
        "",
        "| ID | Lớp | Nguồn | State thực tế | Citation | Kết quả |",
        "|---|---|---|---|---:|---|",
    ])
    for item in run["results"]:
        provenance = item["provenance"].get("turn_id", "synthetic")
        actual = item.get("actual", {})
        lines.append(
            f"| {item['id']} | `{item['taxonomy']}` | `{provenance}` | `{actual.get('state', 'error')}` | "
            f"{len(actual.get('citations') or [])} | **{'Đạt' if item['passed'] else 'Rớt'}** |"
        )
    failures = [item for item in run["results"] if not item["passed"]]
    lines.extend(["", "## Phân tích case chưa đạt", ""])
    if not failures:
        lines.append("Không có case thất bại trong lượt chạy này.")
    else:
        for item in failures:
            lines.append(f"### {item['id']}")
            lines.append("")
            lines.append(f"- Câu hỏi: {item['input']['question']}")
            lines.append(f"- Sai lệch: {'; '.join(item['failures'])}")
            answer = item.get("actual", {}).get("answer", "")
            answer = "\n".join(line.rstrip() for line in answer.splitlines())
            lines.append(f"- Output thực tế: {answer}")
            lines.append("")
    lines.extend([
        "## Giới hạn của run 1",
        "",
        "- Mỗi case chạy trong session mới để lịch sử không làm nhiễu phép đo.",
        "- Assertion tự động đo hành vi quan trọng nhưng chưa thay thế chấm độc lập về độ dễ hiểu của câu văn.",
        "- Hai thành viên vẫn cần chấm độc lập cùng 5 output; nếu lệch từ 1/5 case trở lên thì phải viết lại rubric.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--golden", type=Path, default=DEFAULT_GOLDEN)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--md-output", type=Path, default=DEFAULT_MD_OUTPUT)
    args = parser.parse_args()

    golden = json.loads(args.golden.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []
    with httpx.Client(base_url=args.base_url, timeout=45) as client:
        health_response = client.get("/api/health")
        health_response.raise_for_status()
        health = health_response.json()
        for case in golden["cases"]:
            payload = {
                "session_id": f"cp3-{case['id'].lower()}-{uuid.uuid4()}",
                **case["input"],
            }
            started = time.perf_counter()
            try:
                response = client.post("/api/chat", json=payload)
                response.raise_for_status()
                actual = response.json()
                passed, failures = grade(actual, case["expected"])
                error = None
            except Exception as exc:
                actual = {}
                passed = False
                failures = [f"request failed: {type(exc).__name__}"]
                error = type(exc).__name__
            results.append({
                "id": case["id"],
                "taxonomy": case["taxonomy"],
                "frequency": case["frequency"],
                "provenance": case["provenance"],
                "input": case["input"],
                "expected": case["expected"],
                "actual": actual,
                "passed": passed,
                "failures": failures,
                "request_error": error,
                "latency_ms": round((time.perf_counter() - started) * 1000),
            })

    taxonomy_totals = Counter(item["taxonomy"] for item in results)
    taxonomy_passed = Counter(item["taxonomy"] for item in results if item["passed"])
    passed_count = sum(item["passed"] for item in results)
    run = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url,
        "golden_set": str(args.golden.relative_to(PROJECT_ROOT)),
        "health": health,
        "summary": {
            "total": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "pass_rate_percent": round(100 * passed_count / len(results), 1),
            "by_taxonomy": {
                taxonomy: {"passed": taxonomy_passed[taxonomy], "total": total}
                for taxonomy, total in sorted(taxonomy_totals.items())
            },
        },
        "results": results,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.md_output.write_text(markdown_report(run), encoding="utf-8")
    print(json.dumps(run["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
