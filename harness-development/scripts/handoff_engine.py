#!/usr/bin/env python3
"""Create specialist-agent and continuation handoff packets."""

from __future__ import annotations

import argparse

from harness_common import append_history, handoff_path, main_guard, print_json, render_handoff_packet


def create(args: argparse.Namespace) -> None:
    path = handoff_path(args.target, args.request_id, args.specialist, stable=args.stable)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_handoff_packet(
            args.target,
            args.request_id,
            specialist=args.specialist,
            completed=args.completed,
            pending=args.pending,
            risks=args.risk,
            next_action=args.next_action,
        ),
        encoding="utf-8",
    )
    append_history(args.target, args.request_id, "handoff.created", f"Created {args.specialist} handoff", path=str(path))
    print_json({"request_id": args.request_id, "specialist": args.specialist, "path": str(path)})


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".")
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--specialist", choices=["architecture", "security", "test", "ui", "product", "release", "continuation"], required=True)
    parser.add_argument("--completed", action="append", default=[])
    parser.add_argument("--pending", action="append", default=[])
    parser.add_argument("--risk", action="append", default=[])
    parser.add_argument("--next-action", default="")
    parser.add_argument("--stable", action="store_true", help="Write handoffs/<specialist>.md instead of a timestamped packet.")
    args = parser.parse_args()
    create(args)


if __name__ == "__main__":
    main_guard(run)
