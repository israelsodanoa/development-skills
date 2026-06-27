# Plan: 20260627-193714-planning-quality-gates

## Overview

Objective recap: Upgrade harness planning from lightweight templates into strict, research-backed planning and task quality gates.

This plan must be implementation-ready before task breakdown. It uses research-backed planning controls to make scope, decisions, dependencies, risks, and verification explicit.

## Planning Standard

- `wbs`: use work-breakdown decomposition so every deliverable has an implementation owner.
- `invest`: keep planned slices independent, valuable, estimable, small, and testable.
- `smart`: keep outcomes specific, measurable, achievable, relevant, and verification-bound.
- `adr`: record decisions with context, decision, rationale, and consequences.
- `rapid`: identify who recommends, agrees, performs, gives input, and decides when decisions are not obvious.
- `cynefin`: classify complexity before choosing linear, expert-led, experimental, or emergency sequencing.
- `gherkin`: express behavioral acceptance with Given/When/Then scenarios when runtime behavior is observable.
- `premortem`: identify failure modes before implementation and attach mitigations.

## Decomposition Map

- Deliverable 1: Apply the approved spec to the smallest complete planning surface.
- Deliverable 2: Preserve existing CLI behavior while strengthening generated artifacts and validation.
- Deliverable 3: Prove the new gate behavior with focused tests and compile checks.

## Dependency Graph

- Approved intake and spec -> plan quality gate -> task quality gate -> implementation -> verification report.
- Shared validator behavior before engine output changes.
- Engine output changes before prompt, docs, and test assertions that depend on those outputs.

## Implementation Strategy

1. Inspect the relevant project files, request state, and harness memory before editing.
2. Implement shared validation first so both CLIs and phase transitions use one quality contract.
3. Update templates and prompt packets to teach the same contract that validators enforce.
4. Add tests that cover valid artifacts, invalid artifacts, state quality evidence, and transition gates.

## Implementation Slices

- Slice 1: Shared plan/task quality validation and backward-compatible state defaults.
- Slice 2: CLI engine output and approval state evidence.
- Slice 3: Prompt and documentation updates that describe the enforced workflow.
- Slice 4: Tests for plan creation, validation, gating, prompt support, and task granularity.

## Decision Records

- Context: Plan and task artifacts were previously marker-based and could pass while too vague for reliable implementation.
- Decision: Enforce research-backed planning and XS/S task quality through existing validators.
- Rationale: Keeping the gate in shared validation makes CLI approval and phase transitions consistent.
- Consequences: Incomplete or oversized task lists fail earlier; users may need to fill richer artifacts before implementation.

## Verification Strategy

- Run targeted checks closest to the changed behavior.
- Run `python3 -m unittest discover tests` for workflow regression coverage.
- Run `python3 -m compileall scripts` for Python syntax coverage.
- Produce `verification-report.md` after acceptance evidence is recorded.

## Verification Matrix

| Criteria | Evidence | Command |
| --- | --- | --- |
| Plan template includes research-backed sections | Generated `plan.md` inspection and tests | `python3 -m unittest discover tests` |
| Task validation rejects vague or oversized work | Task workflow tests | `python3 -m unittest discover tests` |
| Scripts remain syntactically valid | Compile evidence | `python3 -m compileall scripts` |

## Premortem Risks

- Failure mode: Validators become so strict that generated artifacts cannot pass. Mitigation: keep generated plan structurally valid and test invalid cases separately.
- Failure mode: Existing transition gates bypass quality checks. Mitigation: route transitions through the shared validators.
- Failure mode: Documentation drifts from CLI behavior. Mitigation: update prompt and workflow references with the same required fields.

## Complexity Classification

Cynefin domain: complicated. The implementation is deterministic but touches shared workflow contracts, so sequence validator changes before engine, prompt, docs, and tests.

## Sequencing Rationale

- Build foundations first: common validators and state defaults.
- Then update engines that call those validators.
- Then update prompts/docs that explain the new behavior.
- Finish with tests and compile checks to catch regressions.

## Parallelization Boundaries

- Parallel: documentation and prompt wording can proceed after validator field names are stable.
- Sequential: shared validation must land before engine approval logic and state transition assertions.

## Risks

- Strict validation may reject useful plans if field names drift; mitigate with stable templates and focused tests.
- Task parsing is markdown-based; mitigate by using simple required field labels and clear generated examples.

## Open Questions

- None recorded yet.
