# Series conventions

Every lab in the series follows these, so a learner who has done one knows where to look in the next.

1. **One public repository per lab**, linked from this hub.
2. **A fake provider and a real one.** Code takes the model as an argument. The fake provider is
   deterministic and free, and CI uses it. Learners switch to a real provider with one flag.
3. **No hidden network calls in tests.** Live tests exist but are skipped unless `AIENG_LIVE=1`.
4. **Deterministic checks first.** Evals start as code that checks structure and facts. Model
   graders come later, and are themselves evaluated (see the AI Evaluation Science Lab).
5. **Negative controls on every gate.** For each gate there is a broken variant, and a test that the
   gate fails on it.
6. **Errors are not answers.** Refusals, truncation and missing decisions raise or return an error;
   they are never passed downstream as output.
7. **Cost is visible.** Every real call reports tokens and an estimated cost.
8. **Eight articles per lab**, short enough to read in one sitting, each tied to code in the repo.
9. **Licences:** MIT for code, CC BY 4.0 for articles.
10. **Citation:** `CITATION.cff` and `.zenodo.json` in every repo; a Zenodo DOI for each v1.0.0 release.
11. **A "how to test this" link** from each engineering lab to its companion in the AI Quality
    Engineering series.

## Model defaults

Claude is the default provider, using `claude-opus-5-5` with `effort` set explicitly. Requests opt
into server-side refusal fallbacks. Lab 3 adds OpenAI alongside it, behind the same interface.
