#!/usr/bin/env python3
"""Create, validate, and approve implementation plans."""

from __future__ import annotations

import argparse

from harness_common import HarnessError, append_history, load_state, main_guard, plan_path, print_json, save_state, validate_plan, write_if_absent


def plan_template(request_id: str, objective: str) -> str:
    return f"""# Plan: {request_id}

## Overview

{objective}

## Implementation Strategy

1. Inspect the relevant project files and memory.
2. Make the smallest cohesive changes needed for the approved spec.
3. Update `.harness` state and history after meaningful steps.

## Verification Strategy

- Run targeted checks closest to the changed behavior.
- Run broader checks before completion when risk justifies it.
- Produce `verification-report.md`.

## Risks

- Record concrete risks discovered during planning.

## Open Questions

- None recorded yet.
"""


def create(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    if not state.get("approvals", {}).get("spec"):
        raise HarnessError("Cannot create plan.md until the spec gate is approved")
    wrote = write_if_absent(plan_path(args.target, args.request_id), plan_template(args.request_id, state["objective"]), force=args.force)
    append_history(args.target, args.request_id, "plan.created" if wrote else "plan.exists", "Plan artifact checked")
    print_json({"request_id": args.request_id, "path": str(plan_path(args.target, args.request_id)), "written": wrote})


def validate(args: argparse.Namespace) -> None:
    missing = validate_plan(args.target, args.request_id)
    print_json({"request_id": args.request_id, "valid": not missing, "missing_sections": missing})


def approve(args: argparse.Namespace) -> None:
    missing = validate_plan(args.target, args.request_id)
    if missing:
        raise SystemExit(f"ERROR: plan is missing sections: {', '.join(missing)}")
    state = load_state(args.target, args.request_id)
    state["approvals"]["plan"] = True
    state["status"] = "plan_approved"
    state["next_action"] = "Create tasks.md."
    save_state(args.target, args.request_id, state)
    append_history(args.target, args.request_id, "approval.recorded", "Approved plan gate", artifact="plan.md")
    print_json({"request_id": args.request_id, "approved": "plan"})


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, func in [("create", create), ("validate", validate), ("approve", approve)]:
        item = sub.add_parser(name)
        item.add_argument("--target", default=".")
        item.add_argument("--request-id", required=True)
        if name == "create":
            item.add_argument("--force", action="store_true")
        item.set_defaults(func=func)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_guard(run)
