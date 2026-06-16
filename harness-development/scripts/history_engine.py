#!/usr/bin/env python3
"""Append and query request history events."""

from __future__ import annotations

import argparse

from harness_common import append_history, main_guard, parse_json_arg, print_json, read_jsonl, history_path


def append(args: argparse.Namespace) -> None:
    data = parse_json_arg(args.data_json) or {}
    event = append_history(args.target, args.request_id, args.type, args.summary, **data)
    print_json(event)


def list_events(args: argparse.Namespace) -> None:
    events = read_jsonl(history_path(args.target, args.request_id))
    if args.type:
        events = [event for event in events if event.get("type") == args.type]
    print_json({"request_id": args.request_id, "events": events})


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("append")
    add.add_argument("--target", default=".")
    add.add_argument("--request-id", required=True)
    add.add_argument("--type", required=True)
    add.add_argument("--summary", required=True)
    add.add_argument("--data-json", default="")
    add.set_defaults(func=append)
    list_parser = sub.add_parser("list")
    list_parser.add_argument("--target", default=".")
    list_parser.add_argument("--request-id", required=True)
    list_parser.add_argument("--type", default="")
    list_parser.set_defaults(func=list_events)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_guard(run)
