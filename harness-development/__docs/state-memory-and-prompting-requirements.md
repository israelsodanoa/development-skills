# State, Memory, And Prompting Requirements

Research date: 2026-06-15

## 1. State And Memory Philosophy

The skill shall distinguish between task state and project memory.

- Task state is current, temporary, and tied to one episode of work.
- Project memory is durable, maintained, and reused across many episodes.

The skill shall avoid relying on hidden conversation history as the source of truth. If information matters for future work, it must be recorded in a repository artifact or in the final verification report.

## 2. Task State Requirements

| ID | Field | Requirement |
| --- | --- | --- |
| SM-001 | `task_id` | Stable identifier for the active work item when available. |
| SM-002 | `objective` | User-visible statement of what the agent is trying to accomplish. |
| SM-003 | `acceptance_criteria` | Testable criteria, each with an ID. |
| SM-004 | `non_goals` | Explicitly excluded work. |
| SM-005 | `risk_level` | Low, medium, high, or critical with reason. |
| SM-006 | `permissions` | Allowed, approval-required, and forbidden actions for this task. |
| SM-007 | `context_sources` | Files, docs, issues, logs, traces, and examples loaded, with reason. |
| SM-008 | `plan` | Ordered tasks and verification checkpoints. |
| SM-009 | `inspected_files` | Files read or inspected and why. |
| SM-010 | `changed_files` | Files edited and why. |
| SM-011 | `decisions` | Decisions made, by whom or by which evidence. |
| SM-012 | `assumptions` | Assumptions that affect implementation or verification. |
| SM-013 | `open_questions` | Questions that block or materially affect quality. |
| SM-014 | `commands_run` | Command, working directory, purpose, outcome, and next action. |
| SM-015 | `verification_status` | Criteria-to-evidence status. |
| SM-016 | `failure_attributions` | Failed checks, likely cause, repair plan, and rerun result. |
| SM-017 | `interventions` | Human help, reason, avoidability, and harness gap. |
| SM-018 | `next_action` | Current next step for continuation or handoff. |

## 3. Project Memory Requirements

| ID | Memory artifact | Requirement |
| --- | --- | --- |
| SM-019 | Project map | Describe major directories, ownership, boundaries, and where to find deeper docs. |
| SM-020 | Architecture memory | Capture layering, dependency direction, module boundaries, public API contracts, data contracts, and integration points. |
| SM-021 | Testing memory | Capture frameworks, commands, fixtures, test levels, coverage expectations, and test anti-patterns. |
| SM-022 | Domain memory | Capture business terms, invariants, user flows, compliance constraints, and edge cases. |
| SM-023 | Tool memory | Capture safe commands, MCP tools, browser workflows, generated artifacts, and setup steps. |
| SM-024 | Known-failure memory | Capture repeated agent mistakes, common local pitfalls, flaky tests, misleading docs, and bad patterns. |
| SM-025 | Decision memory | Capture architecture decisions, product decisions, accepted tradeoffs, and deprecations. |
| SM-026 | Quality memory | Capture quality scores, technical debt, entropy issues, and improvement backlog. |

## 4. Memory Update Rules

| ID | Rule | Requirement |
| --- | --- | --- |
| SM-027 | Update after durable decisions | If a decision changes future behavior, update project memory before closeout. |
| SM-028 | Update after repeated failures | If a failure repeats, update known failures or add a new control. |
| SM-029 | Keep entrypoints short | The agent entrypoint should point to memory, not duplicate it. |
| SM-030 | Prefer structured indexes | Use indexes, owners, freshness status, and links so the agent can choose context. |
| SM-031 | Mark uncertainty | Stale, unverified, or assumed memory must be labeled. |
| SM-032 | Verify memory freshness | Substantial changes should check whether docs still match code. |

## 5. Context Selection Protocol

The skill shall use this protocol before implementation:

1. Identify the task category: feature, bug, refactor, UI, security, maintenance, or harness improvement.
2. Identify affected domains, modules, commands, tests, and risks.
3. Load the compact project map and task-specific memory.
4. Search code and docs for concrete local patterns.
5. Record selected context sources and reason.
6. Avoid loading unrelated large docs.
7. If context is missing, record the gap and continue only if risk is acceptable.

Context selection output:

