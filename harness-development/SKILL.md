---
name: harness-development
description: Harness engineering for project development management, autonomous coding workflows, spec-driven implementation, repository harness setup, agent controls, project memory, Sonar quality gates, task handoffs, verification evidence, and durable harness improvement. Use when Codex needs to bootstrap or operate a reproducible `.harness` folder, run governed implementation work, coordinate specialist agents, persist specs/plans/tasks/state/history, or audit autonomous-agent development quality.
---

# Harness Development

## Operating Rule

Use a repository-local `.harness/` folder as the durable source of truth for every implementation request. Do not rely on hidden conversation history for requirements, approvals, decisions, handoffs, command evidence, or verification status.

The common engine lives in this skill's `scripts/` directory. Target projects receive persistent `.harness/` artifacts only; never create `.harness/scripts/`.

## Start Here

1. Bootstrap or refresh the target repository harness:

```bash
python3 /path/to/harness-development/scripts/init_project_harness.py --target /path/to/project
```

2. Create a draft request before implementation:

```bash
python3 /path/to/harness-development/scripts/request_engine.py create --target /path/to/project --title "short task title" --objective "user-visible objective"
```

3. Run the intake interview and complete intake before spec approval:

```bash
python3 /path/to/harness-development/scripts/intake_engine.py questions --target /path/to/project --request-id <request_id>
python3 /path/to/harness-development/scripts/intake_engine.py record --target /path/to/project --request-id <request_id> --field success_criteria --answer "testable criteria"
python3 /path/to/harness-development/scripts/intake_engine.py complete --target /path/to/project --request-id <request_id>
```

4. Run the gated workflow for every implementation request:

```text
SPECIFY -> PLAN -> TASKS -> IMPLEMENT -> VERIFY -> CLOSEOUT
```

Each phase must update `.harness/requests/<request_id>/state.json` and append meaningful events to `.harness/requests/<request_id>/history.jsonl`.

## Required Workflow

- Persist `intake.md` first. Use an adaptive interview to capture objective, task type, audience, desired outcome, success criteria, non-goals, constraints, permissions, verification expectations, assumptions, waivers, and blocking open questions.
- Complete intake before approving `spec.md` or entering PLAN.
- Persist `spec.md` after intake. Include objective, stack, commands, project structure, code style, testing strategy, boundaries, success criteria, assumptions, and open questions.
- Validate and approve the spec gate before creating `plan.md`.
- Validate and approve the strict research-backed plan gate before creating `tasks.md`. The plan must include WBS decomposition, dependency graph, implementation slices, decision records, verification matrix, premortem risks, complexity classification, sequencing rationale, and parallelization boundaries.
- Validate and approve the strict task gate before implementation. Every task must be atomic, XS/S-sized, dependency-explicit, independently verifiable, and include exact scope, non-scope, acceptance, scenario, files, risk notes, rollback/repair, and parallelization label.
- Record commands, failures, repairs, approvals, handoffs, and verification events as history.
- Generate `verification-report.md` before claiming completion.
- Summarize substantial work with `episode_engine.py`.

Small fixes still use this workflow with concise specs and tasks. Shorten the artifacts; do not skip the gates.

## Scripts

Use the Python scripts in `scripts/` as the reproducible engine. Run them from the skill package against a target project with `--target /path/to/project`. Prefer absolute target paths for long-running or multi-session work.

### `init_project_harness.py`

Install or update the persistent `.harness/` scaffold in a target repository.

Optimal usage:

```bash
python3 scripts/init_project_harness.py --target /path/to/project
```

Use this first for any repository that does not already have `.harness/`. By default, init configures Docker-based SonarQube, starts the `sonarqube` service, and waits until `/api/system/status` reports `UP`. Use `--force` only when intentionally replacing scaffold-managed templates. Use `--skip-sonar` only when the project should bypass SonarQube startup and record Sonar as skipped.

Outputs: `.harness/config/`, `.harness/memory/`, `.harness/sonar/`, `.harness/requests/`, `.harness/reports/`. It also records the skill `scripts/` path in `.harness/config/harness.json` and Sonar runtime status in `.harness/sonar/sonar-config.json`.

