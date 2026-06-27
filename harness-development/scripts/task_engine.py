#!/usr/bin/env python3
"""Create, validate, and approve implementation task lists."""

from __future__ import annotations

import argparse

from harness_common import (
    HarnessError,
    append_history,
    ensure_planning_quality_state,
    load_state,
    main_guard,
    now_iso,
    print_json,
    save_state,
    tasks_path,
    validate_tasks_artifact,
    write_if_absent,
)


def tasks_template(request_id: str) -> str:
    return f"""# Tasks: {request_id}

## Task T001: Convert The First Plan Slice Into An Atomic Change

- Task: Implement one independently verifiable XS/S change from the approved plan.
- Outcome: One success criterion from `spec.md` is moved closer to verified completion without unrelated edits.
- Exact Scope: One cohesive code, test, documentation, or harness-artifact change selected from the approved plan.
- Non-Scope: Unrelated refactors, dependency additions, release work, and broad cleanup outside the selected slice.
- Size: XS
- Acceptance:
  - The selected change is complete for its narrow scope.
  - The implementation remains compatible with the approved plan and spec boundaries.
- Scenario:
  - Given the approved intake, spec, and plan
  - When this atomic task is implemented and verified
  - Then the matching acceptance criterion has concrete evidence
- Verify: Run the closest targeted command or manual evidence check and record the result.
- Dependencies: Approved plan gate.
- Files: `.harness/requests/{request_id}/tasks.md`, plus the concrete implementation file path selected before editing.
- Risk Notes: The main risk is choosing a task that is too broad; split again if it touches independent subsystems.
- Rollback/Repair: Revert only the selected task's changes or repair the smallest failing check attribution.
- Parallelization: Sequential until concrete files and dependencies are known.

## Checkpoint

- [ ] State and history are updated.
- [ ] Required verification evidence is recorded.
- [ ] No task is larger than S; split M/L/XL work before implementation.
"""


def create(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    if not state.get("approvals", {}).get("plan"):
        raise HarnessError("Cannot create tasks.md until the plan gate is approved")
    wrote = write_if_absent(tasks_path(args.target, args.request_id), tasks_template(args.request_id), force=args.force)
    append_history(args.target, args.request_id, "tasks.created" if wrote else "tasks.exists", "Tasks artifact checked")
    print_json({"request_id": args.request_id, "path": str(tasks_path(args.target, args.request_id)), "written": wrote})


def validate(args: argparse.Namespace) -> None:
    result = validate_tasks_artifact(args.target, args.request_id)
    print_json({
        "request_id": args.request_id,
        "valid": not result["missing_markers"] and not result["quality_problems"],
        "missing_markers": result["missing_markers"],
        "quality_problems": result["quality_problems"],
        "task_count": result["task_count"],
    })


def approve(args: argparse.Namespace) -> None:
    result = validate_tasks_artifact(args.target, args.request_id)
    problems = []
    if result["missing_markers"]:
        problems.append("missing markers: " + ", ".join(result["missing_markers"]))
    if result["quality_problems"]:
        problems.append("quality problems: " + "; ".join(result["quality_problems"]))
    if problems:
        raise SystemExit("ERROR: tasks.md is invalid: " + "; ".join(problems))
    state = load_state(args.target, args.request_id)
    quality = ensure_planning_quality_state(state)
    quality["tasks"] = {
        "status": "valid",
        "minimum_size": "XS/S",
        "validated_at": now_iso(),
        "task_count": result["task_count"],
    }
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
