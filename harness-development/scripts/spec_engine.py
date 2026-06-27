#!/usr/bin/env python3
"""Create, validate, and approve request specifications."""

from __future__ import annotations

import argparse

from harness_common import (
    HarnessError,
    append_history,
    ensure_intake_state,
    intake_gate_problems,
    load_state,
    main_guard,
    print_json,
    save_state,
    spec_path,
    validate_spec,
    write_if_absent,
)


def markdown_items(items: list, default: str) -> str:
    if not items:
        return f"- {default}"
    lines: list[str] = []
    for item in items:
        if isinstance(item, dict):
            text = item.get("text") or item.get("value") or str(item)
        else:
            text = str(item)
        lines.append(f"- {text}")
    return "\n".join(lines)


def spec_template(request_id: str, state: dict) -> str:
    ensure_intake_state(state)
    objective = state.get("objective", "")
    intake_answers = state.get("intake", {}).get("answers", {})
    verification = intake_answers.get("verification_expectations", {}).get("value", "Document the nearest tests, required regression level, coverage expectations, and exact verification commands.")
    constraints = intake_answers.get("constraints", {}).get("value", "No additional constraints recorded.")
    audience = intake_answers.get("audience", {}).get("value", "To be confirmed from intake.")
    desired_outcome = intake_answers.get("desired_outcome", {}).get("value", "To be confirmed from intake.")
    assumptions = state.get("assumptions", [])
    return f"""# Spec: {request_id}

## Objective

{objective}

Audience: {audience}

Desired outcome: {desired_outcome}

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

{verification}

## Boundaries

- Always: preserve unrelated user work; record evidence in `.harness`.
- Ask first: dependencies, CI, migrations, Docker/Sonar execution, external systems, releases.
- Never: commit secrets, fabricate evidence, remove failing tests to claim success.
- Constraints: {constraints}

### Non-Goals

{markdown_items(state.get("non_goals", []), "None recorded.")}

## Success Criteria

{markdown_items(state.get("acceptance_criteria", []), "Define a concrete, testable criterion before planning.")}

## Assumptions

{markdown_items(assumptions, "None recorded.")}

## Open Questions

{markdown_items(state.get("open_questions", []), "None recorded.")}
"""


def create(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    wrote = write_if_absent(spec_path(args.target, args.request_id), spec_template(args.request_id, state), force=args.force)
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
    intake_problems = intake_gate_problems(state)
    if intake_problems:
        raise HarnessError(f"Cannot approve spec; intake is incomplete: {'; '.join(intake_problems)}")
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
