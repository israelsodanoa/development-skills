#!/usr/bin/env python3
"""Create and inspect per-request harness folders."""

from __future__ import annotations

import argparse

from harness_common import (
    append_history,
    default_state,
    ensure_harness,
    ensure_request_dirs,
    intake_path,
    intake_template,
    load_state,
    make_request_id,
    main_guard,
    print_json,
    save_state,
    state_path,
    sync_required_request_artifacts,
    write_if_absent,
)


def create(args: argparse.Namespace) -> None:
    ensure_harness(args.target)
    request_id = args.request_id or make_request_id(args.title)
    ensure_request_dirs(args.target, request_id)
    path = state_path(args.target, request_id)
    if path.exists() and not args.force:
        raise SystemExit(f"ERROR: request already exists: {request_id}")
    state = default_state(request_id, args.objective or args.title)
    save_state(args.target, request_id, state)
    append_history(args.target, request_id, "request.created", f"Created request {request_id}", objective=state["objective"])
    intake_written = write_if_absent(intake_path(args.target, request_id), intake_template(request_id, state["objective"]), force=args.force)
    append_history(args.target, request_id, "intake.created" if intake_written else "intake.exists", "Intake artifact checked")
    artifacts = sync_required_request_artifacts(args.target, request_id, force=args.force, event_type="request.artifacts.generated")
    print_json(
        {
            "request_id": request_id,
            "request_dir": str(path.parent),
            "state": str(path),
            "intake": str(intake_path(args.target, request_id)),
            "artifacts": artifacts["artifacts"],
        }
    )


def show(args: argparse.Namespace) -> None:
    print_json(load_state(args.target, args.request_id))


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    create_parser = sub.add_parser("create")
    create_parser.add_argument("--target", default=".")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--objective", default="")
    create_parser.add_argument("--request-id", default="")
    create_parser.add_argument("--force", action="store_true")
    create_parser.set_defaults(func=create)

    show_parser = sub.add_parser("show")
    show_parser.add_argument("--target", default=".")
    show_parser.add_argument("--request-id", required=True)
    show_parser.set_defaults(func=show)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_guard(run)
