#!/usr/bin/env python3
"""Generate phase-specific prompt packets for harnessed implementation."""

from __future__ import annotations

import argparse

from harness_common import intake_path, load_state, main_guard, print_json, request_dir, tasks_path, plan_path, spec_path, now_iso


PHASE_INSTRUCTIONS = {
    "intake": """Interview the user before planning. Ask adaptive question batches, persist answers in intake.md/state.json, and do not move to spec approval until intake is complete.

Required output contract:
1. Objective
2. Task type
3. Audience or user
4. Desired outcome
5. Acceptance criteria
6. Non-goals
7. Constraints
8. Permissions
9. Verification expectations
10. Assumptions, waivers, and blocking open questions

Use a common first batch, then type-specific follow-ups for feature, bug, refactor, UI/runtime, security/reliability, review, maintenance, or harness-improvement work. Ask risk follow-ups for migrations, external systems, credentials, destructive actions, production impact, or ambiguous product behavior.""",
    "specify": "Derive assumptions, objective, success criteria, boundaries, risk, and open questions. Persist updates in spec.md.",
    "plan": """Use the approved spec to produce a research-backed implementation plan that can pass the strict plan gate.

Required output contract:
1. Objective recap and planning standard.
2. WBS decomposition map that covers deliverables.
3. Dependency graph with explicit before/after relationships.
4. Implementation strategy and implementation slices.
5. Decision records using context, decision, rationale, and consequences; identify RAPID roles when ownership is ambiguous.
6. Verification strategy and Verification Matrix mapping criteria to evidence and command.
7. Premortem risks with failure mode and mitigation.
8. Cynefin complexity classification and sequencing rationale.
9. Parallelization boundaries that distinguish parallel and sequential work.
10. Residual risks and open questions.

Apply WBS, INVEST, SMART, ADR, RAPID, Cynefin, Gherkin, and premortem thinking. Do not approve the plan until every required section contains concrete detail and validation passes.""",
    "tasks": """Break the approved plan into the lowest practical level: atomic XS/S tasks that can each be implemented and verified in one focused session.

Required output contract for every task:
1. Task ID and short title.
2. Task, outcome, exact scope, and non-scope.
3. Size limited to XS or S; split M, L, or XL work again.
4. Acceptance criteria.
5. Gherkin-style Given/When/Then scenario when behavior is observable.
6. Verification command or evidence.
7. Dependencies and likely files or path patterns.
8. Risk notes and rollback/repair note.
9. Parallelization label: parallel, sequential, or coordination-required.

Reject placeholder tasks, vague file lists, tasks joined with "and", and tasks that touch independent subsystems. Do not approve `tasks.md` until strict validation passes.""",
    "implement": "Complete one task at a time, preserve unrelated work, and record decisions, commands, and changed files.",
    "failure": "Attribute the failed check before repair: expected, actual, likely cause, smallest fix, rerun check.",
    "review": "Review diff scope, evidence coverage, architecture, security, product fit, and test quality.",
    "verify": "Map each acceptance criterion to command, runtime, review, or documented-waiver evidence.",
    "improve": "Classify repeated failures into missing controls and propose durable harness changes.",
    "handoff": "Produce resume-ready state with completed work, pending work, risks, decisions, and next action.",
}


def render(args: argparse.Namespace) -> str:
    state = load_state(args.target, args.request_id)
    phase = args.phase.lower()
    instruction = PHASE_INSTRUCTIONS[phase]
    return f"""# Prompt Packet: {phase}

Generated: {now_iso()}
Request ID: {args.request_id}
Current phase: {state.get('phase')}
Objective: {state.get('objective')}

## Required Instruction

{instruction}

## Durable Artifacts

- Intake: `{intake_path(args.target, args.request_id)}`
- Spec: `{spec_path(args.target, args.request_id)}`
- Plan: `{plan_path(args.target, args.request_id)}`
- Tasks: `{tasks_path(args.target, args.request_id)}`
- State: `{request_dir(args.target, args.request_id) / 'state.json'}`
- History: `{request_dir(args.target, args.request_id) / 'history.jsonl'}`

## Gating Rule

Do not approve `spec.md` or enter PLAN until intake is complete. Do not advance later phases without validating and approving the current gate in `state.json`.
"""


def generate(args: argparse.Namespace) -> None:
    text = render(args)
    output = request_dir(args.target, args.request_id) / "prompt-packets" / f"{args.phase.lower()}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.write:
        output.write_text(text, encoding="utf-8")
    if args.print:
        print(text)
    else:
        print_json({"request_id": args.request_id, "phase": args.phase, "path": str(output), "written": args.write})


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".")
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--phase", choices=sorted(PHASE_INSTRUCTIONS), required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--print", action="store_true")
    args = parser.parse_args()
    generate(args)


if __name__ == "__main__":
    main_guard(run)
