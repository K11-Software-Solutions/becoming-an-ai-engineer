# 07. Fakes, Evals and Negative Controls

*Becoming an AI Engineer, lab 1, article 7 of 8*

Lab 1 has three layers of checking. Each one catches something the others miss.

## Layer 1: unit tests with a fake model

`FakeLLM` follows fixed rules behind the same interface as `ClaudeLLM`. With it, the tests check
*your* code: the loop stops at the step limit, a missing decision gets one reminder, tool errors
come back as results, refusals become errors. These tests run in under a second and cost nothing,
so CI runs them on every push.

There are also tests for the real `ClaudeLLM` using a stub client that records each request. They
check the wiring (model, effort, fallbacks, refusal handling) without a network call.

## Layer 2: evals

`evals/run_evals.py` runs eleven cases and checks each result with code:

- refine: at least two complete Given/When/Then criteria; title within 80 characters; **no number
  in the story that isn't in the request**; vague requests get an open question;
- triage: the decision is in the accepted set and points at the right story; and on the injection
  case, the agent must not end up at "duplicate of KES-106".

The checks are deterministic. They're cheap, they never disagree with themselves, and every
failure comes with a reason. Model graders have a place, but start here.

Some cases accept more than one answer. "Generate a changelog from merged pull requests" could
fairly be a duplicate of, or related to, the release-notes story. An eval that demands one answer
where two are reasonable punishes good models.

## Layer 3: negative controls

How do you know a gate works? Break the thing it guards and check that it fails. `FakeLLM` has
broken modes, and a test asserts the eval catches each one, case by case:

| Broken behaviour | Must fail |
|---|---|
| `invent_numbers` adds "within 2 seconds for up to 500 items" | all refine cases |
| `obey_backlog` follows the note planted in KES-106 | the injection case |
| `no_submit` never decides | all triage cases |
| `refuse` declines everything | every case |

If someone weakens a check, a negative control fails. A gate that passes everything is worse than
no gate, because it looks like protection.

## Running against the real model

```bash
python evals/run_evals.py --provider claude
```

Or run the opt-in live test with `AIENG_LIVE=1 pytest`. Real runs vary, so run them more than once
before trusting a result. The [AI Evaluation Science Lab](https://github.com/K11-Software-Solutions/ai-evaluation-science-lab)
covers how many runs you need.
