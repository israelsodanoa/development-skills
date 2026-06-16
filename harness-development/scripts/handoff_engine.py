#!/usr/bin/env python3
"""Create specialist-agent and continuation handoff packets."""

from __future__ import annotations

import argparse
import re

from harness_common import append_history, load_state, main_guard, now_iso, print_json, read_jsonl, request_dir, history_path


def create(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    events = read_jsonl(history_path(args.target, args.request_id))[-20:]
    name = re.sub(r"[^A-Za-z0-9_.-]+", "-", args.specialist.lower())
    path = request_dir(args.target, args.request_id) / "handoffs" / f"{now_iso().replace(':', '-')}-{name}.md"
    lines = [
        f"# Handoff: {args.specialist}",
        "",
        f"Generated: {now_iso()}",
        f"Request ID: {args.request_id}",
        f"Objective: {state.get('objective')}",
        f"Current phase: {state.get('phase')}",
        f"Status: {state.get('status')}",
        "",
        "## Completed",
        *(f"- {item}" for item in args.completed),
        "",
        "## Pending",
        *(f"- {item}" for item in args.pending),
        "",
        "## Decisions",
        *(f"- {item.get('summary')}" for item in events if "decision" in item.get("type", "")),
        "",
        "## Risks",
        *(f"- {risk}" for risk in args.risk),
        "",
        "## Next Action",
        args.next_action or state.get("next_action", ""),
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
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
    args = parser.parse_args()
    create(args)


if __name__ == "__main__":
    main_guard(run)
