# Control Layer Requirements

Research date: 2026-06-15

## 1. Control Model

The Harness Development skill shall model the repository as a governed development environment around an autonomous agent. The control model has three axes:

- Timing: feedforward controls before action and feedback controls after action.
- Execution type: computational controls and inferential controls.
- Governance target: intent, context, tools, permissions, verification, observability, review, entropy, and human judgment.

## 2. Control Layers

| ID | Layer | Purpose | Required controls |
| --- | --- | --- | --- |
| CTRL-001 | Intent and acceptance | Define what the work must achieve. | Task brief, acceptance criteria, non-goals, risk level, definition of done. |
| CTRL-002 | Project memory | Give the agent durable project knowledge. | Agent entrypoint, architecture docs, testing guide, domain glossary, known failures, decisions. |
| CTRL-003 | Task state | Keep work coherent across time. | Active plan, inspected files, open questions, decisions, verification status, handoff. |
| CTRL-004 | Tool surface | Expose safe and useful actions. | Tool registry, command registry, MCP inventory, browser automation, test runners, static analysis. |
| CTRL-005 | Permission boundary | Bound autonomous action. | Always/Ask First/Never policy, sandbox, credentials policy, destructive-command policy. |
| CTRL-006 | Fast verification | Catch objective failures early. | Unit tests, lint, type checks, format, build, architecture checks, dependency checks. |
| CTRL-007 | Runtime observability | Verify behavior in running systems. | Logs, traces, metrics, screenshots, videos, DOM snapshots, API probes. |
| CTRL-008 | Inferential review | Catch semantic and judgment-heavy issues. | Self-review, specialized review agents, LLM-as-judge, product review, architecture review. |
| CTRL-009 | Evidence and audit | Make completion reviewable. | Verification report, trace package, failure attribution, intervention log, residual-risk log. |
| CTRL-010 | Entropy management | Prevent long-term quality decay. | Stale-doc scans, dead-code checks, dependency audits, architecture drift checks, cleanup backlog. |

## 3. Feedforward Controls

Feedforward controls steer the agent before it acts.

| ID | Control | Requirement |
| --- | --- | --- |
| CTRL-011 | Agent entrypoint | The skill shall prefer a compact agent entrypoint that maps the project, safe commands, docs, and boundaries. |
| CTRL-012 | Specification | The skill shall require a task spec or acceptance criteria before implementation. |
| CTRL-013 | Architecture guide | The skill shall load architecture rules relevant to touched modules. |
| CTRL-014 | Testing guide | The skill shall load test conventions, fixture rules, and exact test commands before adding or changing tests. |
| CTRL-015 | Command registry | The skill shall provide exact commands with working directory, purpose, cost, risk, and expected outputs. |
| CTRL-016 | Known failures | The skill shall expose repeated agent mistakes and local anti-patterns before work begins. |
| CTRL-017 | Examples | The skill shall use local examples of preferred patterns when they are more reliable than prose rules. |
| CTRL-018 | Permission policy | The skill shall state allowed, approval-required, and forbidden actions before tool use. |

## 4. Feedback Controls

Feedback controls inspect agent work after action and feed correction back into the loop.

| ID | Control | Requirement |
| --- | --- | --- |
| CTRL-019 | Targeted tests | The skill shall run tests closest to the changed behavior first. |
| CTRL-020 | Broader regression checks | The skill shall escalate to broader suites as risk and touched surface increase. |
| CTRL-021 | Static checks | The skill shall run type, lint, format, dependency, and architecture checks when available. |
| CTRL-022 | Runtime checks | The skill shall gather runtime evidence for UI, API, integration, performance, and observability changes. |
| CTRL-023 | Security checks | The skill shall run secrets, dependency, SAST, permission, and threat-model checks for security-sensitive changes. |
| CTRL-024 | Review agents | The skill shall request specialized review for architecture, security, product fit, test quality, or UI when deterministic checks are insufficient. |
| CTRL-025 | Human review | The skill shall escalate ambiguous requirements, irreversible actions, and risk tradeoffs to a human. |
| CTRL-026 | Entropy checks | The skill shall check for stale docs, dead code, duplicate helpers, dependency churn, and residue after substantial changes. |

## 5. Computational Versus Inferential Controls

| ID | Rule | Requirement |
| --- | --- | --- |
| CTRL-027 | Prefer deterministic checks | Use computational controls when they can cheaply and reliably express the requirement. |
| CTRL-028 | Use inferential controls for judgment | Use model-based review when quality depends on semantics, product fit, architecture tradeoffs, or test meaning. |
| CTRL-029 | Do not overuse judges | Do not replace deterministic tests with LLM review when a clear executable check is practical. |
| CTRL-030 | Treat inferential output as review input | Inferential findings require agent or human judgment and should not silently override explicit tests or requirements. |
| CTRL-031 | Make feedback LLM-readable | When writing custom checks, produce concise error messages that state what failed and how to investigate. |

## 6. Permission Boundaries

The skill shall use a three-tier permission model.

### Always Allowed When Relevant

- Read repository files.
- Search code and docs.
- Inspect Git status and diffs.
- Run documented safe commands.
- Add or update tests within the task scope.
- Create local-only evidence artifacts.
- Update task state and verification reports.

### Ask First

- Add or upgrade dependencies.
- Change CI configuration.
- Modify database schema or migrations.
- Run expensive, destructive, networked, or long-running commands.
- Access credentials, secrets, private production data, or external systems.
- Change public APIs or backward compatibility contracts.
- Push branches, create PRs, merge, deploy, publish packages, or tag releases.
- Delete files that are not clearly generated or obsolete within the task scope.

### Never Without Explicit Override

- Commit secrets or sensitive data.
- Disable or delete failing tests to make checks pass.
- Rewrite unrelated user changes.
- Run destructive filesystem or database commands outside an approved sandbox.
- Fabricate test, log, screenshot, or trace evidence.
- Claim production verification when only local verification occurred.

## 7. Failure Mode Mapping

| Failure mode | Primary control | Secondary control |
| --- | --- | --- |
| Misunderstood task | Acceptance criteria | Human clarification gate |
| Wrong layer edited | Architecture guide | Module-boundary check |
| Wrong command used | Command registry | Agent entrypoint |
| Guessed API shape | Contract docs | Type/schema tests |
| Premature completion | Verification report | Review gate |
| Random patching | Failure attribution | Reproduction protocol |
| Shallow tests | Testing guide | Test-quality review |
| Overengineering | Product/architecture review | Simplicity examples |
| Hidden UI regression | Browser verification | Screenshot comparison |
| Security regression | Security checks | Human security review |
| Stale docs | Doc freshness scan | Doc ownership |
| Context drift | Task state | Handoff protocol |
| Long-running incoherence | Feature decomposition | Context reset/compaction protocol |

## 8. Control Improvement Rule

When the agent or reviewer observes the same failure mode more than once, the skill shall require one of these durable responses:

- Add or clarify a feedforward guide.
- Add or tighten a feedback sensor.
- Add a deterministic script or command.
- Add an example or fixture.
- Update known failures.
- Add a permission rule.
- Add a review prompt.
- Add an entropy or freshness check.

The skill shall record if no durable control is added and why.

