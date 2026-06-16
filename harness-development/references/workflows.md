# Workflows Reference

## Universal Workflow

1. Intake: derive objective, success criteria, non-goals, risk, and approvals.
2. Harness scan: inspect `.harness/`, command registry, project docs, tests, and known failures.
3. Context selection: load only relevant memory, docs, files, and examples.
4. Specify: persist `spec.md` and validate it.
5. Plan: persist `plan.md` only after spec approval.
6. Tasks: persist `tasks.md` only after plan approval.
7. Implement: make small changes and update state/history after meaningful steps.
8. Feedback: run targeted deterministic checks first, then broader checks as risk grows.
9. Failure attribution: diagnose failed checks before repair.
10. Runtime verification: gather browser, API, log, trace, screenshot, or metric evidence when behavior is observable only at runtime.
11. Review: run self-review and specialist review when deterministic checks are insufficient.
12. Evidence report: map acceptance criteria to evidence before closeout.

## Specialist Handoffs

Use handoff packets for architecture, security, test, UI, product, release, or continuation work. Include objective, current phase, completed work, pending work, files changed, commands run, decisions, assumptions, risks, and next action.

## Harness Improvement

When the same failure mode repeats, add or propose a durable control: rule, doc, test, checker, command registry entry, known-failure note, review prompt, or permission boundary.
