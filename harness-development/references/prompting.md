# Prompting Reference

Prompt packets must be scoped, phase-specific, and evidence-oriented.

Required phases:

- `intake`: interview the user before planning and persist answers, waivers, assumptions, and blocking questions in `intake.md` and `state.json`.
- `specify`: derive objective, assumptions, success criteria, boundaries, risk, and open questions.
- `plan`: produce ordered implementation strategy and verification checkpoints.
- `tasks`: break the approved plan into small tasks with acceptance and verification.
- `implement`: execute one task at a time using selected context and permitted tools.
- `failure`: attribute failed checks before repair.
- `review`: inspect diff, evidence coverage, architecture, tests, and risk.
- `verify`: map criteria to evidence and residual risk.
- `improve`: convert repeated failures into durable controls.
- `handoff`: prepare resume-ready state for another agent or session.

Every prompt packet should name the request ID, current phase, objective, relevant artifact paths, required output, and gating rule.

The intake prompt asks a common first batch covering objective, task type, audience, desired outcome, success criteria, non-goals, constraints, permissions, and verification expectations. It then asks type-specific follow-ups for feature, bug, refactor, UI/runtime, security/reliability, review, maintenance, or harness-improvement work, plus risk follow-ups for migrations, external systems, credentials, destructive actions, production impact, or ambiguous product behavior. Do not approve `spec.md` or enter PLAN until intake is complete.
