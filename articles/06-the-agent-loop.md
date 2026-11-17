# 06. The Agent Loop, Written by Hand

*Becoming an AI Engineer, lab 1, article 6 of 8*

An agent is a model calling tools in a loop until the job is done. SDKs will run that loop for you
(lab 3 compares them), but write it once by hand first. Then you know what an SDK is doing, and
which decisions are still yours.

## The loop

`triage()` in `aieng/pdlc.py` is about 30 lines:

```text
messages = [the request]
repeat up to MAX_STEPS times:
    step = model(system, messages, tools)
    append the assistant turn
    if no tool calls:  remind once, then give up
    for each tool call:
        if submit_decision: return the decision
        run the tool, collect the result
    append all results as one user message
give up: no decision after MAX_STEPS
```

A typical run:

```text
search_backlog('Remind assigned reviewers when a pull request has no review activity')
get_story('KES-103')
submit_decision -> duplicate KES-103
```

## The decisions in those 30 lines

Each one is a design choice you'll make again with any SDK:

| Decision | Lab 1's choice | Why |
|---|---|---|
| When does it stop? | When `submit_decision` is called | A clear end, with a structured answer |
| What if it never stops? | `MAX_STEPS = 6` | Bounds cost and time |
| What if it stops without answering? | Remind once, then report an error | One nudge is cheap; looping isn't |
| What if a tool fails? | Return the error to the model | It can recover |
| What if the model refuses? | Return an error result | Never pass a refusal on as a decision |
| What do we record? | A readable trace of steps, plus usage | You can't debug what you can't see |

## Keep the trace

`TriageResult.steps` lists every tool call. When an agent gives a wrong answer, the trace tells you
whether it searched badly, read the wrong story, or read the right one and misjudged it. Those
have different fixes.

## When to use an SDK instead

Once you need streaming, parallel tool calls at scale, sub-agents, or built-in tools such as file
access, an SDK saves real work. The Claude Agent SDK, for example, gives you Claude Code's harness
as a library. Lab 3 rebuilds this exact agent with three SDKs, so you can compare like with like.
