# Skills map

What AI Engineer roles ask for, and where this curriculum teaches it. The list comes from current
job descriptions for AI Engineer roles focused on the product development lifecycle (PDLC) and
agentic AI.

| Skill the role asks for | Taught in | Notes |
|---|---|---|
| Python for AI services | 1 onward | Typed models, packaging, tests |
| LLM APIs, prompt engineering | 1 | Claude by default; OpenAI alongside it in lab 3 |
| Structured outputs and tool calling | 1 | Pydantic contracts, strict tool schemas |
| Agentic AI, agent loops | 1, 3, 6 | Hand-written loop first, then SDKs |
| Agent SDKs (Claude Agent SDK, OpenAI Agents SDK, LangGraph) | 3 | One agent built four ways, compared |
| MCP servers | 4 | Build, secure and test servers for the backlog, repo and CI |
| Claude Code skills, plugins, hooks, slash commands | 5 | Packaging team workflows for coding assistants |
| Cursor rules, GitHub Copilot instructions and extensions | 5 | Same workflow, three tools |
| AI across the PDLC | 1, 6 | Refinement, design review, test generation, PR review, release notes |
| RAG | 2 | Chunking, embeddings, hybrid search, citations |
| Docker | 7 | Small, reproducible images |
| CI/CD | 1 (basic), 7 | Eval gates, staged rollout |
| AWS: EKS, S3, IAM | 8 | IRSA rather than long-lived keys |
| Terraform, Helm | 8 | `terraform plan`/`validate` and Helm lint in CI; local kind cluster; real EKS optional |
| LLM evaluation | 1, 7 | Deterministic checks first; the QE series goes deeper |
| Observability | 9 | Traces, token and cost metrics, alerts |
| Guardrails | 1 (injection), 6, 9 | Data is not instructions; tool permissions; refusal handling |
| C#/.NET, Angular | Appendix | Calling the same services from a .NET API and an Angular UI |

## Levels

- **Beginner** (lab 1, start of lab 2): can call a model, get validated structured output, give it
  tools, and test all of it without spending money.
- **Intermediate** (labs 2–5): can build retrieval, agents with SDKs, MCP servers and
  coding-assistant extensions a team would actually adopt.
- **Advanced** (labs 6–9, capstone): can ship agents into the delivery process, deploy them on
  Kubernetes in AWS, and run them with known cost and reliability.
