# 01. What an AI Engineer Actually Builds

*Becoming an AI Engineer, lab 1, article 1 of 8*

An AI Engineer does not train models. They build software that uses them: services that call a
model, give it tools, check what comes back, and run reliably for real users. Most of the job is
ordinary engineering. The model is one dependency, and an unusual one.

## What makes the dependency unusual

A normal function returns the same output for the same input. A model does not, and it can be
wrong in ways that look right. Three consequences shape everything in this series:

1. **You need contracts.** If a model's output feeds other code, define its shape and validate it.
2. **You need tests that don't call the model.** Otherwise your tests are slow, cost money and
   fail at random.
3. **You need evals.** Unit tests check your code. Evals check whether the system, model included,
   does the job well enough.

## What the job descriptions ask for

Read a few AI Engineer job descriptions and the same list comes up: agentic AI, agent SDKs, MCP
servers, extensions for coding assistants such as Claude Code, Cursor and Copilot, cloud deployment
with Terraform, Helm and Kubernetes, CI/CD, evaluation, observability, guardrails and RAG. The
[skills map](../docs/skills-map.md) shows where each one is taught.

That list is long, but it rests on four foundations, and they are what lab 1 covers:

| Foundation | Lab 1 code |
|---|---|
| Calling a model properly | `aieng/llm.py` |
| Getting structured, validated output | `aieng/models.py`, `refine_story` |
| Letting the model use tools | `aieng/backlog.py` |
| Running a loop until the job is done | `triage` in `aieng/pdlc.py` |

Everything later (SDKs, MCP, deployment) is a better way of doing one of these four things.

## The product we build

Each lab adds to the **Kestrel PDLC Assistant**, an assistant that helps a software team across the
product development lifecycle. In lab 1 it does two things: it turns rough feature requests into
user stories, and it checks new requests against the backlog for duplicates.

PDLC work is a good place to start because results are checkable. A story has testable acceptance
criteria or it doesn't. A duplicate points to the right story or it doesn't.

## Try it

```bash
python -m aieng refine "As a product manager, I want to export the roadmap to CSV so I can share it with finance."
```

This runs on the fake provider: no API key, no cost. Article 02 explains why that comes first.