### `request_engine.py`

Create and inspect per-request harness folders.

Optimal usage:

```bash
python3 scripts/request_engine.py create --target /path/to/project --title "short task title" --objective "user-visible objective"
python3 scripts/request_engine.py show --target /path/to/project --request-id <request_id>
```

Use this before writing a spec for any implementation request. The generated request ID becomes the stable key for every later command.

Outputs: `.harness/requests/<request_id>/state.json`, `intake.md`, `history.jsonl`, `handoffs/`, `prompt-packets/`, and `evidence/`.

### `intake_engine.py`

Create, run, validate, and complete the request intake interview.

Optimal usage:

```bash
python3 scripts/intake_engine.py create --target /path/to/project --request-id <request_id>
python3 scripts/intake_engine.py questions --target /path/to/project --request-id <request_id>
python3 scripts/intake_engine.py record --target /path/to/project --request-id <request_id> --field objective --answer "specific outcome"
python3 scripts/intake_engine.py record --target /path/to/project --request-id <request_id> --field non_goals --waive --reason "No exclusions"
python3 scripts/intake_engine.py validate --target /path/to/project --request-id <request_id>
python3 scripts/intake_engine.py complete --target /path/to/project --request-id <request_id>
python3 scripts/intake_engine.py interview --target /path/to/project --request-id <request_id> --complete
```

Use this immediately after request creation. The first question batch covers objective, task type, audience, desired outcome, success criteria, non-goals, constraints, permissions, and verification expectations. Follow-up batches adapt to feature, bug, refactor, UI/runtime, security/reliability, review, maintenance, harness-improvement, and risk-heavy work.

Outputs: `.harness/requests/<request_id>/intake.md`, `state.json` intake metadata, top-level acceptance criteria/non-goals/permissions/risk fields when recorded, and intake history events.

### `spec_engine.py`

Create, validate, and approve `spec.md`.

Optimal usage:

```bash
python3 scripts/spec_engine.py create --target /path/to/project --request-id <request_id>
python3 scripts/spec_engine.py validate --target /path/to/project --request-id <request_id>
python3 scripts/spec_engine.py approve --target /path/to/project --request-id <request_id>
```

Use it during `SPECIFY`. Fill the generated spec with objective, tech stack, commands, project structure, code style, testing strategy, boundaries, success criteria, and open questions before approval. `approve` fails until intake is complete. Do not create `plan.md` until this gate is approved.

Outputs: `.harness/requests/<request_id>/spec.md`, approval state, and history events.

### `plan_engine.py`

Create, validate, and approve `plan.md` after the spec gate passes.

Optimal usage:

```bash
python3 scripts/plan_engine.py create --target /path/to/project --request-id <request_id>
python3 scripts/plan_engine.py validate --target /path/to/project --request-id <request_id>
python3 scripts/plan_engine.py approve --target /path/to/project --request-id <request_id>
```

Use it during `PLAN`. The plan must apply WBS, INVEST, SMART, ADR, RAPID, Cynefin, Gherkin, and premortem thinking. `validate` reports missing sections and `quality_problems`; `approve` fails until the strict plan contract passes and records `planning_quality.plan` in state. Do not create `tasks.md` until this gate is approved.

Outputs: `.harness/requests/<request_id>/plan.md`, approval state, `planning_quality.plan`, and history events.

### `task_engine.py`

Create, validate, and approve `tasks.md` after the plan gate passes.

Optimal usage:

```bash
python3 scripts/task_engine.py create --target /path/to/project --request-id <request_id>
python3 scripts/task_engine.py validate --target /path/to/project --request-id <request_id>
python3 scripts/task_engine.py approve --target /path/to/project --request-id <request_id>
```

Use it during `TASKS`. Each task must be an atomic XS/S work item with task ID, outcome, exact scope, non-scope, acceptance, Gherkin-style scenario when applicable, verification command/evidence, dependencies, likely files, risk notes, rollback/repair, and parallelization label. `validate` reports missing markers and per-task `quality_problems`; `approve` fails until all tasks pass and records `planning_quality.tasks` in state. Do not enter implementation until this gate is approved.

