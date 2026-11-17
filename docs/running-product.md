# The running product: Kestrel PDLC Assistant

Kestrel Labs is a fictional company of about 60 engineers building a project-management product.
Its platform team is building an AI assistant that helps across the product development
lifecycle. Every lab adds to the same assistant, so what you learn compounds instead of resetting.

| Lab | What the assistant gains |
|---|---|
| 1 | Refines rough requests into user stories; triages them against the backlog |
| 2 | Answers questions from Kestrel's docs, ADRs and backlog, with citations |
| 3 | The triage agent rebuilt with three SDKs, to compare what each gives you |
| 4 | MCP servers for the backlog, the repository and CI, usable from any MCP client |
| 5 | Team workflows packaged for Claude Code, Cursor and Copilot |
| 6 | Agents for design review, test generation, PR review and release notes |
| 7 | Containerised, with eval gates in the delivery pipeline |
| 8 | Deployed on EKS with Terraform and Helm, reading artefacts from S3 |
| 9 | Observed, cost-controlled and running on schedules |
| Capstone | Released with an assurance case built from the evidence above |

## The backlog

`aieng/data/backlog.json` holds six stories (KES-101 to KES-106). KES-106 deliberately contains an
instruction aimed at AI assistants. It is a test fixture: the assistant must treat backlog text as
data. Later labs reuse it.

## Why a PDLC product

The work in PDLC agents is concrete and checkable: a story has acceptance criteria or it doesn't, a
duplicate is the right story or it isn't. That makes it a good place to learn engineering habits
before moving to open-ended tasks.
