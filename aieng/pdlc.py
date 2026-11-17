"""The two PDLC capabilities built in lab 1.

refine_story   one structured-output call: a rough request becomes a validated UserStory
triage         a small tool-calling agent: search the backlog, read candidates, submit a decision

The agent loop is written by hand so every step is visible. Production code would usually let
an SDK's tool runner drive it (lab 3 compares the options); the decisions made here (a step
limit, tool errors returned to the model, a required final tool, a re-prompt if it is skipped)
carry over unchanged.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from aieng.backlog import TOOLS, execute
from aieng.llm import LLMError, Usage
from aieng.models import TriageDecision, UserStory

PROMPTS = Path(__file__).parent / "prompts"
MAX_STEPS = 6


def prompt(name: str) -> tuple[str, str]:
    """A prompt and its fingerprint: prompts are versioned artefacts, like code."""
    text = (PROMPTS / f"{name}.md").read_text(encoding="utf-8")
    return text, hashlib.sha256(text.replace("\r\n", "\n").encode()).hexdigest()[:12]


def refine_story(request: str, llm) -> tuple[UserStory, Usage]:
    system, _ = prompt("refine_story")
    return llm.structured(system, f"Feature request:\n{request}", UserStory)


@dataclass
class TriageResult:
    decision: TriageDecision | None
    steps: list[str] = field(default_factory=list)       # a readable trace of what the agent did
    usage: Usage = field(default_factory=Usage)
    error: str = ""


def triage(request: str, llm, max_steps: int = MAX_STEPS) -> TriageResult:
    system, _ = prompt("triage")
    messages: list = [{"role": "user", "content": request}]
    result = TriageResult(None)
    reminded = False
    for _ in range(max_steps):
        try:
            step = llm.step(system, messages, TOOLS)
        except LLMError as exc:
            result.error = f"{type(exc).__name__}: {exc}"
            return result
        result.usage = result.usage + step.usage
        messages.append({"role": "assistant", "content": step.assistant_content})
        if not step.tool_calls:
            if reminded:                                  # asked once already: give up rather than loop
                result.error = "the agent finished without calling submit_decision"
                return result
            reminded = True
            result.steps.append("reminded: call submit_decision")
            messages.append({"role": "user", "content": "Please finish by calling submit_decision."})
            continue
        tool_results = []
        for call in step.tool_calls:
            if call.name == "submit_decision":
                result.decision = TriageDecision(**call.input)
                result.steps.append(f"submit_decision -> {call.input['decision']} {call.input['story_id'] or ''}".rstrip())
                return result
            output, is_error = execute(call.name, call.input)
            result.steps.append(f"{call.name}({next(iter(call.input.values()))!r}){' -> error' if is_error else ''}")
            tool_results.append({"type": "tool_result", "tool_use_id": call.id, "content": output, "is_error": is_error})
        messages.append({"role": "user", "content": tool_results})   # every result in ONE user message
    result.error = f"no decision after {max_steps} steps"
    return result
