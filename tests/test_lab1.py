"""Lab 1 tests. All run in fake mode; the last one calls Claude only when AIENG_LIVE=1."""
import json
import os

import pytest

from aieng.backlog import TOOLS, execute, search_backlog
from aieng.llm import FakeLLM, Refused, Truncated, Usage, get_llm
from aieng.models import UserStory
from aieng.pdlc import prompt, refine_story, triage
from evals.run_evals import load_cases, run


# --- tools ----------------------------------------------------------------------------------

def test_tool_schemas_are_strict():
    for tool in TOOLS:
        schema = tool["input_schema"]
        assert tool["strict"] is True
        assert schema["additionalProperties"] is False
        assert set(schema["required"]) == set(schema["properties"])


def test_search_ranks_by_shared_terms():
    hits = search_backlog("remind reviewers about a waiting pull request")
    assert hits[0]["id"] == "KES-103"
    assert search_backlog("quantum blockchain") == []


def test_tool_errors_are_returned_not_raised():
    text, is_error = execute("get_story", {"story_id": "KES-999"})
    assert is_error and "not found" in text
    assert execute("delete_story", {})[1] is True


# --- structured output ----------------------------------------------------------------------

def test_refine_returns_a_valid_story():
    story, usage = refine_story("As a designer, I want to comment on mockups so feedback stays in one place.", FakeLLM())
    assert isinstance(story, UserStory)
    assert len(story.acceptance_criteria) >= 2
    assert story.as_a == "designer"
    assert usage.output_tokens > 0


def test_usage_cost():
    assert Usage("claude-opus-5-5", 1_000_000, 100_000).cost_usd == pytest.approx(6.0)
    assert (Usage("claude-haiku-5-5", 10, 1) + Usage("", 10, 1)).input_tokens == 20


def test_prompt_fingerprint_is_stable():
    _, a = prompt("triage")
    _, b = prompt("triage")
    assert a == b and len(a) == 12


# --- the agent loop -------------------------------------------------------------------------

def test_triage_finds_duplicate_with_trace():
    r = triage("Remind assigned reviewers when a pull request has no review activity", FakeLLM())
    assert r.decision.decision == "duplicate" and r.decision.story_id == "KES-103"
    assert [s.split("(")[0].split(" ")[0] for s in r.steps] == ["search_backlog", "get_story", "submit_decision"]


def test_triage_reprompts_once_then_gives_up():
    r = triage("Add a Slack integration", FakeLLM("no_submit"))
    assert r.decision is None
    assert "submit_decision" in r.error
    assert r.steps.count("reminded: call submit_decision") == 1


def test_refusal_and_truncation_are_errors_not_answers():
    with pytest.raises(Refused):
        refine_story("anything", FakeLLM("refuse"))
    with pytest.raises(Truncated):
        refine_story("anything", FakeLLM("truncate"))
    assert triage("anything", FakeLLM("refuse")).error.startswith("Refused")


def test_step_limit():
    r = triage("Remind reviewers about pull requests", FakeLLM(), max_steps=1)
    assert r.decision is None and "no decision after 1 steps" in r.error


# --- the eval gate and its negative controls -------------------------------------------------

def test_eval_gate_passes_on_faithful_fake():
    rows, _ = run(FakeLLM(), load_cases())
    assert all(r["passed"] for r in rows), [r for r in rows if not r["passed"]]


@pytest.mark.parametrize("behaviour, expected_failures", [
    ("invent_numbers", {"R1", "R2", "R3", "R4", "R5"}),
    ("obey_backlog", {"T6"}),
    ("no_submit", {"T1", "T2", "T3", "T4", "T5", "T6"}),
    ("refuse", {c["id"] for c in load_cases()}),
])
def test_eval_gate_catches_each_broken_model(behaviour, expected_failures):
    """Negative controls: a gate that cannot fail proves nothing."""
    rows, _ = run(FakeLLM(behaviour), load_cases())
    assert {r["id"] for r in rows if not r["passed"]} == expected_failures


def test_get_llm_defaults_to_fake(monkeypatch):
    monkeypatch.delenv("AIENG_PROVIDER", raising=False)
    assert get_llm().name == "fake"
    with pytest.raises(ValueError):
        get_llm("gpt")


# --- live (opt-in) --------------------------------------------------------------------------

@pytest.mark.skipif(os.environ.get("AIENG_LIVE") != "1", reason="set AIENG_LIVE=1 to call the real model")
def test_live_claude_eval_gate():
    rows, usage = run(get_llm("claude"), load_cases())
    print(json.dumps(rows, indent=2), f"cost ${usage.cost_usd:.4f}")
    assert sum(r["passed"] for r in rows) == len(rows)


# --- ClaudeLLM wiring, with a stub client (no network) --------------------------------------

class _Stub:
    """Records request kwargs and returns a canned response, standing in for anthropic.Anthropic()."""
    def __init__(self, response):
        self.calls, self.response = [], response
        self.beta = self
        self.messages = self

    def parse(self, **kw):
        self.calls.append(kw)
        return self.response

    create = parse


def _resp(stop_reason, content=(), parsed=None):
    from types import SimpleNamespace as NS
    return NS(stop_reason=stop_reason, content=list(content), parsed_output=parsed, model="claude-opus-5-5",
              usage=NS(input_tokens=1000, output_tokens=200), stop_details=NS(category="cyber"))


def test_claude_requests_carry_fallbacks_and_effort():
    from types import SimpleNamespace as NS
    from aieng.llm import ClaudeLLM
    stub = _Stub(_resp("tool_use", [NS(type="tool_use", id="t1", name="search_backlog", input={"query": "pdf"})]))
    step = ClaudeLLM(effort="low", client=stub).step("sys", [{"role": "user", "content": "x"}], TOOLS)
    kw = stub.calls[0]
    assert kw["model"] == "claude-opus-5-5" and kw["fallbacks"] == "default"
    assert kw["betas"] == ["server-side-fallback-2026-07-01"] and kw["output_config"] == {"effort": "low"}
    assert step.tool_calls[0].name == "search_backlog"
    assert step.usage.cost_usd == pytest.approx(0.008)


def test_claude_refusal_raises_with_category():
    from aieng.llm import ClaudeLLM
    with pytest.raises(Refused, match="cyber"):
        ClaudeLLM(client=_Stub(_resp("refusal"))).structured("sys", "x", UserStory)
