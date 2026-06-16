#!/usr/bin/env python3
"""Create, validate, and approve request specifications."""

from __future__ import annotations

import argparse

from harness_common import append_history, load_state, main_guard, print_json, save_state, spec_path, validate_spec, write_if_absent


def spec_template(request_id: str, objective: str) -> str:
    return f"""# Spec: {request_id}

## Objective

{objective}

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

Document the nearest tests, required regression level, coverage expectations, and exact verification commands.

## Boundaries

- Always: preserve unrelated user work; record evidence in `.harness`.
- Ask first: dependencies, CI, migrations, Docker/Sonar execution, external systems, releases.
- Never: commit secrets, fabricate evidence, remove failing tests to claim success.

## Success Criteria

- [ ] Define a concrete, testable criterion before planning.

## Open Questions

- None recorded yet.
"""


def create(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    wrote = write_if_absent(spec_path(args.target, args.request_id), spec_template(args.request_id, state["objective"]), force=args.force)
    append_history(args.target, args.request_id, "spec.created" if wrote else "spec.exists", "Spec artifact checked")
    print_json({"request_id": args.request_id, "path": str(spec_path(args.target, args.request_id)), "written": wrote})


def validate(args: argparse.Namespace) -> None:
    missing = validate_spec(args.target, args.request_id)
    print_json({"request_id": args.request_id, "valid": not missing, "missing_sections": missing})


def approve(args: argparse.Namespace) -> None:
    missing = validate_spec(args.target, args.request_id)
    if missing:
        raise SystemExit(f"ERROR: spec is missing sections: {', '.join(missing)}")
    state = load_state(args.target, args.request_id)
    state["approvals"]["spec"] = True
    state["status"] = "spec_approved"
    state["next_action"] = "Create plan.md."
    save_state(args.target, args.request_id, state)
    append_history(args.target, args.request_id, "approval.recorded", "Approved spec gate", artifact="spec.md")
    print_json({"request_id": args.request_id, "approved": "spec"})


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
