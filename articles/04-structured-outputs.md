# 04. Structured Outputs: Let the Schema Do the Work

*Becoming an AI Engineer, lab 1, article 4 of 8*

If code reads a model's output, the output needs a shape. Asking nicely for JSON in the prompt and
parsing it with a regular expression works until it doesn't. Structured outputs make the shape part
of the request.

## Define the contract

`aieng/models.py` defines what a user story is:

```python
class UserStory(BaseModel):
    title: str
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: list[AcceptanceCriterion]
    open_questions: list[str]
    priority: Literal["low", "medium", "high"]
```

`Literal` limits priority to three values. Field descriptions tell the model what each field is
for. The model is the contract between the LLM and the rest of your code.

## Ask for it

```python
resp = client.beta.messages.parse(
    model="claude-opus-5-5", max_tokens=16000, system=system,
    messages=[{"role": "user", "content": prompt}],
    output_format=UserStory,
    output_config={"effort": "medium"},
    ...
)
story = resp.parsed_output        # a UserStory instance
```

The SDK turns the Pydantic class into a JSON schema, the API constrains the reply to it, and the SDK
validates and returns a typed object.

## What a schema can't check

A schema guarantees shape, not quality. A story can be perfectly valid and still have a criterion
that says nothing, or a "within 2 seconds" the requester never mentioned. Those are checked by the
evals (article 07): at least two criteria, no empty parts, title length, no invented numbers, open
questions for vague requests.

Use the schema for what it's good at (types, required fields, allowed values) and evals for the
rest.

## Design tips

- Prefer a few clear fields over many optional ones.
- Give the model somewhere to put uncertainty. `open_questions` exists so the model doesn't have to
  invent an answer to fill a field.
- Use enums for anything code branches on.
