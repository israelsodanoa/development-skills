# Planning And Task Breakdown Reference

Planning and task breakdown are strict gates. A request may not enter `TASKS` unless `plan.md` passes the research-backed plan quality contract, and it may not enter `IMPLEMENT` unless `tasks.md` contains atomic XS/S work items.

## Planning Frameworks

- `wbs`: decompose the request into deliverables so scope is complete before sequencing.
- `invest`: keep implementation slices independent, valuable, estimable, small, and testable.
- `smart`: phrase outcomes as specific, measurable, achievable, relevant, and verification-bound.
- `adr`: record decisions with context, decision, rationale, and consequences.
- `rapid`: name recommendation, agreement, performance, input, and decision ownership when ownership is ambiguous.
- `cynefin`: classify complexity as clear, complicated, complex, or chaotic before choosing sequencing.
- `gherkin`: express observable acceptance as Given/When/Then scenarios.
- `premortem`: identify likely failure modes before implementation and attach mitigations.

## Plan Gate

`plan.md` must include objective recap, planning standard, decomposition map, dependency graph, implementation strategy, implementation slices, decision records, verification strategy, verification matrix, premortem risks, complexity classification, sequencing rationale, parallelization boundaries, risks, and open questions.

The plan gate fails when required sections are missing, planning detail is placeholder-like, framework IDs are absent from the planning standard, decision records lack rationale or consequences, verification does not map criteria to evidence and command, or parallel/sequential boundaries are not explicit.

## Task Gate

Every task in `tasks.md` must use a `## Task <id>: <title>` heading and include task, outcome, exact scope, non-scope, size, acceptance, scenario, verify, dependencies, files, risk notes, rollback/repair, and parallelization fields.

Task size must be `XS` or `S`. Split any M, L, XL, multi-subsystem, vague, or joined-by-and task until each item is independently implementable and verifiable in one focused session.

## Approval Discipline

Use `plan_engine.py validate` and `task_engine.py validate` before approval. Treat `quality_problems` as blockers, not advice. Approval records `planning_quality` evidence in `state.json`; downstream transitions rely on the same validators.
