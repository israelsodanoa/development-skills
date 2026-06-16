#!/usr/bin/env python3
"""Summarize request history into an auditable episode report."""

from __future__ import annotations

import argparse
from collections import Counter

from harness_common import history_path, load_state, main_guard, now_iso, print_json, read_jsonl, request_dir


def summarize(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    events = read_jsonl(history_path(args.target, args.request_id))
    counts = Counter(event.get("type", "unknown") for event in events)
    output = args.output or str(request_dir(args.target, args.request_id) / "episode-summary.md")
    lines = [
        f"# Episode Summary: {args.request_id}",
        "",
        f"Generated: {now_iso()}",
        f"Objective: {state.get('objective')}",
        f"Final phase: {state.get('phase')}",
        f"Status: {state.get('status')}",
        "",
        "## Event Counts",
        "",
        *(f"- {key}: {value}" for key, value in sorted(counts.items())),
        "",
        "## Decisions And Approvals",
        "",
        *(f"- {event.get('timestamp')}: {event.get('summary')}" for event in events if "decision" in event.get("type", "") or "approval" in event.get("type", "")),
        "",
        "## Commands And Quality Evidence",
        "",
        *(f"- {event.get('timestamp')}: {event.get('summary')} ({event.get('log_path', '')})" for event in events if "command" in event.get("type", "") or "sonar" in event.get("type", "")),
        "",
        "## Outcome",
        "",
        f"- Next action: {state.get('next_action')}",
    ]
    path = request_dir(args.target, args.request_id) / "episode-summary.md" if not args.output else __import__("pathlib").Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print_json({"request_id": args.request_id, "path": str(path), "event_counts": dict(counts)})


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".")
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    summarize(args)


if __name__ == "__main__":
    main_guard(run)
