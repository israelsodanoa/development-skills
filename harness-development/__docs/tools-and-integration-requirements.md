# Tools And Integration Requirements

Research date: 2026-06-15

## 1. Tooling Philosophy

The skill shall make tools legible and safe for autonomous agents. A tool is part of the harness only when the agent knows when to use it, how to invoke it, what output means, what risks it carries, and how it contributes to evidence.

## 2. Codex Skill Packaging Requirements

| ID | Requirement |
| --- | --- |
| TOOL-001 | The implemented skill shall have a directory name using lowercase letters, digits, and hyphens only. |
| TOOL-002 | The implemented skill shall include a required `SKILL.md`. |
| TOOL-003 | `SKILL.md` frontmatter shall include only `name` and `description`. |
| TOOL-004 | The `description` shall front-load trigger contexts: harness engineering, project development management, autonomous coding workflows, agent controls, verification, project memory, and harness improvement. |
| TOOL-005 | `SKILL.md` body shall remain concise and procedural. |
| TOOL-006 | Detailed workflows and schemas shall live in `references/` and be loaded only when relevant. |
| TOOL-007 | Deterministic repeated operations shall be implemented as scripts when practical. |
| TOOL-008 | `agents/openai.yaml` should be generated or updated to match the final skill. |
| TOOL-009 | The skill shall be validated with the platform validation script after implementation. |
| TOOL-010 | Placeholder example files shall be deleted before release. |

## 3. Command Registry Requirements

The skill shall require a project-level command registry. The registry may be a Markdown file, YAML file, JSON file, or section in an existing project instruction file.

Required fields:

```yaml
commands:
  - id: test.unit
    command: npm test -- --runInBand
    workdir: .
    purpose: Run unit tests
    when_to_run: After changing application logic
    expected_runtime: medium
    risk: safe
    required_before_completion: true
    success_signal: exit code 0
    failure_protocol: Run failure attribution before repair
```

| ID | Requirement |
| --- | --- |
| TOOL-011 | Each command shall include exact executable text and working directory. |
| TOOL-012 | Each command shall include purpose, when to run, expected runtime, risk, and success signal. |
| TOOL-013 | Commands that mutate state, use credentials, deploy, publish, or access production shall be marked approval-required. |
| TOOL-014 | Missing command registry entries shall be recorded as harness gaps. |
| TOOL-015 | The agent shall prefer registered commands over guessed commands. |

## 4. Required Tool Categories

| ID | Category | Examples | Harness use |
| --- | --- | --- | --- |
| TOOL-016 | Code discovery | `rg`, file tree, language servers, dependency graph tools. | Find relevant code and avoid wrong-layer edits. |
| TOOL-017 | Version control | `git status`, `git diff`, branches, PR tools. | Preserve user work and make changes reviewable. |
| TOOL-018 | Build and package | Project build commands, package managers. | Verify structural integrity. |
| TOOL-019 | Testing | Unit, integration, E2E, contract, mutation, snapshot tests. | Verify behavior and regressions. |
| TOOL-020 | Static analysis | Type checks, lint, format, architecture checks, Semgrep. | Catch fast deterministic issues. |
| TOOL-021 | Runtime verification | Local server, API clients, browser automation, screenshots, logs, traces, metrics. | Prove running behavior. |
| TOOL-022 | Security | Secrets scan, dependency audit, SAST, permission checks. | Bound security risk. |
| TOOL-023 | Documentation | Markdown lint, link checker, docs freshness scanner. | Prevent stale project memory. |
| TOOL-024 | Observability | Trace query tools, log search, metrics dashboards, replay tools. | Diagnose runtime behavior and verify fixes. |
| TOOL-025 | Agent review | Specialized reviewer agents or prompts. | Catch semantic gaps. |

## 5. MCP Integration Requirements

| ID | Requirement |
| --- | --- |
| TOOL-026 | The skill shall discover available MCP servers and tools before assuming integrations exist. |
| TOOL-027 | MCP tools shall be treated like any other tool: purpose, input constraints, permission risk, output interpretation, and evidence value must be clear. |
| TOOL-028 | Browser, issue tracker, CI, observability, database, and cloud tools shall require project-specific permission boundaries. |
| TOOL-029 | MCP outputs used as evidence shall be recorded in the verification report or episode trace. |
| TOOL-030 | The skill shall define fallback behavior when a desired MCP tool is missing. |

## 6. Script Requirements

The implemented skill may include scripts for deterministic harness operations.

Recommended scripts:

| ID | Script | Purpose |
| --- | --- | --- |
| TOOL-031 | `validate_harness_state.py` | Validate required task-state fields and schema. |
| TOOL-032 | `render_verification_report.py` | Generate a verification report from state and command logs. |
| TOOL-033 | `audit_docs_freshness.py` | Check project-memory links, owners, and stale references. |
| TOOL-034 | `summarize_episode.py` | Convert trace logs into an auditable episode summary. |
| TOOL-035 | `check_command_registry.py` | Validate command registry fields and risky-command labels. |

Script acceptance requirements:

- Scripts must be executable with documented commands.
- Scripts must not require network access unless explicitly documented.
- Scripts must fail closed on malformed input.
- Scripts must produce LLM-readable output.
- Representative scripts must be run during implementation validation.

## 7. Repository Harness Artifacts

The skill shall be able to create or update these artifacts when appropriate and approved:

| ID | Artifact | Purpose |
| --- | --- | --- |
| TOOL-036 | Agent entrypoint | Compact guide for agents entering the repo. |
| TOOL-037 | Command registry | Safe commands and exact invocation rules. |
| TOOL-038 | Project memory index | Map to architecture, testing, domain, and tool docs. |
| TOOL-039 | Task-state file | Active work state and handoff. |
| TOOL-040 | Verification template | Criteria-to-evidence report. |
| TOOL-041 | Known-failures log | Repeated mistakes and local anti-patterns. |
| TOOL-042 | Control gap backlog | Missing guides, sensors, tools, permissions, or memory. |
| TOOL-043 | Entropy report | Stale docs, residue, dead code, dependency churn, drift. |

The skill should adapt artifact names to existing repository conventions. If no convention exists, `.harness/` or `docs/exec-plans/` are acceptable candidates, subject to user approval.

## 8. Tool Use Protocol

| ID | Requirement |
| --- | --- |
| TOOL-044 | Before running a command, state its purpose and whether it is registered. |
| TOOL-045 | After running a command, record result, failure summary, and next action. |
| TOOL-046 | If a command fails, run failure attribution before editing again unless the failure is trivial and obvious. |
| TOOL-047 | Do not run approval-required tools without approval. |
| TOOL-048 | Do not use tool output as proof beyond its actual scope. |
| TOOL-049 | Prefer narrow, relevant checks during iteration and broader checks before completion. |
| TOOL-050 | Preserve raw evidence where useful: logs, screenshots, traces, command output, or report paths. |

## 9. Integration With Project Lifecycle

| ID | Lifecycle point | Requirement |
| --- | --- | --- |
| TOOL-051 | Pre-development | Verify command registry and project memory are sufficient for the task. |
| TOOL-052 | In-session | Run fast checks and update task state after meaningful changes. |
| TOOL-053 | Pre-review | Generate verification report and self-review. |
| TOOL-054 | Review | Provide reviewers with diff, evidence, risks, and unresolved checks. |
| TOOL-055 | Post-review | Apply feedback, rerun targeted checks, and update evidence. |
| TOOL-056 | Post-merge | Record escaped issues and entropy signals as harness improvement inputs. |