Outputs: `.harness/requests/<request_id>/tasks.md`, approval state, `planning_quality.tasks`, and history events.

### `harness_state.py`

Show, validate, approve, and transition request state.

Optimal usage:

```bash
python3 scripts/harness_state.py validate --target /path/to/project --request-id <request_id>
python3 scripts/harness_state.py transition --target /path/to/project --request-id <request_id> --to PLAN
python3 scripts/harness_state.py transition --target /path/to/project --request-id <request_id> --to IMPLEMENT
```

Use it whenever moving through `SPECIFY -> PLAN -> TASKS -> IMPLEMENT -> VERIFY -> CLOSEOUT`. It blocks skipped phases, gated phases when the prior artifact is missing, invalid, or unapproved, and closeout when registry commands marked `required_before_completion` have not succeeded.

Outputs: updated `state.json` and `state.transition` history events.

### `history_engine.py`

Append and query durable request events.

Optimal usage:

```bash
python3 scripts/history_engine.py append --target /path/to/project --request-id <request_id> --type decision --summary "Chose the existing API boundary"
python3 scripts/history_engine.py list --target /path/to/project --request-id <request_id>
```

Use it after meaningful decisions, assumptions, user approvals, failures, interventions, handoffs, and verification events that another agent must be able to reconstruct.

Outputs: `.harness/requests/<request_id>/history.jsonl`.

### `memory_engine.py`

Maintain project memory, known failures, and control gaps.

Optimal usage:

```bash
python3 scripts/memory_engine.py show --target /path/to/project --artifact index
python3 scripts/memory_engine.py add-source --target /path/to/project --section testing --path docs/testing.md --reason "Nearest test conventions"
python3 scripts/memory_engine.py add-gap --target /path/to/project --type command-registry --summary "No integration test command registered"
python3 scripts/memory_engine.py add-known-failure --target /path/to/project --summary "Agents repeatedly edit the wrong service layer"
```

Use it when context, controls, or durable project knowledge change. Record repeated failures as known failures or control gaps before closeout.

Outputs: `.harness/memory/memory-index.json`, `known-failures.json`, and `control-gaps.json`.

### `command_engine.py`

Validate and run registered commands with evidence capture.

Optimal usage:

```bash
python3 scripts/command_engine.py validate --target /path/to/project
python3 scripts/command_engine.py run --target /path/to/project --request-id <request_id> --id test.unit
python3 scripts/command_engine.py run --target /path/to/project --request-id <request_id> --id quality.sonar.run --approved
```

Use registered commands instead of guessed shell commands whenever possible. Pass `--approved` only after approval-required command execution has been approved and recorded. Run `quality.sonar.run` through this engine before closeout so the required command evidence is written to request state.

Outputs: command evidence logs under `.harness/requests/<request_id>/evidence/commands/`, `commands_run` state entries, and command history events.

### `sonar_engine.py`

Detect the target stack, configure Docker-based SonarQube, manage the local SonarQube runtime, and run approved Sonar scans.

Optimal usage:

```bash
python3 scripts/sonar_engine.py detect --target /path/to/project
python3 scripts/sonar_engine.py configure --target /path/to/project
python3 scripts/sonar_engine.py up --target /path/to/project --approved
python3 scripts/sonar_engine.py status --target /path/to/project
python3 scripts/sonar_engine.py run --target /path/to/project --request-id <request_id> --approved
python3 scripts/sonar_engine.py down --target /path/to/project --approved
```

Use `configure` during bootstrap and whenever the project stack changes. Use `up` to start SonarQube and wait for the system API to report `UP`; `init_project_harness.py` does this by default. Use `status` before scans or after runtime changes. Use `run` for a self-contained local scan: it configures missing Sonar files, starts the local Docker service if needed, uses default local admin credentials to bootstrap anonymous local scan permissions and the project when needed, and runs the scanner with quality-gate waiting enabled. Do not create or export `SONAR_TOKEN`; the local Docker server disables forced authentication for anonymous local analysis and stores no scanner credentials.

