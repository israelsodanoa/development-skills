# Use Cases And Workflows

Research date: 2026-06-15

## 1. Use Case Catalog

| ID | Use case | Primary actor | Trigger | Desired outcome |
| --- | --- | --- | --- | --- |
| UC-001 | Bootstrap a repository harness | Human engineer | "Set this repo up for harnessed agent development." | Project map, command registry, memory index, verification template, and initial control gaps. |
| UC-002 | Implement a feature | Human engineer or product owner | Feature request with desired behavior. | Feature branch or patch with evidence mapped to acceptance criteria. |
| UC-003 | Fix a bug | Human engineer or support signal | Bug report, failing test, trace, log, or reproduction. | Root-cause-oriented fix with reproduction and regression evidence. |
| UC-004 | Refactor safely | Technical lead | Maintainability or architecture improvement request. | Behavior-preserving refactor with architecture and regression evidence. |
| UC-005 | Build or change UI | Product/design stakeholder | UI task, screenshot, Figma link, or design requirement. | Visual and behavioral implementation verified through browser evidence. |
| UC-006 | Improve security or reliability | Security/reliability owner | Vulnerability, audit finding, incident, or risk review. | Fix with threat/risk notes, security checks, and approval trail. |
| UC-007 | Run long-running development | Human engineer | Large feature or project that cannot fit one session. | Structured handoffs, progress state, feature-by-feature delivery, and no context-loss drift. |
| UC-008 | Review an agent change | Reviewer agent or human | Existing diff or PR. | Findings, required changes, risk assessment, and verification gaps. |
| UC-009 | Convert failure into harness improvement | Agent operator | Repeated mistake, avoidable human intervention, or escaped defect. | New or updated rule, doc, check, script, prompt, or workflow. |
| UC-010 | Run entropy maintenance | Maintainer or automation | Scheduled scan or post-merge drift signal. | Cleanup issue or PR with stale docs, dead code, dependency, and architecture drift evidence. |

## 2. Universal Development Workflow

The skill shall use this workflow for most project-development tasks.

| Step | Workflow requirement | State output | Gate |
| --- | --- | --- | --- |
| WF-001 | Intake: capture task, user intent, acceptance criteria, non-goals, constraints, risk level, and required approvals. | `task_intake` | Do not implement until minimum acceptance criteria exist. |
| WF-002 | Harness scan: inspect existing project instructions, command registry, tests, docs, architecture, and known failures. | `harness_assessment` | Missing controls are recorded as gaps, not silently ignored. |
| WF-003 | Context selection: load only relevant memory, docs, files, examples, and prior decisions. | `context_record` | The agent records why each context source is relevant. |
| WF-004 | Plan: produce ordered tasks, files likely touched, verification strategy, open questions, and risk mitigations. | `task_plan` | Ask or escalate if a required decision cannot be inferred safely. |
| WF-005 | Implement: edit through allowed tools, prefer small cohesive changes, and preserve unrelated user work. | `action_trace` | Risky actions follow permission boundaries. |
| WF-006 | Fast feedback: run targeted deterministic checks during work. | `verification_events` | Failed checks trigger failure attribution before repair. |
| WF-007 | Failure attribution: reproduce, describe observed failure, identify likely cause, choose repair, rerun relevant checks. | `failure_attribution_log` | No random patching after an unexplained failure. |
| WF-008 | Runtime or behavior verification: run application, browser, API, logs, traces, screenshots, or metrics when relevant. | `runtime_evidence` | User-visible or integration behavior needs runtime evidence unless impossible. |
| WF-009 | Review loop: run self-review, specialized agent review when available, and human review when required. | `review_log` | Required findings must be resolved or explicitly accepted as residual risk. |
| WF-010 | Evidence report: map acceptance criteria to evidence, commands, outputs, screenshots, traces, and exceptions. | `verification_report` | Completion cannot be claimed without requirement-level evidence. |
| WF-011 | Harness improvement: identify repeated mistakes, missing controls, avoidable interventions, and new docs/checks/scripts needed. | `harness_delta` | Repeated failures create a follow-up control change. |
| WF-012 | Handoff or closeout: update task state, record residual risks, and produce concise user-facing summary. | `handoff_or_closeout` | Long-running tasks must preserve next actions. |

## 3. Bootstrap Repository Harness Workflow

Use when a repository has no explicit harness or when the user asks to prepare a project for autonomous-agent development.

1. Inspect repository structure, language, frameworks, package managers, CI, tests, docs, and current instructions.
2. Identify existing command sources: `package.json`, `Makefile`, CI YAML, task runners, scripts, README, and docs.
3. Produce an H0-H3 maturity assessment.
4. Create or recommend a compact agent entrypoint such as `AGENTS.md` when absent.
5. Create or recommend a command registry with exact commands and working directories.
6. Create or recommend project-memory files for architecture, testing, domain rules, known failures, and quality standards.
7. Create or recommend a task-state and verification-report template.
8. Add or recommend fast checks that are already supported by the stack.
9. Record gaps that need human approval, such as adding dependencies or CI jobs.

