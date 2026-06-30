# Prompting Reference

Prompt packets must be scoped, phase-specific, and evidence-oriented.

Prompt packets must also be context-efficient. Put cache-stable phase instructions, context economy rules, and memory guardrails before volatile request metadata such as generation time, current objective, and transient status. End each packet with the immediate phase goal and gating rule so critical constraints are not buried in the middle of a long prompt.

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

Every prompt packet should include a compact context budget and context ledger:

- Budget status, current selected token estimate, target input budget, compression trigger, reserved output budget, and estimator.
- Selected context entries with source, priority, inclusion mode, placement, cache scope, token estimate, and summary.
- Skipped context entries with the reason a source stayed out of prompt context.

Request creation generates prompt packets for all required phases under `.harness/requests/<request_id>/prompt-packets/`. Workflow validation and phase transitions backfill missing packets for older requests. Explicit `prompt_engine.py --write` calls may refresh an individual packet and must record a history event.

Every prompt packet must include memory guardrails:

- Retrieve relevant memory before action with `memory_engine.py retrieve`, including selected and skipped sources.
- Record context economy metadata on retrieved sources: priority, inclusion mode, placement, cache scope, summary, and token estimate.
- Treat request `state.json` as working memory and `history.jsonl` as episodic memory.
- Reflect after evidence with `memory_engine.py reflect`.
- Promote only evidence-backed semantic or procedural memory with `memory_engine.py promote`.
- Record stale or superseded memory with `memory_engine.py prune` instead of silently deleting user-edited memory.

Context economy rules:

- Prefer paths and summaries over raw pasted files, long logs, or broad search dumps.
- Use excerpts only when exact text matters to the phase. Use full-file context only for small files or when the implementation cannot be correct without exact content.
- Place durable rules, source summaries, and reusable context in the stable prefix; place task-specific facts in volatile request context.
- If selected context exceeds `target_input_tokens`, compact the working summary or remove low-priority sources before adding more.
- If selected context reaches `compression_trigger_tokens`, refresh `handoffs/continuation.md`, split the task, or delegate a narrow specialist packet.

The intake prompt asks a common first batch covering objective, task type, audience, desired outcome, success criteria, non-goals, constraints, permissions, and verification expectations. It then asks type-specific follow-ups for feature, bug, refactor, UI/runtime, security/reliability, review, maintenance, or harness-improvement work, plus risk follow-ups for migrations, external systems, credentials, destructive actions, production impact, or ambiguous product behavior. Do not approve `spec.md` or enter PLAN until intake is complete.

The plan prompt must require WBS, INVEST, SMART, ADR, RAPID, Cynefin, Gherkin, and premortem framework coverage. The tasks prompt must require lowest-practical decomposition and reject placeholder, M/L/XL, multi-subsystem, or vague tasks before approval.