```yaml
context_record:
  task_category: feature
  selected_sources:
    - path: docs/architecture/payments.md
      reason: owns affected module boundary
    - path: tests/payments/
      reason: nearest regression coverage
  skipped_sources:
    - path: docs/mobile.md
      reason: unrelated platform
  gaps:
    - no contract test guide found
```

## 6. Prompting Strategy Requirements

Prompting in the skill shall be procedural, scoped, and evidence-oriented. It shall not rely on motivational wording or vague quality requests.

| ID | Prompt type | Required inputs | Required outputs |
| --- | --- | --- | --- |
| PR-001 | Intake prompt | User request, repository state, known constraints. | Acceptance criteria, non-goals, risk level, assumptions, open questions. |
| PR-002 | Harness assessment prompt | Repo files, command sources, docs, tests. | H0-H3 level, existing controls, missing controls, recommended next controls. |
| PR-003 | Context selection prompt | Task category, affected area, memory index. | Relevant docs/files, search plan, context gaps. |
| PR-004 | Planning prompt | Acceptance criteria, selected context, risk level. | Ordered plan, verification strategy, files likely touched, approval needs. |
| PR-005 | Implementation prompt | Current plan, permitted tools, relevant files, coding rules. | Small changes, state updates, checks to run. |
| PR-006 | Failure attribution prompt | Failed command/output, changed files, intended behavior. | Reproduction status, likely cause, repair plan, rerun check. |
| PR-007 | Self-review prompt | Diff, task criteria, evidence, local standards. | Findings, gaps, risks, required follow-up. |
| PR-008 | Specialized review prompt | Diff, domain-specific criteria, evidence. | Architecture/security/product/test/UI findings. |
| PR-009 | Verification prompt | Acceptance criteria, commands, outputs, runtime evidence. | Requirement-level verification report. |
| PR-010 | Harness improvement prompt | Repeated failure or intervention, run trace. | Missing control classification and proposed durable change. |
| PR-011 | Handoff prompt | Current state, completed work, pending work, risks. | Resume-ready handoff artifact. |

## 7. Prompt Patterns

### Intake

```text
Derive the project-development task from the request.
Return:
1. Objective
2. Acceptance criteria with stable IDs
3. Non-goals
4. Risk level and why
5. Required approvals
6. Assumptions
7. Open questions that block safe implementation
Do not propose implementation steps yet.
```

### Planning

```text
Using the accepted criteria and selected context, produce a plan.
For each step include:
- Purpose
- Files or areas likely touched
- Controls to consult before editing
- Verification checkpoint
- Approval needed, if any
Keep steps ordered by dependency.
```

### Failure Attribution

```text
A check failed. Before editing again:
1. State the failed command or observation.
2. State the expected behavior.
3. State the actual behavior.
4. Identify the most likely cause and confidence.
5. Choose the smallest diagnostic or repair step.
6. Name the check that will be rerun.
```

### Verification

```text
Produce a verification report.
For each acceptance criterion:
- Status: passed, failed, blocked, not applicable, or unverified
- Evidence: command, test, screenshot, trace, log, review, or explanation
- Residual risk
Do not claim completion if any required criterion is failed, blocked, or unverified.
```

### Harness Improvement

```text
Given the failure, review comment, intervention, or escaped defect:
1. Classify the missing control: guide, sensor, tool, permission, memory, prompt, state, review, entropy.
2. Explain whether the issue was preventable.
3. Propose one durable control.
4. Define how to verify the control works.
5. Record where the control should live.
```

## 8. Handoff Protocol

The skill shall write handoff state when:

- Work exceeds one session.
- Context compaction or reset is likely.
- The agent pauses for approval.
- A blocker remains unresolved.
- A user interrupts work.

Handoff artifact:

```yaml
handoff:
  objective: ""
  current_status: ""
  completed:
    - ""
  pending:
    - ""
  changed_files:
    - ""
  commands_run:
    - command: ""
      result: ""
  decisions:
    - ""
  assumptions:
    - ""
  risks:
    - ""
  next_action: ""
```

## 9. Memory Safety Requirements

| ID | Requirement |
| --- | --- |
| SM-033 | Do not store secrets, credentials, tokens, private customer data, or sensitive logs in project memory. |
| SM-034 | Do not treat old memory as authoritative when code, tests, or current command output contradict it. |
| SM-035 | Do not use hidden evaluator notes or expected fixes as agent-visible context. |
| SM-036 | Do not hide human intervention from the episode record. |
| SM-037 | Do not compress away unresolved risks, blocked checks, or failed verification. |

