#!/usr/bin/env python3
"""Create, validate, and approve implementation task lists."""

from __future__ import annotations

import argparse

from harness_common import HarnessError, append_history, load_state, main_guard, print_json, save_state, tasks_path, validate_tasks, write_if_absent


def tasks_template(request_id: str) -> str:
    return f"""# Tasks: {request_id}

- [ ] Task: Replace with first implementation slice
  - Acceptance: The slice satisfies the relevant success criteria from `spec.md`.
  - Verify: Run the registered targeted check and record evidence.
  - Dependencies: None
  - Files: Identify likely touched files before implementation.

## Checkpoint

- [ ] State and history are updated.
- [ ] Required verification evidence is recorded.
"""


def create(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    if not state.get("approvals", {}).get("plan"):
        raise HarnessError("Cannot create tasks.md until the plan gate is approved")
    wrote = write_if_absent(tasks_path(args.target, args.request_id), tasks_template(args.request_id), force=args.force)
    append_history(args.target, args.request_id, "tasks.created" if wrote else "tasks.exists", "Tasks artifact checked")
    print_json({"request_id": args.request_id, "path": str(tasks_path(args.target, args.request_id)), "written": wrote})


def validate(args: argparse.Namespace) -> None:
    missing = validate_tasks(args.target, args.request_id)
    print_json({"request_id": args.request_id, "valid": not missing, "missing_markers": missing})


def approve(args: argparse.Namespace) -> None:
    missing = validate_tasks(args.target, args.request_id)
    if missing:
        raise SystemExit(f"ERROR: tasks.md is missing markers: {', '.join(missing)}")
    state = load_state(args.target, args.request_id)
    state["approvals"]["tasks"] = True
    state["status"] = "tasks_approved"
    state["next_action"] = "Transition to IMPLEMENT and complete tasks one at a time."
    save_state(args.target, args.request_id, state)
    append_history(args.target, args.request_id, "approval.recorded", "Approved tasks gate", artifact="tasks.md")
    print_json({"request_id": args.request_id, "approved": "tasks"})


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
