# Prompting Reference

Prompt packets must be scoped, phase-specific, and evidence-oriented.

Required phases:

- `intake`: interview the user before planning and persist answers, waivers, assumptions, and blocking questions in `intake.md` and `state.json`.
- `specify`: derive objective, assumptions, success criteria, boundaries, risk, and open questions.
- `plan`: produce a research-backed plan with WBS decomposition, dependency graph, implementation slices, ADR/RAPID decision records, verification matrix, premortem risks, Cynefin complexity classification, sequencing rationale, parallelization boundaries, risks, and open questions.
- `tasks`: break the approved plan into atomic XS/S tasks with exact scope, non-scope, acceptance, Given/When/Then scenario when applicable, verification command/evidence, dependencies, likely files, risk notes, rollback/repair, and parallelization label.
- `implement`: execute one task at a time using selected context and permitted tools.
- `failure`: attribute failed checks before repair.
- `review`: inspect diff, evidence coverage, architecture, tests, and risk.
- `verify`: map criteria to evidence and residual risk.
- `improve`: convert repeated failures into durable controls.
- `handoff`: prepare resume-ready state for another agent or session.

Every prompt packet should name the request ID, current phase, objective, relevant artifact paths, required output, and gating rule.

Request creation generates prompt packets for all required phases under `.harness/requests/<request_id>/prompt-packets/`. Workflow validation and phase transitions backfill missing packets for older requests. Explicit `prompt_engine.py --write` calls may refresh an individual packet and must record a history event.

Every prompt packet must include memory guardrails:

- Retrieve relevant memory before action with `memory_engine.py retrieve`, including selected and skipped sources.
- Treat request `state.json` as working memory and `history.jsonl` as episodic memory.
- Reflect after evidence with `memory_engine.py reflect`.
- Promote only evidence-backed semantic or procedural memory with `memory_engine.py promote`.
- Record stale or superseded memory with `memory_engine.py prune` instead of silently deleting user-edited memory.

The intake prompt asks a common first batch covering objective, task type, audience, desired outcome, success criteria, non-goals, constraints, permissions, and verification expectations. It then asks type-specific follow-ups for feature, bug, refactor, UI/runtime, security/reliability, review, maintenance, or harness-improvement work, plus risk follow-ups for migrations, external systems, credentials, destructive actions, production impact, or ambiguous product behavior. Do not approve `spec.md` or enter PLAN until intake is complete.

The plan prompt must require WBS, INVEST, SMART, ADR, RAPID, Cynefin, Gherkin, and premortem framework coverage. The tasks prompt must require lowest-practical decomposition and reject placeholder, M/L/XL, multi-subsystem, or vague tasks before approval.
