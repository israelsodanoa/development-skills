# Prompting Reference

Prompt packets must be scoped, phase-specific, and evidence-oriented.

Required phases:

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
