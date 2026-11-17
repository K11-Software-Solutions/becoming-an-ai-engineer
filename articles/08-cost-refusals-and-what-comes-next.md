# 08. Cost, Refusals and What Comes Next

*Becoming an AI Engineer, lab 1, article 8 of 8*

The last article of lab 1 covers two things that separate a demo from a service, then looks ahead.

## Cost

Every real call returns input and output tokens. Lab 1 prices them (per million tokens, input and
output):

| Model | Input | Output |
|---|---|---|
| `claude-opus-5-5` | $4.00 | $20.00 |
| `claude-sonnet-5-5` | $2.00 | $10.00 |
| `claude-haiku-5-5` | $0.10 | $0.50 |

An agent run costs the sum of its steps, and each step re-sends the conversation so far. That is
why the triage loop has a step limit, and why `TriageResult` adds up usage across steps.

Ways to cut cost, roughly in order of how often they help:

1. Lower `effort` for simple tasks. Try it per task and keep the eval passing.
2. Keep prompts and tool results short. A tool that returns a whole document when a title would do
   costs you on every later step.
3. Use a smaller model for steps that don't need a large one, and prove it with the eval.

The [AI Performance and Cost Lab](https://github.com/K11-Software-Solutions/ai-performance-cost-lab)
measures cost per *good* answer, which is the number that matters.

## Refusals

Sometimes a model declines a request. Lab 1 handles it in two layers:

- **Server-side fallback.** Requests opt in with `fallbacks="default"`, so a policy refusal is
  retried on a fallback model inside the same API call.
- **Explicit errors.** If the request is still refused, `ClaudeLLM` raises `Refused` with the
  category. The triage loop turns that into an error result, never a decision.

The rule underneath: a refusal, a truncated reply or a missing decision is never passed on as if it
were an answer.

## What lab 1 gave you

You can now call a model with pinned settings, get validated structured output, give it tools,
run it in a loop with limits, see what it cost, and test all of it without a network connection,
with negative controls proving the tests can fail.

## What comes next

- **Lab 2, RAG Engineering**: the assistant answers questions from Kestrel's documents, with
  citations.
- **Lab 3, Agent SDKs**: this triage agent rebuilt with the Claude Agent SDK, the OpenAI Agents SDK
  and LangGraph, compared on the same eval.
- **Lab 4, MCP servers**: the backlog tools moved into an MCP server any client can use.

The habits stay the same in every lab: a fake for CI, deterministic checks first, negative
controls, and visible cost.
