# 02. Your First LLM Call, Done Properly

*Becoming an AI Engineer, lab 1, article 2 of 8*

A first LLM call is three lines. A first LLM call you can ship is about thirty. This article walks
through the difference, using `ClaudeLLM` in `aieng/llm.py`.

## Put the model behind an interface

Every function in lab 1 takes an `llm` argument with two methods:

```python
structured(system, prompt, schema)   # -> (validated object, Usage)
step(system, messages, tools)        # -> one model turn, maybe with tool calls
```

Two classes implement it: `ClaudeLLM`, which calls the API, and `FakeLLM`, which follows fixed
rules. Your application code never knows which one it has. That single decision is what makes the
rest of the lab testable.

## The parts of a real call

```python
resp = client.beta.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    system=system,
    messages=messages,
    tools=tools,
    output_config={"effort": "medium"},
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",
)
```

- **`model`**: pin it. A model change is a behaviour change, and you want to make it on purpose.
- **`max_tokens`**: the ceiling on the reply. Too low and replies are cut off.
- **`system`**: the instructions. It lives in a file (article 03).
- **`output_config.effort`**: how hard the model thinks. Set it explicitly so cost and latency
  don't change when a default does.
- **`fallbacks`**: if the model declines a request on policy grounds, the API retries it on a
  fallback model within the same call. It's a beta, so the `betas` header opts in.

The client reads credentials from `ANTHROPIC_API_KEY` and retries rate limits and server errors on
its own.

## Check why it stopped

Every response has a `stop_reason`. Code that ignores it will eventually treat a half-finished
reply as an answer.

| `stop_reason` | Meaning | What lab 1 does |
|---|---|---|
| `end_turn` | Finished normally | Use the reply |
| `tool_use` | Wants a tool run | Run it (article 05) |
| `max_tokens` | Cut off | Raise `Truncated` |
| `refusal` | Declined, even after fallback | Raise `Refused`, with the category |

## Count the cost

Every call returns token counts. `Usage.cost_usd` turns them into dollars using the published
prices. The CLI prints it after every command. Make cost visible from day one, and nobody is
surprised by the bill later.

## Try it

```bash
python -m aieng refine "Better notifications." --provider claude --effort low
```

Then run it with `--effort high` and compare the tokens and the result.
