# Workflows Reference

## Universal Workflow

1. Request creation: create a draft request folder and state record.
2. Intake interview: ask adaptive question batches until objective, task type, audience, desired outcome, success criteria, non-goals, constraints, permissions, verification expectations, assumptions, waivers, and blocking open questions are recorded.
3. Intake completion: mark intake complete only when required fields are answered or explicitly waived.
4. Harness scan: inspect `.harness/`, command registry, project docs, tests, and known failures.
5. Context selection: load only relevant memory, docs, files, and examples.
6. Specify: persist `spec.md` and validate it.
7. Plan: persist `plan.md` only after completed intake and spec approval. Apply WBS decomposition, dependency graphing, ADR/RAPID decisions, Cynefin complexity classification, verification matrixing, premortem risks, sequencing rationale, and parallelization boundaries; approve only when strict validation passes.
8. Tasks: persist `tasks.md` only after plan approval. Break work into atomic XS/S tasks with exact scope, non-scope, acceptance, Given/When/Then scenario when applicable, verification evidence, dependencies, likely files, risk notes, rollback/repair, and parallelization label; approve only when strict validation passes.
9. Implement: make small changes and update state/history after meaningful steps.
10. Feedback: run targeted deterministic checks first, then broader checks as risk grows.
11. Failure attribution: diagnose failed checks before repair.
12. Runtime verification: gather browser, API, log, trace, screenshot, or metric evidence when behavior is observable only at runtime.
13. Review: run self-review and specialist review when deterministic checks are insufficient.
14. Evidence report: map acceptance criteria to evidence before closeout.

## Specialist Handoffs

Use handoff packets for architecture, security, test, UI, product, release, or continuation work. Include objective, current phase, completed work, pending work, files changed, commands run, decisions, assumptions, risks, and next action.

## Harness Improvement

When the same failure mode repeats, add or propose a durable control: rule, doc, test, checker, command registry entry, known-failure note, review prompt, or permission boundary.

## Planning And Task Breakdown

Treat `quality_problems` from `plan_engine.py validate` and `task_engine.py validate` as blockers. Approved plan and task gates record `planning_quality` evidence in `state.json`; downstream transitions use the same validators.
