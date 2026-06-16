# How Harness Engineering Raises Feature Quality

Research date: 2026-06-15

## Quality Thesis

Harness engineering improves feature quality by turning autonomous development from "generate code and hope" into a controlled, evidence-producing workflow. It does not make a probabilistic model perfectly reliable. It makes the development system more reliable by constraining action, exposing context, catching defects early, requiring proof, and feeding every failure back into the environment.

The practical quality bar is this: a feature is not done because an agent says it is done. It is done when the harness can show that the implementation satisfies the acceptance criteria, preserves existing behavior, respects architecture and safety constraints, and leaves an auditable trail.

## Why Quality Improves

### 1. Repeated Mistakes Become Durable Controls

The core harness-engineering move is to convert an observed agent mistake into a permanent change in the environment. If the agent repeatedly uses the wrong command, update the agent guide. If it guesses API shapes, add a typed boundary rule or schema check. If it misses a visual regression, add a screenshot script. If it writes brittle tests, add a test-quality review step.

This compounds. Each fixed failure mode reduces future review burden and makes later work start from a better baseline.

### 2. The Agent Receives Project-Specific Judgment

Humans carry implicit knowledge: architecture taste, conventions, business context, tolerated debt, and prior incidents. Agents do not naturally carry that organizational memory. A harness externalizes it into files, templates, tools, and checks the agent can actually use.

That lowers variance. The agent is less likely to solve the right problem in the wrong layer, copy an obsolete pattern, or invent a convention that conflicts with the codebase.

### 3. Feedback Shifts Left

Quality is cheaper when failures are caught during implementation instead of during human review or production. A harness runs fast sensors early:

- Type checks catch incompatible interfaces.
- Linters and formatters catch style and simple correctness issues.
- Targeted tests catch behavior regressions close to the edit.
- Architecture checks catch layer violations before they spread.
- Security scanners catch risky dependencies, secrets, and common unsafe patterns.
- Browser automation and screenshot checks catch visible UI failures.

The agent can then self-correct before a human spends time reviewing.

### 4. "Done" Requires Evidence

A strong harness requires an explicit verification report. Each acceptance criterion should map to at least one piece of evidence: a test, trace, screenshot, log, reproduction script, static check, manual approval, or documented reason a check is not applicable.

This prevents unverified success claims and makes review faster. Reviewers inspect evidence and residual risk rather than reconstructing the entire task from scratch.

### 5. Architecture And Maintainability Are Controlled Continuously

Autonomous agents can generate many small changes quickly. Without controls, small inconsistencies compound into architectural drift and maintenance debt. Harness controls protect long-term quality by encoding:

- Module boundaries.
- Dependency direction.
- Data validation rules.
- Logging and observability conventions.
- Shared utility preferences.
- Test structure and fixture patterns.
- Documentation update requirements.

Recurring drift sensors and cleanup tasks keep these controls active after merge, not only during initial implementation.

### 6. Human Judgment Moves To The Right Layer

The best use of human review is not catching every missing semicolon or forgotten command. Deterministic tools should catch those. Human judgment is most valuable for product fit, tradeoffs, architecture intent, risk tolerance, and whether the evidence is convincing.

A harness raises quality by preserving human judgment where it matters and automating the checks that machines can do consistently.

### 7. Traceability Makes The Harness Improve

Action traces, tool traces, context traces, failure-attribution logs, intervention logs, and entropy audits turn agent runs into diagnosable episodes. When a run fails, the team can ask:

- Did the agent see the right context?
- Did it use the right tools?
- Did a command fail without recovery?
- Did the tests prove the actual requirement?
- Did a human intervention reveal a missing guide or tool?
- Did the change introduce maintainability burden?

Those answers point directly to harness improvements.

## Feature Quality Contract

A harnessed feature should produce the following artifacts before it is accepted:

| Artifact | What it proves |
| --- | --- |
| Acceptance-criteria map | The implementation was checked against the requested behavior, not just against generated tests. |
| Context record | The agent consulted relevant architecture, domain, and testing guidance. |
| Diff summary | The changed files match the intended scope and avoid unrelated churn. |
| Test evidence | Targeted tests, regression tests, or approved fixtures passed, with commands recorded. |
| Static evidence | Type checks, lint, formatting, dependency, security, or architecture checks passed. |
| Runtime evidence | Logs, screenshots, videos, traces, metrics, or reproduction scripts show the behavior works in the running system when relevant. |
| Failure-attribution log | Any failed checks were diagnosed instead of patched randomly. |
| Entropy check | The change did not leave stale docs, dead files, duplicated helpers, dependency churn, or architectural residue. |
| Human approval note | A human made any required product, risk, or architecture judgment. |

## Metrics To Track

Quality should be measured by outcomes and evidence, not by lines of code generated.

| Metric | Why it matters |
| --- | --- |
| Acceptance-criteria coverage | Shows whether each requirement has verification evidence. |
| Defect escape rate | Tracks whether harnessed changes still fail after merge. |
| Review iteration count | Shows whether agents are producing review-ready work. |
| Avoidable human intervention rate | Reveals missing tools, docs, or permissions. |
| Test failure recovery rate | Shows whether agents diagnose failures coherently. |
| Architecture violation count | Measures drift against intended system structure. |
| Security finding count | Tracks whether autonomous changes introduce risk. |
| Entropy score | Captures maintenance burden such as duplicated code, stale docs, dead files, and dependency churn. |
| Verification runtime and cost | Ensures the harness remains usable and does not create runaway feedback loops. |
| Rollback or revert rate | Measures whether merged changes were genuinely safe. |

## Common Failure Modes And Harness Controls

| Agent failure mode | Harness control |
| --- | --- |
| Runs the wrong command | Command registry and `AGENTS.md` instructions. |
| Edits the wrong layer | Architecture guide, dependency rules, module-boundary checks. |
| Guesses API or data shapes | Typed SDKs, schema validation at boundaries, API docs, contract tests. |
| Claims completion without proof | Required verification report and acceptance-criteria map. |
| Fixes symptom instead of cause | Bug-reproduction protocol and failure-attribution log. |
| Writes brittle or shallow tests | Test guide, approved fixtures, mutation testing, test-quality review. |
| Adds duplicated utilities | Shared-utility rule, duplicate-code scanner, review sensor. |
| Introduces security risk | Permission policy, secrets scan, SAST rules, dependency audit. |
| Leaves stale docs or residue | Documentation checklist, entropy audit, recurring cleanup task. |
| Drifts from product intent | Human product review and explicit non-goals. |

## Practical Implementation Sequence

1. Start with a clear `AGENTS.md`: project map, safe commands, coding standards, test policy, and known mistakes.
2. Add a verification report template: require requirement-by-requirement evidence.
3. Register commands: make build, test, lint, type-check, security, and browser workflows easy for the agent to run correctly.
4. Add fast deterministic gates: targeted tests, lint, type checks, and architecture rules.
5. Add behavior evidence where relevant: fixtures, screenshots, videos, replay scripts, or trace checks.
6. Add semantic review only where deterministic checks are weak: architecture tradeoffs, product fit, test quality, overengineering.
7. Track interventions and repeated failures: every repeat should produce a harness change.
8. Run recurring drift controls: dead code, stale docs, dependency hygiene, architecture violations, and cleanup PRs.

## Bottom Line

Harness engineering raises feature quality because it makes quality a property of the development system, not just the skill of a single agent run. The agent still writes code, but the harness defines the operating environment, catches mistakes, demands evidence, preserves human judgment, and improves after every failure.

