# Intake: 20260627-193714-planning-quality-gates

## Normalized Summary

- Status: complete
- Task type: harness_improvement
- Objective: Upgrade harness planning from lightweight templates into strict, research-backed planning and task quality gates.

## Required Fields

- [x] `objective` - Objective
- [x] `task_type` - Task type
- [x] `audience` - Audience or user
- [x] `desired_outcome` - Desired outcome
- [x] `success_criteria` - Success criteria
- [x] `non_goals` - Non-goals
- [x] `constraints` - Constraints
- [x] `permissions` - Permissions
- [x] `verification_expectations` - Verification expectations

## Answers

### objective

- Kind: answer
- Value: Upgrade harness planning from lightweight templates into strict, research-backed planning and task quality gates.

### task_type

- Kind: answer
- Value: harness_improvement

### audience

- Kind: answer
- Value: Codex agents and human operators using harness-development to plan implementation work.

### desired_outcome

- Kind: answer
- Value: Plan and task artifacts become detailed, enforceable, implementation-ready, and blocked by strict quality validation before downstream phases.

### success_criteria

- Kind: answer
- Value: Plan template requires research-backed planning sections\nTask template requires atomic XS/S task fields\nPlan/task validators reject incomplete or oversized artifacts\nPrompt packets and docs describe the new workflow\nUnittest discovery and compileall pass

### non_goals

- Kind: answer
- Value: No external dependencies\nNo command interface renames\nNo changes to authoritative top-level state fields beyond optional planning quality evidence

### constraints

- Kind: answer
- Value: Use Python standard library only; keep existing CLI commands stable; preserve backwards-compatible state.

### permissions

- Kind: answer
- Value: Always: edit harness scripts, docs, and tests. Ask first: destructive git operations, external services, dependency additions. Never: commit secrets or fabricate evidence.

### verification_expectations

- Kind: answer
- Value: Run python3 -m unittest discover tests and python3 -m compileall scripts.


## Waivers

- None recorded.

## Question Rounds

- No question batches recorded yet.

## Open Questions

- None recorded.