Required output:

- `harness_assessment`
- `command_registry`
- `project_memory_index`
- `control_gap_backlog`
- `recommended_next_controls`

## 4. Feature Implementation Workflow

Use for new feature work.

1. Convert the request into acceptance criteria and non-goals.
2. Determine affected product domain, architecture layer, user flows, data contracts, and test levels.
3. Select relevant docs and files.
4. Produce a small-step implementation plan.
5. Add or update tests close to the behavior.
6. Implement the feature.
7. Run fast checks and targeted tests.
8. Run runtime or UI verification when the feature is user-visible.
9. Run review loop.
10. Produce evidence report and residual-risk notes.

Completion requires:

- Each acceptance criterion has evidence.
- Prior behavior remains covered by regression checks or documented risk.
- No unrelated changes are hidden in the diff.
- New public behavior is documented where the project expects it.

## 5. Bug Fix Workflow

Use for defects, regressions, incident follow-ups, and flaky behavior.

1. Capture expected behavior, actual behavior, reproduction source, and severity.
2. Reproduce the bug or document why reproduction is currently impossible.
3. Add a failing test, replay, trace query, screenshot, or reproduction script when practical.
4. Diagnose root cause before modifying behavior.
5. Implement the smallest coherent fix.
6. Run the failing check again and relevant regression checks.
7. Record failure attribution and whether the bug exposes a missing harness control.

The skill shall not treat a bug fix as complete if it only patches symptoms without reproduction or an explicit reason reproduction was impossible.

## 6. Refactor Workflow

Use for behavior-preserving internal change.

1. State the refactor goal and behavior-preservation boundary.
2. Identify architecture rules, module boundaries, dependency direction, and public APIs.
3. Run current tests before large edits when feasible.
4. Prefer mechanical transformations or codemods when available.
5. Keep refactor diffs separate from behavior changes unless explicitly approved.
6. Run tests, type checks, architecture checks, and affected integration checks.
7. Produce a before/after summary and list any behavior changes separately.

Required controls:

- Architecture fitness checks.
- Duplicate or dead-code checks when relevant.
- Review for overengineering and unnecessary abstraction.

## 7. UI And Runtime Workflow

Use when the change affects screens, browser behavior, CLI output, APIs, logs, performance, or runtime integration.

1. Identify observable behavior and target environment.
2. Start the application or service using documented commands.
3. Use browser automation, API clients, logs, traces, screenshots, videos, or metrics as applicable.
4. Capture before/after evidence when fixing regressions or visual defects.
5. Verify responsive states, error states, loading states, and accessibility where relevant.
6. Record runtime evidence in the verification report.

The skill shall prefer direct runtime evidence over static claims when the requested behavior is observable only in a running system.

## 8. Long-Running Development Workflow

Use when work spans multiple sessions, many files, or multiple features.

1. Planner creates a product or technical spec from the user request.
2. Planner decomposes work into a feature list with independent completion checks.
3. Each coding session works one feature or coherent slice at a time.
4. The agent updates task state after every meaningful step.
5. Before context reset or handoff, the agent writes current state, completed work, pending work, decisions, and verification results.
6. The next session starts by reading only the handoff, active task state, project map, and relevant docs.
7. Completion requires an aggregate verification report across all slices.

Required handoff fields:

- Current objective.
- Completed tasks.
- Pending tasks.
- Files changed.
- Commands run and outcomes.
- Decisions made.
- Known risks.
- Next recommended action.

## 9. Review Workflow

Use when reviewing an agent-produced diff or PR.

1. Read task intake, acceptance criteria, and verification report.
2. Inspect diff scope and unrelated changes.
3. Verify evidence covers requirements.
4. Run or request missing checks when necessary.
5. Review architecture, maintainability, security, product fit, and test quality.
6. Classify findings by severity and required action.
7. Record whether issues indicate a missing harness control.

Review output must lead with findings. If no issues are found, it must state residual risks or test gaps.

## 10. Harness Improvement Workflow

Use after repeated mistakes, avoidable interventions, recurring review findings, escaped defects, or slow manual verification.

1. Identify the failure pattern.
2. Classify the missing control type: guide, sensor, tool, permission, memory, prompt, state, review, or entropy control.
3. Choose the cheapest durable control that would have prevented or caught the issue.
4. Implement or propose the control.
5. Add evidence that the new control works.
6. Update known failures and control registry.

Examples:

- Wrong test command repeated: update command registry and agent entrypoint.
- Missed UI regression: add browser/screenshot workflow.
- Guessed API shape: add schema docs, type checks, or contract tests.
- Stale docs misled agent: add freshness check or doc owner.
- Repeated overengineering: add review prompt and examples of preferred minimal patterns.

