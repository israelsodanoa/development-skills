# Functional Requirements Specification: Harness Development Skill

Research date: 2026-06-15

## 1. Objective

Create a Codex agent skill that applies harness engineering to manage project development. The skill shall guide an autonomous coding agent through structured project intake, planning, implementation, verification, review, evidence production, and continuous harness improvement.

The skill exists to make autonomous development higher quality by treating the system around the model as the product surface: repository instructions, project memory, tool access, command registries, permissions, task state, feedback sensors, observability, verification reports, and human governance.

## 2. Target Users

- Human engineers who delegate feature, bug, refactor, or maintenance work to autonomous coding agents.
- Technical leads who want agent work to follow project architecture, testing, and review standards.
- Agent operators who need repeatable evidence that a feature is complete.
- Future Codex agents that need compact procedural guidance for running harnessed project-development workflows.

## 3. Scope

### In Scope

- Project intake and acceptance-criteria capture.
- Harness maturity assessment for a repository.
- Creation or maintenance of project harness artifacts such as command registries, verification templates, task state, known-failure logs, and documentation maps.
- Context and memory selection for autonomous agent runs.
- Development-phase workflows for features, bug fixes, refactors, UI changes, security fixes, and maintenance tasks.
- Feedforward guides and feedback sensors.
- Tool and permission governance.
- Verification reporting, evidence mapping, and completion audit.
- Continuous improvement of the harness after repeated mistakes or avoidable interventions.

### Out Of Scope

- Fully replacing human product judgment.
- Bypassing repository, organization, or platform permissions.
- Automatically deploying to production without explicit user approval.
- Guaranteeing correctness without acceptance criteria or observable behavior.
- Creating a monolithic project manual that the agent loads in full for every task.

## 4. Operating Principles

- The harness, not the model alone, is responsible for repeatable quality.
- Every repeated agent mistake is evidence of a missing or weak control.
- "Done" is an evidence-backed state, not an agent assertion.
- Context must be selected, not dumped.
- Fast deterministic checks should run before slower inferential review.
- Human attention is a scarce control surface and should be used for product, architecture, risk, and ambiguity decisions.
- The harness must improve after failures, not merely retry the same prompt.

## 5. Functional Requirements

| ID | Requirement | Priority | Acceptance Evidence |
| --- | --- | --- | --- |
| FR-001 | The skill shall trigger for project development management, harness engineering, autonomous-agent quality control, agent workflow design, and repository harness setup tasks. | Must | `SKILL.md` description includes these trigger contexts. |
| FR-002 | The skill shall begin by deriving or confirming task intent, acceptance criteria, non-goals, constraints, and risk level. | Must | Intake template contains all fields and the workflow requires filling them before implementation. |
| FR-003 | The skill shall assess repository harness maturity using H0-H3 levels: minimal baseline, tool harness, context-memory harness, and observability-verification harness. | Must | Assessment checklist maps current repository artifacts to maturity level. |
| FR-004 | The skill shall create or update a compact project map instead of instructing the agent to load all documentation at once. | Must | Context-selection rules and project-memory index are present. |
| FR-005 | The skill shall require an explicit command registry for safe build, test, lint, type-check, format, security, local-run, and visual-verification commands. | Must | Tooling requirements define registry fields and validation rules. |
| FR-006 | The skill shall maintain task state for active work, including plan, inspected files, decisions, assumptions, open questions, blocked items, verification status, and next action. | Must | State schema includes those fields and workflows update them. |
| FR-007 | The skill shall define project memory controls for architecture, domain rules, testing strategy, known failures, service maps, data contracts, and prior decisions. | Must | Memory schema and update rules are documented. |
| FR-008 | The skill shall provide prompting strategies for intake, planning, implementation, failure attribution, self-review, reviewer delegation, harness improvement, and handoff. | Must | Prompt patterns are specified with required inputs and outputs. |
| FR-009 | The skill shall expose feedforward controls that steer the agent before action, including specs, rules, examples, architecture guides, testing guides, command registries, and known-failure notes. | Must | Control requirements distinguish feedforward controls and map them to failure modes. |
| FR-010 | The skill shall expose feedback controls that inspect work after action, including tests, lint, type checks, architecture checks, security scans, browser/screenshot checks, logs, traces, and review agents. | Must | Control requirements distinguish feedback controls and map them to failure modes. |
| FR-011 | The skill shall classify controls as computational or inferential and prefer computational controls when they are cheap, deterministic, and sufficient. | Must | Control model includes computational/inferential selection rules. |
| FR-012 | The skill shall implement a failure-attribution protocol before repair when verification fails. | Must | Workflows require reproduction, observed failure, suspected cause, repair plan, and follow-up check. |
| FR-013 | The skill shall require requirement-level verification before completion. | Must | Verification report maps each acceptance criterion to evidence or a documented exception. |
| FR-014 | The skill shall track human interventions and classify whether each intervention was unavoidable or indicates a missing harness control. | Must | Intervention log schema and improvement workflow are defined. |
| FR-015 | The skill shall require permission boundaries for destructive commands, dependency changes, credential access, migrations, production operations, external network access, and publishing. | Must | Boundaries are written as Always, Ask First, and Never rules. |
| FR-016 | The skill shall support long-running development through handoff artifacts and context compaction/reset protocols. | Must | Multi-session workflow defines startup, handoff, resume, and completion rules. |
| FR-017 | The skill shall support agent-to-agent review loops when available, while preserving human approval for ambiguous product, architecture, security, or irreversible decisions. | Should | Review workflow includes local self-review, specialized reviewer prompts, and escalation rules. |
| FR-018 | The skill shall support UI and runtime verification through browser automation, screenshots, DOM snapshots, logs, traces, and metrics when applicable. | Should | UI/runtime workflow lists required artifacts and acceptance evidence. |
| FR-019 | The skill shall support recurring entropy controls such as stale-doc scans, dead-code checks, dependency audits, architecture drift checks, and cleanup tasks. | Should | Maintenance workflow and metrics include entropy controls. |
| FR-020 | The skill shall produce an auditable episode package for substantial tasks. | Must | Trace schema includes action, tool, context, verification, failure-attribution, intervention, entropy, permission, cost, and outcome evidence. |
| FR-021 | The skill shall define completion criteria that require evidence, residual-risk disclosure, and no unresolved required checks. | Must | Evaluation requirements define done and not-done states. |
| FR-022 | The skill shall include a process for converting repeated failures into durable harness changes: rule, doc, tool, script, test, checker, or review prompt. | Must | Harness improvement workflow exists and has acceptance criteria. |
| FR-023 | The skill shall avoid creating bloated skill instructions. Detailed guidance shall live in references and be loaded only when relevant. | Must | Skill packaging requirements use progressive disclosure. |
| FR-024 | The skill shall include optional scripts only for operations requiring deterministic reliability or repeated execution. | Should | Tool requirements define script inclusion criteria and test expectations. |
| FR-025 | The skill shall define metrics for quality, autonomy, review burden, intervention rate, defect escape rate, verification cost, and entropy. | Should | Evaluation requirements include metric definitions and collection points. |

