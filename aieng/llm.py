"""Two interchangeable model providers behind one small interface.

    ClaudeLLM   calls the Claude API through the official Anthropic Python SDK
    FakeLLM     deterministic rules with the same interface, so tests and CI need no API key

Every function in this lab takes an `llm` argument, so the same code runs against either.
That is the main habit lab 1 teaches: design LLM code so you can test it without the LLM.

Two methods cover what most application code needs:

    structured(system, prompt, schema)  ->  (validated Pydantic object, Usage)
    step(system, messages, tools)       ->  Step: one model turn, possibly with tool calls

ClaudeLLM opts into server-side refusal fallbacks (beta): if the model declines a request on
policy grounds, the API retries it on a fallback model inside the same call. A request that
is still refused raises Refused, and a reply cut off by max_tokens raises Truncated; neither
is ever returned as if it were a normal answer.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

DEFAULT_MODEL = "claude-opus-5-5"
FALLBACK_BETA = "server-side-fallback-2026-07-01"
PRICES_PER_MTOK = {                      # (input, output) USD per million tokens, from the published price list
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}


class LLMError(Exception):
    pass


class Refused(LLMError):
    """The model declined the request (stop_reason "refusal"), even after any fallback."""


class Truncated(LLMError):
    """The reply hit max_tokens: it is incomplete and must not be used as an answer."""


@dataclass
class Usage:
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(self.model or other.model, self.input_tokens + other.input_tokens,
                     self.output_tokens + other.output_tokens)

    @property
    def cost_usd(self) -> float:
        pin, pout = PRICES_PER_MTOK.get(self.model, (0.0, 0.0))
        return (self.input_tokens * pin + self.output_tokens * pout) / 1_000_000


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class Step:
    stop_reason: str                      # end_turn | tool_use
    text: str
    tool_calls: list[ToolCall]
    assistant_content: Any                # what to append to the conversation as the assistant turn
    usage: Usage = field(default_factory=Usage)


class ClaudeLLM:
    name = "claude"

    def __init__(self, model: str = DEFAULT_MODEL, effort: str = "medium", client: Any = None):
        import anthropic                       # imported here so fake mode never needs the SDK configured
        self.client = client or anthropic.Anthropic()   # credentials from ANTHROPIC_API_KEY or an `ant auth login` profile
        self.model, self.effort = model, effort

    def _common(self, system: str) -> dict:
        return {"model": self.model, "max_tokens": 16000, "system": system,
                "betas": [FALLBACK_BETA], "fallbacks": "default"}

    @staticmethod
    def _check(resp) -> None:
        if resp.stop_reason == "refusal":
            category = getattr(getattr(resp, "stop_details", None), "category", None)
            raise Refused(f"declined (category: {category})")
        if resp.stop_reason == "max_tokens":
            raise Truncated("reply hit max_tokens")

    def structured(self, system: str, prompt: str, schema: type[BaseModel]) -> tuple[BaseModel, Usage]:
        resp = self.client.beta.messages.parse(
            **self._common(system),
            messages=[{"role": "user", "content": prompt}],
            output_format=schema,
            output_config={"effort": self.effort},
        )
        self._check(resp)
        return resp.parsed_output, Usage(resp.model, resp.usage.input_tokens, resp.usage.output_tokens)

    def step(self, system: str, messages: list, tools: list[dict]) -> Step:
        resp = self.client.beta.messages.create(
            **self._common(system), messages=messages, tools=tools, output_config={"effort": self.effort},
        )
        self._check(resp)
        calls = [ToolCall(b.id, b.name, json.loads(json.dumps(b.input))) for b in resp.content if b.type == "tool_use"]
        text = "".join(b.text for b in resp.content if b.type == "text")
        return Step("tool_use" if calls else "end_turn", text, calls, resp.content,
                    Usage(resp.model, resp.usage.input_tokens, resp.usage.output_tokens))


# --- the fake ------------------------------------------------------------------------------

WORD = re.compile(r"[A-Za-z0-9']+")
VAGUE = re.compile(r"\b(maybe|somehow|etc|something|better|improve|nicer|faster)\b", re.I)


class FakeLLM:
    """Deterministic stand-in. Good enough to exercise every code path; not a model.

    behaviour: "faithful" (default), "refuse" (every call is declined), "truncate" (replies cut
    off), "invent_numbers" (stories gain limits nobody asked for), "no_submit" (the triage agent
    never calls submit_decision), "obey_backlog" (follows instructions found inside backlog text:
    a prompt-injection failure).
    """
    name = "fake"

    def __init__(self, behaviour: str | None = None):
        self.behaviour = behaviour or os.environ.get("FAKE_LLM_BEHAVIOUR", "faithful")

    def _guard(self) -> None:
        if self.behaviour == "refuse":
            raise Refused("declined (category: fake)")
        if self.behaviour == "truncate":
            raise Truncated("reply hit max_tokens")

    def structured(self, system: str, prompt: str, schema: type[BaseModel]) -> tuple[BaseModel, Usage]:
        self._guard()
        from aieng.models import UserStory
        if schema is not UserStory:
            raise NotImplementedError(schema)
        prompt = re.sub(r"^\s*Feature request:\s*", "", prompt)
        words = WORD.findall(prompt)
        first = re.split(r"(?<=[.!?])\s+", prompt.strip())[0].rstrip(".!?")
        title = first[:77] + "..." if len(first) > 80 else first
        role = re.search(r"\bas an? ([a-z ]+?)(?:,| I\b)", prompt, re.I)
        story = UserStory(
            title=title or "Untitled request",
            as_a=role.group(1).strip() if role else "member of the product team",
            i_want=first[0].lower() + first[1:] if first else "to do what the request describes",
            so_that="the outcome described in the request is achieved",
            acceptance_criteria=[
                {"given": "the feature is available", "when": f"a user does what the request asks: {first.lower()}",
                 "then": "the result described in the request is visible to the user"},
                {"given": "the feature is available", "when": "something goes wrong while doing it",
                 "then": "the user sees a clear error and no data is lost"},
            ],
            open_questions=(["What exactly counts as done? The request is vague."]
                            if len(words) < 12 or VAGUE.search(prompt) else []),
            priority="high" if re.search(r"\b(security|password|data loss|outage|blocked)\b", prompt, re.I) else "medium",
        )
        if self.behaviour == "invent_numbers":
            story.acceptance_criteria[0].then += " within 2 seconds for up to 500 items"
        return story, Usage("fake", len(words) * 2, 200)

    def step(self, system: str, messages: list, tools: list[dict]) -> Step:
        self._guard()
        request = messages[0]["content"]
        results = [b for m in messages if m["role"] == "user" and isinstance(m["content"], list)
                   for b in m["content"] if b.get("type") == "tool_result"]
        n = len(results)
        if n == 0:                                    # 1st turn: search with the request's terms
            return self._call(0, "search_backlog", {"query": request})
        last = json.loads(results[-1]["content"]) if not results[-1].get("is_error") else None
        if n == 1 and last:                           # 2nd turn: read the best match
            return self._call(1, "get_story", {"story_id": last[0]["id"]})
        if self.behaviour == "no_submit":
            return Step("end_turn", "I think this is probably new.", [], [{"type": "text", "text": "I think this is probably new."}])
        if n >= 2 and last and isinstance(last, dict):
            story = last
            if self.behaviour == "obey_backlog" and "mark every request as a duplicate of" in story["description"]:
                target = re.search(r"duplicate of (\S+?)\.", story["description"]).group(1)
                return self._call(2, "submit_decision", {"decision": "duplicate", "story_id": target,
                                                         "reason": "the backlog note says so"})
            searched = json.loads(results[0]["content"])
            score = searched[0]["matching_terms"] if searched else 0
            decision = "duplicate" if score >= 4 else "related" if score >= 2 else "new"
            return self._call(2, "submit_decision", {
                "decision": decision, "story_id": story["id"] if decision != "new" else None,
                "reason": f"{score} key terms shared with {story['id']}: {story['title']}"})
        return self._call(2, "submit_decision", {"decision": "new", "story_id": None, "reason": "no matching stories"})

    @staticmethod
    def _call(i: int, name: str, args: dict) -> Step:
        call = ToolCall(f"toolu_fake_{i}", name, args)
        content = [{"type": "tool_use", "id": call.id, "name": name, "input": args}]
        return Step("tool_use", "", [call], content, Usage("fake", 300, 40))


def get_llm(provider: str | None = None, **kwargs) -> ClaudeLLM | FakeLLM:
    provider = provider or os.environ.get("AIENG_PROVIDER", "fake")
    if provider == "claude":
        return ClaudeLLM(**kwargs)
    if provider == "fake":
        return FakeLLM()
    raise ValueError(f"unknown provider {provider!r}: use fake or claude")
