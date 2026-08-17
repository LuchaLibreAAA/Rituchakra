from __future__ import annotations

from pathlib import Path

KNOWLEDGE = Path(__file__).resolve().parent / "knowledge"


def retrieve(topic: str, locale: str = "en") -> dict:
    topic_l = (topic or "").lower()
    files = sorted(KNOWLEDGE.glob("*.md"))
    chunks: list[str] = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        if any(k in text.lower() or k in f.name.lower() for k in topic_l.split()) or not topic_l:
            chunks.append(f"## {f.stem}\n{text}")
    if not chunks and files:
        chunks = [files[0].read_text(encoding="utf-8")]
    body = "\n\n".join(chunks)[:4000]
    return {
        "topic": topic,
        "locale": locale,
        "source": "bundled-rag",
        "text": body,
        "note": "AIKosh KCC ingest activates when AIKOSH_API_KEY is set.",
    }
