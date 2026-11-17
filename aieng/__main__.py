"""Command line for lab 1.

    python -m aieng refine "As a PM I want to export the roadmap to CSV"
    python -m aieng triage "Remind reviewers about stale pull requests"
    python -m aieng refine "..." --provider claude        # real model (needs credentials)
"""
from __future__ import annotations

import argparse
import json
import sys

from aieng.llm import DEFAULT_MODEL, LLMError, get_llm
from aieng.pdlc import refine_story, triage


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m aieng", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["refine", "triage"])
    p.add_argument("request")
    p.add_argument("--provider", choices=["fake", "claude"], default=None, help="default: $AIENG_PROVIDER or fake")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    a = p.parse_args(argv)
    llm = get_llm(a.provider, **({"model": a.model, "effort": a.effort} if a.provider == "claude" else {}))
    try:
        if a.command == "refine":
            story, usage = refine_story(a.request, llm)
            print(json.dumps(story.model_dump(), indent=2))
        else:
            r = triage(a.request, llm)
            print("\n".join(f"  {s}" for s in r.steps))
            if r.error:
                print(f"error: {r.error}", file=sys.stderr)
                return 1
            print(json.dumps(r.decision.model_dump(), indent=2))
            usage = r.usage
    except LLMError as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"[{llm.name}] tokens in {usage.input_tokens}, out {usage.output_tokens}, est. cost ${usage.cost_usd:.4f}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