Outputs: `.harness/sonar/docker-compose.sonar.yml`, `.harness/sonar/sonar-project.properties`, `.harness/sonar/.env.example`, `.harness/sonar/sonar-config.json`, optional Sonar evidence logs, and quality history events.

### `prompt_engine.py`

Generate phase-specific prompt packets.

Optimal usage:

```bash
python3 scripts/prompt_engine.py --target /path/to/project --request-id <request_id> --phase specify --write
python3 scripts/prompt_engine.py --target /path/to/project --request-id <request_id> --phase review --print
```

Use prompt packets when handing work to another agent, restarting after compaction, or narrowing context for a specific phase. Available phases: `intake`, `specify`, `plan`, `tasks`, `implement`, `failure`, `review`, `verify`, `improve`, and `handoff`.

Outputs: `.harness/requests/<request_id>/prompt-packets/<phase>.md` when `--write` is used.

### `handoff_engine.py`

Create specialist-agent or continuation handoff packets.

Optimal usage:

```bash
python3 scripts/handoff_engine.py --target /path/to/project --request-id <request_id> --specialist security --pending "Review auth boundary" --risk "Token handling changed"
python3 scripts/handoff_engine.py --target /path/to/project --request-id <request_id> --specialist continuation --completed "Spec and plan approved" --next-action "Implement Task 1"
```

Use it before context reset, user interruption, cross-agent review, or specialist delegation. Supported specialists: `architecture`, `security`, `test`, `ui`, `product`, `release`, and `continuation`.

Outputs: `.harness/requests/<request_id>/handoffs/*.md` and handoff history events.

### `verification_engine.py`

Render requirement-level verification reports.

Optimal usage:

```bash
python3 scripts/verification_engine.py --target /path/to/project --request-id <request_id>
```

Use it during `VERIFY`, after acceptance criteria and command evidence have been recorded in state/history. Review the generated report before closeout; do not claim completion if required criteria remain failed, blocked, or unverified.

Outputs: `.harness/requests/<request_id>/verification-report.md`.

### `episode_engine.py`

Summarize request history into an auditable episode report.

Optimal usage:

```bash
python3 scripts/episode_engine.py --target /path/to/project --request-id <request_id>
```

Use it for substantial tasks, long-running work, reviews, or closeout audits. It summarizes event counts, approvals, decisions, command evidence, and final outcome.

Outputs: `.harness/requests/<request_id>/episode-summary.md` unless `--output` is supplied.

### `docs_freshness.py`

Audit project-memory links, owners, and freshness hints.

Optimal usage:

```bash
python3 scripts/docs_freshness.py --target /path/to/project
```

Use it during harness bootstrap, substantial changes, and maintenance work to detect stale or incomplete memory references. Treat findings as control gaps when they could mislead future agents.

Outputs: `.harness/reports/docs-freshness.json` unless `--output` is supplied.

### `harness_common.py`

Shared library for the engine scripts. Do not invoke it directly. Read or modify it only when changing common behavior such as state paths, JSON handling, scaffold copying, stack detection, Sonar template rendering, command execution, or registry validation.

## References

Load only the reference needed for the current activity:

- `references/scaffolding.md`: `.harness/` layout and non-destructive update rules.
- `references/workflows.md`: universal, feature, bug, refactor, UI, review, and long-running flows.
- `references/controls.md`: feedforward, feedback, permission, review, and entropy controls.
- `references/state-memory.md`: task state, project memory, context selection, and handoff rules.
- `references/prompting.md`: prompt packet requirements for each phase.
- `references/planning-task-breakdown.md`: research-backed plan/task quality gates, framework mapping, and atomic task contract.
- `references/tools.md`: command registry, tool use, MCP, and evidence capture rules.
- `references/sonar.md`: Docker-based Sonar template and execution policy.
- `references/evaluation.md`: definition of done, verification reports, episode traces, and metrics.

## Completion Discipline

Do not claim completion unless each required acceptance criterion has evidence, required commands are run or explicitly waived, failed checks have attribution and follow-up, approval-required actions are recorded, and residual risks are disclosed.
