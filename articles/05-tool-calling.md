# 05. Tool Calling: The Model Asks, Your Code Acts

*Becoming an AI Engineer, lab 1, article 5 of 8*

With tool calling, a model can use functions you provide: search a backlog, read a file, call an
API. The key point is that the model never runs anything. It asks, in a structured message, and
your code decides whether and how to do it.

## Defining tools

`aieng/backlog.py` defines three tools as JSON Schema:

```python
{"name": "get_story",
 "description": "Read one backlog story in full by its id, e.g. KES-104.",
 "strict": True,
 "input_schema": {"type": "object",
                  "properties": {"story_id": {"type": "string"}},
                  "required": ["story_id"],
                  "additionalProperties": False}}
```

- **The description is a prompt.** It tells the model when the tool is useful. Write it for a
  reader who has never seen your code.
- **`strict: true`** makes the model's arguments match the schema exactly. Strict tools need
  `additionalProperties: false` and every property listed in `required`. A test checks this.
- **Nullable fields** use `["string", "null"]`, as `story_id` does in `submit_decision`.

## Running tools

When the model wants a tool, the reply stops with `stop_reason: "tool_use"` and contains
`tool_use` blocks with an id, a name and arguments. Your code runs the function and sends back a
`tool_result` with the same id.

Two rules from lab 1:

1. **Return errors; don't raise them.** `execute()` catches a missing story and returns
   `("error: story KES-999 not found", is_error=True)`. The model can then try something else. An
   exception would end the whole run.
2. **All results go back in one user message.** If the model asks for three tools at once, send
   three `tool_result` blocks together.

## A tool as the final answer

`submit_decision` isn't a lookup. It is how the agent hands back its answer, with a schema. That
gives you a structured result from an agent, the same way `output_format` does for a single call.

## Tools are a permission boundary

Every tool you give a model is something it can do. Lab 1's tools only read. When later labs add
tools that write (comment on a PR, create a ticket), the questions become: who approved this, and
what stops a planted instruction from triggering it? The
[Agent Testing Lab](https://github.com/K11-Software-Solutions/agent-testing-lab) covers how to test that.
