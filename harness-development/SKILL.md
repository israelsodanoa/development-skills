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

2. Create a request before implementation:

```bash
python3 /path/to/harness-development/scripts/request_engine.py create --target /path/to/project --title "short task title" --objective "user-visible objective"
```

3. Run the gated workflow for every implementation request:

```text
SPECIFY -> PLAN -> TASKS -> IMPLEMENT -> VERIFY -> CLOSEOUT
```

Each phase must update `.harness/requests/<request_id>/state.json` and append meaningful events to `.harness/requests/<request_id>/history.jsonl`.

## Required Workflow

- Persist `spec.md` first. Include objective, stack, commands, project structure, code style, testing strategy, boundaries, success criteria, assumptions, and open questions.
- Validate and approve the spec gate before creating `plan.md`.
- Validate and approve the plan gate before creating `tasks.md`.
- Validate and approve the tasks gate before implementation.
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

Use this first for any repository that does not already have `.harness/`. Use `--force` only when intentionally replacing scaffold-managed templates. Use `--skip-sonar` when the project should not receive Sonar templates yet.

Outputs: `.harness/config/`, `.harness/memory/`, `.harness/sonar/`, `.harness/requests/`, `.harness/reports/`. It also records the skill `scripts/` path in `.harness/config/harness.json`.

### `request_engine.py`

Create and inspect per-request harness folders.

Optimal usage:

```bash
python3 scripts/request_engine.py create --target /path/to/project --title "short task title" --objective "user-visible objective"
python3 scripts/request_engine.py show --target /path/to/project --request-id <request_id>
```

Use this before writing a spec for any implementation request. The generated request ID becomes the stable key for every later command.

Outputs: `.harness/requests/<request_id>/state.json`, `history.jsonl`, `handoffs/`, `prompt-packets/`, and `evidence/`.

### `spec_engine.py`

Create, validate, and approve `spec.md`.

Optimal usage:

```bash
python3 scripts/spec_engine.py create --target /path/to/project --request-id <request_id>
python3 scripts/spec_engine.py validate --target /path/to/project --request-id <request_id>
python3 scripts/spec_engine.py approve --target /path/to/project --request-id <request_id>
```

Use it during `SPECIFY`. Fill the generated spec with objective, tech stack, commands, project structure, code style, testing strategy, boundaries, success criteria, and open questions before approval. Do not create `plan.md` until this gate is approved.

Outputs: `.harness/requests/<request_id>/spec.md`, approval state, and history events.

### `plan_engine.py`

Create, validate, and approve `plan.md` after the spec gate passes.

Optimal usage:

```bash
python3 scripts/plan_engine.py create --target /path/to/project --request-id <request_id>
python3 scripts/plan_engine.py validate --target /path/to/project --request-id <request_id>
python3 scripts/plan_engine.py approve --target /path/to/project --request-id <request_id>
```

Use it during `PLAN`. The plan should describe implementation strategy, verification strategy, risks, and unresolved questions. Do not create `tasks.md` until this gate is approved.

Outputs: `.harness/requests/<request_id>/plan.md`, approval state, and history events.

### `task_engine.py`

Create, validate, and approve `tasks.md` after the plan gate passes.

Optimal usage:

```bash
python3 scripts/task_engine.py create --target /path/to/project --request-id <request_id>
python3 scripts/task_engine.py validate --target /path/to/project --request-id <request_id>
python3 scripts/task_engine.py approve --target /path/to/project --request-id <request_id>
```

Use it during `TASKS`. Each task must include acceptance, verification, dependencies, and likely files. Do not enter implementation until this gate is approved.

Outputs: `.harness/requests/<request_id>/tasks.md`, approval state, and history events.

### `harness_state.py`

Show, validate, approve, and transition request state.

Optimal usage:

```bash
python3 scripts/harness_state.py validate --target /path/to/project --request-id <request_id>
python3 scripts/harness_state.py transition --target /path/to/project --request-id <request_id> --to PLAN
python3 scripts/harness_state.py transition --target /path/to/project --request-id <request_id> --to IMPLEMENT
```

Use it whenever moving through `SPECIFY -> PLAN -> TASKS -> IMPLEMENT -> VERIFY -> CLOSEOUT`. It blocks skipped phases and blocks gated phases when the prior artifact is missing, invalid, or unapproved.

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

Use registered commands instead of guessed shell commands whenever possible. Pass `--approved` only after approval-required command execution has been approved and recorded.

Outputs: command evidence logs under `.harness/requests/<request_id>/evidence/commands/`, `commands_run` state entries, and command history events.

### `sonar_engine.py`

Detect the target stack, generate Docker-based Sonar templates, and run approved Sonar workflows.

Optimal usage:

```bash
python3 scripts/sonar_engine.py detect --target /path/to/project
python3 scripts/sonar_engine.py generate --target /path/to/project
python3 scripts/sonar_engine.py run --target /path/to/project --request-id <request_id> --approved
```

Use `detect` or `generate` during bootstrap and whenever the project stack changes. Use `run` only when Docker execution is approved, Docker is available, and the required Sonar environment variables are set. Store credentials only in environment variables.

Outputs: `.harness/sonar/docker-compose.sonar.yml`, `.harness/sonar/sonar-project.properties`, optional Sonar evidence logs, and quality history events.

### `prompt_engine.py`

Generate phase-specific prompt packets.

Optimal usage:

```bash
python3 scripts/prompt_engine.py --target /path/to/project --request-id <request_id> --phase specify --write
python3 scripts/prompt_engine.py --target /path/to/project --request-id <request_id> --phase review --print
```

Use prompt packets when handing work to another agent, restarting after compaction, or narrowing context for a specific phase. Available phases: `specify`, `plan`, `tasks`, `implement`, `failure`, `review`, `verify`, `improve`, and `handoff`.

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
- `references/tools.md`: command registry, tool use, MCP, and evidence capture rules.
- `references/sonar.md`: Docker-based Sonar template and execution policy.
- `references/evaluation.md`: definition of done, verification reports, episode traces, and metrics.

## Completion Discipline

Do not claim completion unless each required acceptance criterion has evidence, required commands are run or explicitly waived, failed checks have attribution and follow-up, approval-required actions are recorded, and residual risks are disclosed.
