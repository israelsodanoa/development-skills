#!/usr/bin/env python3
"""Validate request state and enforce spec-driven phase transitions."""

from __future__ import annotations

import argparse

from harness_common import (
    GATE_BY_TARGET_PHASE,
    PHASE_ORDER,
    PHASES,
    HarnessError,
    append_history,
    intake_gate_problems,
    load_registry,
    load_state,
    main_guard,
    print_json,
    save_state,
    validate_plan,
    validate_spec,
    validate_tasks,
    verification_path,
)


def missing_required_commands(target: str, state: dict) -> list[str]:
    registry = load_registry(target)
    required = [
        command["id"]
        for command in registry.get("commands", [])
        if command.get("required_before_completion")
    ]
    successful = {
        command.get("command_id")
        for command in state.get("commands_run", [])
        if command.get("returncode") == 0
    }
    return [command_id for command_id in required if command_id not in successful]


def approve(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    if args.gate not in state.get("approvals", {}):
        raise HarnessError(f"Unknown gate: {args.gate}")
    state["approvals"][args.gate] = True
    state["status"] = f"{args.gate}_approved"
    save_state(args.target, args.request_id, state)
    append_history(args.target, args.request_id, "approval.recorded", f"Approved {args.gate} gate", note=args.note)
    print_json({"request_id": args.request_id, "approved": args.gate})


def transition(args: argparse.Namespace) -> None:
    target_phase = args.to.upper()
    if target_phase not in PHASES:
        raise HarnessError(f"Unknown phase: {target_phase}")
    state = load_state(args.target, args.request_id)
    current = state.get("phase", "SPECIFY")
    if PHASE_ORDER[target_phase] > PHASE_ORDER[current] + 1:
        raise HarnessError(f"Cannot skip phases: {current} -> {target_phase}")
    gate = GATE_BY_TARGET_PHASE.get(target_phase)
    if gate and not state.get("approvals", {}).get(gate):
        raise HarnessError(f"Cannot enter {target_phase}; {gate} gate is not approved")
    if target_phase == "PLAN" and validate_spec(args.target, args.request_id):
        raise HarnessError("Cannot enter PLAN; spec.md is invalid")
    if target_phase == "PLAN":
        problems = intake_gate_problems(state)
        if problems:
            raise HarnessError(f"Cannot enter PLAN; intake is incomplete: {'; '.join(problems)}")
    if target_phase == "TASKS" and validate_plan(args.target, args.request_id):
        raise HarnessError("Cannot enter TASKS; plan.md is invalid")
    if target_phase == "IMPLEMENT" and validate_tasks(args.target, args.request_id):
        raise HarnessError("Cannot enter IMPLEMENT; tasks.md is invalid")
    if target_phase == "CLOSEOUT" and not verification_path(args.target, args.request_id).exists():
        raise HarnessError("Cannot close out without verification-report.md")
    if target_phase == "CLOSEOUT":
        missing_commands = missing_required_commands(args.target, state)
        if missing_commands:
            raise HarnessError(f"Cannot close out; required commands have not succeeded: {', '.join(missing_commands)}")
    state["phase"] = target_phase
    state["status"] = args.status or target_phase.lower()
    state["next_action"] = args.next_action or state.get("next_action", "")
    save_state(args.target, args.request_id, state)
    append_history(args.target, args.request_id, "state.transition", f"{current} -> {target_phase}", status=state["status"])
    print_json({"request_id": args.request_id, "from": current, "to": target_phase, "status": state["status"]})


def validate(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    missing = [field for field in ["request_id", "objective", "phase", "status", "approvals", "next_action"] if field not in state]
    phase = state.get("phase")
    if phase not in PHASES:
        missing.append("valid phase")
    intake_problems = intake_gate_problems(state)
    print_json({"request_id": args.request_id, "valid": not missing, "problems": missing, "phase": phase, "intake_problems": intake_problems})


def show(args: argparse.Namespace) -> None:
    print_json(load_state(args.target, args.request_id))


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, func in [("show", show), ("validate", validate)]:
        item = sub.add_parser(name)
        item.add_argument("--target", default=".")
        item.add_argument("--request-id", required=True)
        item.set_defaults(func=func)
    approve_parser = sub.add_parser("approve")
    approve_parser.add_argument("--target", default=".")
    approve_parser.add_argument("--request-id", required=True)
    approve_parser.add_argument("--gate", choices=["spec", "plan", "tasks"], required=True)
    approve_parser.add_argument("--note", default="")
    approve_parser.set_defaults(func=approve)
    transition_parser = sub.add_parser("transition")
    transition_parser.add_argument("--target", default=".")
    transition_parser.add_argument("--request-id", required=True)
    transition_parser.add_argument("--to", choices=PHASES, required=True)
    transition_parser.add_argument("--status", default="")
    transition_parser.add_argument("--next-action", default="")
    transition_parser.set_defaults(func=transition)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_guard(run)
