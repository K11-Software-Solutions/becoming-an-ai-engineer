"""The team's backlog and the tools that read it.

Tool definitions are plain JSON Schema with `strict: true`, so every call the model makes
matches the schema exactly. The functions run in our process: the model only asks for them.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

BACKLOG = json.loads((Path(__file__).parent / "data" / "backlog.json").read_text(encoding="utf-8"))
WORD = re.compile(r"[a-z0-9]+")
STOP = frozenset("a an and are as be by can for from i in is it of on or our the their to we with when should users user".split())


def _terms(text: str) -> set[str]:
    return {w.rstrip("s") for w in WORD.findall(text.lower()) if w not in STOP}


def search_backlog(query: str, limit: int = 3) -> list[dict]:
    """Stories ranked by shared terms with the query."""
    q = _terms(query)
    scored = []
    for s in BACKLOG:
        overlap = len(q & _terms(s["title"] + " " + s["description"]))
        if overlap:
            scored.append({"id": s["id"], "title": s["title"], "status": s["status"], "matching_terms": overlap})
    return sorted(scored, key=lambda r: (-r["matching_terms"], r["id"]))[:limit]


def get_story(story_id: str) -> dict:
    for s in BACKLOG:
        if s["id"] == story_id:
            return s
    raise KeyError(f"story {story_id} not found")


TOOLS = [
    {"name": "search_backlog", "description": "Search the backlog for stories sharing terms with the query. Returns id, title, status and how many terms matched.",
     "strict": True,
     "input_schema": {"type": "object", "properties": {"query": {"type": "string", "description": "Key terms from the request"}},
                      "required": ["query"], "additionalProperties": False}},
    {"name": "get_story", "description": "Read one backlog story in full by its id, e.g. KES-104.",
     "strict": True,
     "input_schema": {"type": "object", "properties": {"story_id": {"type": "string"}},
                      "required": ["story_id"], "additionalProperties": False}},
    {"name": "submit_decision", "description": "Record the triage decision. Call exactly once, at the end.",
     "strict": True,
     "input_schema": {"type": "object", "properties": {
         "decision": {"type": "string", "enum": ["duplicate", "related", "new"]},
         "story_id": {"type": ["string", "null"], "description": "Existing story for duplicate or related, else null"},
         "reason": {"type": "string"}},
         "required": ["decision", "story_id", "reason"], "additionalProperties": False}},
]


def execute(name: str, args: dict) -> tuple[str, bool]:
    """Run a read tool. Returns (result as text, is_error). submit_decision is handled by the agent loop."""
    try:
        if name == "search_backlog":
            return json.dumps(search_backlog(args["query"])), False
        if name == "get_story":
            return json.dumps(get_story(args["story_id"])), False
        return f"unknown tool {name}", True
    except (KeyError, TypeError) as exc:
        return f"error: {exc}", True