## 6. Non-Functional Requirements

| ID | Requirement | Acceptance Evidence |
| --- | --- | --- |
| NFR-001 | The skill must be context efficient. | `SKILL.md` remains procedural and delegates detailed content to references. |
| NFR-002 | The skill must be auditable. | Each substantial run produces a verification report and episode evidence. |
| NFR-003 | The skill must be safe by default. | Risky actions require approval or are forbidden. |
| NFR-004 | The skill must be repository-agnostic. | Project-specific details are discovered and stored in project harness artifacts, not hardcoded into the skill. |
| NFR-005 | The skill must preserve user work. | Workflows require checking current state before edits and avoiding reversal of unrelated changes. |
| NFR-006 | The skill must degrade gracefully. | If tools or checks are missing, the agent records the gap and uses the best available evidence without claiming full verification. |
| NFR-007 | The skill must support incremental adoption. | H0-H3 maturity model allows useful operation before all controls exist. |
| NFR-008 | The skill must be measurable. | Metrics and trace schema define how quality and autonomy are evaluated. |

## 7. Commands

This repository currently contains requirements documents rather than executable implementation code. The future skill shall discover and document project-specific commands. For this specification, verification commands are:

```bash
find docs -maxdepth 1 -type f -name '*.md' -print | sort
rg -n 'FR-|NFR-|WF-|CTRL-|SM-|PR-|TOOL-|EVAL-|AC-' docs
rg -n 'TB[D]|FIXM[E]|\[\]' docs resources
rg -n '[^\x00-\x7F]' docs resources
```

## 8. Project Structure

Current specification layout:

```text
resources/
  working-summary.md
  harness-engineering-definitions.md
  harness-control-layers.md
  quality-through-autonomous-agent-harnesses.md
docs/
  README.md
  functional-requirements-specification.md
  use-cases-and-workflows.md
  control-layer-requirements.md
  state-memory-and-prompting-requirements.md
  tools-and-integration-requirements.md
  evaluation-and-quality-requirements.md
```

Target future skill layout:

```text
harness-development/
  SKILL.md
  agents/
    openai.yaml
  references/
    workflows.md
    controls.md
    state-memory.md
    prompting.md
    tools.md
    evaluation.md
  scripts/
    validate_harness_state.py
    render_verification_report.py
    audit_docs_freshness.py
    summarize_episode.py
```

The future skill folder should not include auxiliary documentation such as a README unless the skill packaging standard changes. This `docs/` directory is the planning specification outside the final skill package.

## 9. Documentation Style

- Use concise imperative requirements with stable IDs.
- Prefer tables for requirement matrices and control mappings.
- Use `Must`, `Should`, and `May` for priority.
- Keep repository-specific facts out of the reusable skill unless they are examples.
- Prefer ASCII in files unless a referenced project already requires another character set.
- Include exact command examples rather than vague tool names.

## 10. Success Criteria

| ID | Criterion |
| --- | --- |
| AC-001 | The `docs/` folder contains a coherent functional requirements specification set for the Harness Development skill. |
| AC-002 | The documents cover use cases, workflows, controls, tools, state and memory, prompting strategies, verification, evaluation, and skill packaging. |
| AC-003 | The documents build from the current `resources/` research rather than contradicting it. |
| AC-004 | Requirements are concrete enough to guide a future implementation of `SKILL.md`, references, and scripts. |
| AC-005 | The specification defines the ideal operating scenario for managing project development with autonomous agents. |
| AC-006 | The specification includes acceptance evidence and audit criteria for completion. |

## 11. Open Decisions For Implementation

- Final skill name: default is `harness-development`.
- Whether the initial implementation should be instruction-only or include scripts immediately.
- Whether state artifacts should live in `.harness/`, `docs/exec-plans/`, or another project-standard location when a target repository already has conventions.
- Which MCP integrations are mandatory for the first implementation versus optional.
