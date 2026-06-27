# Spec: 20260627-193714-planning-quality-gates

## Objective

Upgrade harness planning from lightweight templates into strict, research-backed planning and task quality gates.

Audience: Codex agents and human operators using harness-development to plan implementation work.

Desired outcome: Plan and task artifacts become detailed, enforceable, implementation-ready, and blocked by strict quality validation before downstream phases.

## Tech Stack

- To be discovered from the target repository before implementation.

## Commands

- Build: To be discovered from the command registry or project manifests.
- Test: To be discovered from the command registry or project manifests.
- Lint: To be discovered from the command registry or project manifests.
- Dev/local run: To be discovered from the command registry or project manifests.

## Project Structure

- To be mapped from repository inspection.

## Code Style

Document local naming, formatting, and example patterns before implementation.

## Testing Strategy

Run python3 -m unittest discover tests and python3 -m compileall scripts.

## Boundaries

- Always: preserve unrelated user work; record evidence in `.harness`.
- Ask first: dependencies, CI, migrations, Docker/Sonar execution, external systems, releases.
- Never: commit secrets, fabricate evidence, remove failing tests to claim success.
- Constraints: Use Python standard library only; keep existing CLI commands stable; preserve backwards-compatible state.

### Non-Goals

- No external dependencies\nNo command interface renames\nNo changes to authoritative top-level state fields beyond optional planning quality evidence

## Success Criteria

- Plan template requires research-backed planning sections\nTask template requires atomic XS/S task fields\nPlan/task validators reject incomplete or oversized artifacts\nPrompt packets and docs describe the new workflow\nUnittest discovery and compileall pass

## Assumptions

- None recorded.

## Open Questions

- None recorded.
