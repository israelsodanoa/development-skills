#!/usr/bin/env python3
"""Generate phase-specific prompt packets for harnessed implementation."""

from __future__ import annotations

import argparse

from harness_common import load_state, main_guard, print_json, request_dir, tasks_path, plan_path, spec_path, now_iso


PHASE_INSTRUCTIONS = {
    "specify": "Derive assumptions, objective, success criteria, boundaries, risk, and open questions. Persist updates in spec.md.",
    "plan": "Use the approved spec to produce dependency-ordered implementation strategy and verification checkpoints.",
    "tasks": "Break the approved plan into small tasks with acceptance, verification, dependencies, and likely files.",
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

- Spec: `{spec_path(args.target, args.request_id)}`
- Plan: `{plan_path(args.target, args.request_id)}`
- Tasks: `{tasks_path(args.target, args.request_id)}`
- State: `{request_dir(args.target, args.request_id) / 'state.json'}`
- History: `{request_dir(args.target, args.request_id) / 'history.jsonl'}`

## Gating Rule

Do not advance phases without validating and approving the current gate in `state.json`.
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
