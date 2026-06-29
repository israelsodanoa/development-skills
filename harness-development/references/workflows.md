# Workflows Reference

## Universal Workflow

1. Request creation: create a draft request folder, state record, `evidence/manifest.md`, all phase prompt packets, and `handoffs/continuation.md`.
2. Intake interview: ask adaptive question batches until objective, task type, audience, desired outcome, success criteria, non-goals, constraints, permissions, verification expectations, assumptions, waivers, and blocking open questions are recorded.
3. Intake completion: mark intake complete only when required fields are answered or explicitly waived.
4. Harness scan: inspect `.harness/`, command registry, project docs, tests, known failures, and control gaps.
5. Memory retrieval: load only relevant working, semantic, and procedural memory; record selected and skipped sources with `memory_engine.py retrieve`.
6. Context selection: inspect concrete docs, files, and examples; update request working memory with selected context, assumptions, and stale-memory gaps.
7. Specify: persist `spec.md` and validate it.
8. Plan: persist `plan.md` only after completed intake and spec approval. Apply WBS decomposition, dependency graphing, ADR/RAPID decisions, Cynefin complexity classification, verification matrixing, premortem risks, sequencing rationale, and parallelization boundaries; approve only when strict validation passes.
9. Tasks: persist `tasks.md` only after plan approval. Break work into atomic XS/S tasks with exact scope, non-scope, acceptance, Given/When/Then scenario when applicable, verification evidence, dependencies, likely files, risk notes, rollback/repair, and parallelization label; approve only when strict validation passes.
10. Implement: make small changes and update state/history after meaningful steps. Refresh evidence artifacts when commands, runtime checks, reviews, or waivers produce proof.
11. Feedback: run targeted deterministic checks first, then broader checks as risk grows.
12. Reflection: after evidence, failures, or important decisions, record the lesson with `memory_engine.py reflect`.
13. Memory promotion or pruning: promote evidence-backed durable facts/controls with `memory_engine.py promote`; record stale or superseded memory with `memory_engine.py prune`.
14. Failure attribution: diagnose failed checks before repair.
15. Runtime verification: gather browser, API, log, trace, screenshot, or metric evidence when behavior is observable only at runtime.
16. Review: run self-review and specialist review when deterministic checks are insufficient.
17. Evidence report: map acceptance criteria to evidence before closeout and keep `evidence/manifest.md` linked to the raw command/runtime/review artifacts.

## Specialist Handoffs

Use handoff packets for architecture, security, test, UI, product, release, or continuation work. Every request has a stable `handoffs/continuation.md` that is refreshed after phase changes and verification updates; specialist or timestamped packets may be added as needed. Include objective, current phase, completed work, pending work, files changed, commands run, decisions, assumptions, risks, and next action.

## Harness Improvement

When the same failure mode repeats, add or propose a durable control: rule, doc, test, checker, command registry entry, known-failure note, review prompt, or permission boundary.

## Planning And Task Breakdown

Treat `quality_problems` from `plan_engine.py validate` and `task_engine.py validate` as blockers. Approved plan and task gates record `planning_quality` evidence in `state.json`; downstream transitions use the same validators.
