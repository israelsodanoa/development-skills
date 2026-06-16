# Evaluation And Quality Requirements

Research date: 2026-06-15

## 1. Quality Thesis

The skill shall raise feature quality by making autonomous development evidence-producing. Quality is achieved when the harness can show that the implementation satisfies acceptance criteria, preserves existing behavior, respects architecture and safety boundaries, and leaves an auditable trail.

## 2. Definition Of Done

| ID | Requirement |
| --- | --- |
| EVAL-001 | Each acceptance criterion has status and evidence. |
| EVAL-002 | Required commands have been run or a documented reason explains why they could not run. |
| EVAL-003 | Failed checks have failure attribution and follow-up result. |
| EVAL-004 | Runtime behavior has direct evidence when the requested change is observable only at runtime. |
| EVAL-005 | Security, permission, and privacy risks have been considered for risky changes. |
| EVAL-006 | The diff avoids unrelated churn or explicitly reports it. |
| EVAL-007 | Human or policy approval is recorded for approval-required actions. |
| EVAL-008 | Residual risks are stated clearly. |
| EVAL-009 | Any repeated failure or avoidable intervention has a proposed harness improvement. |
| EVAL-010 | The agent does not claim completion if any required criterion remains failed, blocked, or unverified. |

## 3. Evidence Contract

| Evidence type | What it proves | Limits |
| --- | --- | --- |
| Unit test | Local behavior for a small unit. | Does not prove integration or UI behavior. |
| Integration test | Interaction between components. | May not cover production config or edge cases. |
| E2E test | User or system workflow. | Can be slow and brittle. |
| Type check | Static interface consistency. | Does not prove runtime behavior. |
| Lint/format | Style and simple correctness rules. | Does not prove product correctness. |
| Architecture check | Boundary and dependency rules. | Does not prove behavior. |
| Security scan | Known secret, dependency, or static risk patterns. | Does not prove absence of vulnerabilities. |
| Browser screenshot/video | Visual state or interaction evidence. | Needs viewport and scenario context. |
| Logs/traces/metrics | Runtime path and performance evidence. | Needs correct instrumentation and environment. |
| Human approval | Product, risk, or architecture judgment. | Does not replace executable checks. |
| Agent review | Semantic or specialist review. | Probabilistic and should be treated as review input. |

## 4. Verification Report Schema

```yaml
verification_report:
  task_id: ""
  objective: ""
  summary_status: passed
  acceptance_criteria:
    - id: AC-001
      text: ""
      status: passed
      evidence:
        - type: command
          reference: "npm test -- user-flow.test.ts"
          result: passed
      residual_risk: ""
  commands:
    - command: ""
      workdir: ""
      purpose: ""
      result: ""
  runtime_evidence:
    - type: screenshot
      path: ""
      scenario: ""
  failed_checks:
    - check: ""
      attribution: ""
      resolution: ""
  approvals:
    - action: ""
      approver: ""
      reason: ""
  residual_risks:
    - ""
  harness_improvements:
    - ""
```

## 5. Episode Trace Schema

Substantial tasks shall produce an episode package or equivalent record.

| ID | Trace class | Requirement |
| --- | --- | --- |
| EVAL-011 | Action trace | Record meaningful agent actions and file changes. |
| EVAL-012 | Tool trace | Record commands and tool calls with purpose and outcome. |
| EVAL-013 | Context trace | Record which docs, files, examples, and memories were used. |
| EVAL-014 | Verification trace | Record checks, evidence, and requirement coverage. |
| EVAL-015 | Failure-attribution trace | Record failed checks, diagnosis, repair, and rerun result. |
| EVAL-016 | Intervention trace | Record human help and whether it exposed a missing harness control. |
| EVAL-017 | Entropy trace | Record stale docs, duplicate code, residue, dependency churn, and drift. |
| EVAL-018 | Permission trace | Record approval-required or forbidden action decisions. |
| EVAL-019 | Cost trace | Record long-running checks, excessive loops, or expensive tool usage when available. |
| EVAL-020 | Outcome trace | Record final status, residual risk, and follow-up work. |

## 6. Harness Maturity Evaluation

| Level | Required evidence |
| --- | --- |
| H0: Minimal baseline | Task description and repository files only. |
| H1: Tool harness | H0 plus tool registry, command registry, and tool-use protocol. |
| H2: Context-memory harness | H1 plus project memory, task state, known failures, and context-selection protocol. |
| H3: Observability-verification harness | H2 plus deterministic check registry, reproduction protocol, failure-attribution protocol, verification report, and episode trace. |

The skill shall be able to operate at any level but shall not represent H0 or H1 work as fully harnessed. It shall report which controls were missing and how that affects confidence.

## 7. Metrics

| ID | Metric | Definition |
| --- | --- | --- |
| EVAL-021 | Acceptance coverage | Percent of acceptance criteria with direct evidence. |
| EVAL-022 | Verification completeness | Percent of required checks run or explicitly waived. |
| EVAL-023 | Defect escape rate | Rate of harnessed changes that require post-merge bug fixes. |
| EVAL-024 | Review iteration count | Number of review loops before acceptance. |
| EVAL-025 | Avoidable intervention rate | Human interventions that indicate missing controls divided by total interventions. |
| EVAL-026 | Failure recovery rate | Failed checks that the agent diagnosed and resolved without unrelated churn. |
| EVAL-027 | Architecture violation count | Boundary or dependency violations introduced or found. |
| EVAL-028 | Security finding count | Security issues introduced or found during the episode. |
| EVAL-029 | Entropy score | Weighted stale docs, dead files, duplicate helpers, dependency churn, and residue. |
| EVAL-030 | Verification cost | Runtime, token, or compute cost of checks and review loops. |
| EVAL-031 | Rollback rate | Merged changes later reverted or rolled back. |
| EVAL-032 | Harness improvement throughput | Durable controls added per repeated failure pattern. |

## 8. Acceptance Tests For The Future Skill

| ID | Scenario | Expected behavior |
| --- | --- | --- |
| EVAL-033 | User asks to bootstrap a repo harness. | Skill inspects repo, produces maturity assessment, command registry proposal, memory index, and control gap backlog. |
| EVAL-034 | User asks for a feature with vague requirements. | Skill derives acceptance criteria, assumptions, and open questions before implementation. |
| EVAL-035 | A registered test command fails. | Skill records failure attribution before repair and reruns the relevant check. |
| EVAL-036 | User asks for UI work. | Skill requires runtime/browser evidence before claiming completion. |
| EVAL-037 | User asks for a risky database migration. | Skill escalates for approval before changing schema or running migration commands. |
| EVAL-038 | Long-running work is interrupted. | Skill writes handoff state with completed work, pending tasks, risks, and next action. |
| EVAL-039 | Review identifies repeated wrong-layer edits. | Skill proposes a durable architecture guide or boundary check update. |
| EVAL-040 | Project has no command registry. | Skill records an H1 gap and does not pretend registered checks exist. |

## 9. Completion Audit For This Specification

The documentation set is complete when:

- The `docs/` folder exists.
- It contains the primary FRS and companion documents.
- Use cases and workflows are documented.
- Controls are documented.
- Tools and integrations are documented.
- Agent state and memory controls are documented.
- Prompting strategies are documented.
- Evaluation, quality, metrics, and evidence requirements are documented.
- The documents are internally linked from `docs/README.md`.
- No unfinished placeholder markers remain.
