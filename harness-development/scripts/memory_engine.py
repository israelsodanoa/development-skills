#!/usr/bin/env python3
"""Maintain project memory, known failures, and control gaps."""

from __future__ import annotations

import argparse

from harness_common import harness_dir, load_json, main_guard, now_iso, parse_json_arg, print_json, write_json


def path_for(target: str, artifact: str):
    mapping = {
        "index": harness_dir(target) / "memory" / "memory-index.json",
        "known-failures": harness_dir(target) / "memory" / "known-failures.json",
        "control-gaps": harness_dir(target) / "memory" / "control-gaps.json",
    }
    return mapping[artifact]


def show(args: argparse.Namespace) -> None:
    print_json(load_json(path_for(args.target, args.artifact)))


def add_gap(args: argparse.Namespace) -> None:
    path = path_for(args.target, "control-gaps")
    data = load_json(path, default={"schema_version": 1, "gaps": []})
    data.setdefault("gaps", []).append(
        {
            "id": f"gap-{len(data.get('gaps', [])) + 1}",
            "type": args.type,
            "summary": args.summary,
            "severity": args.severity,
            "status": "open",
            "created_at": now_iso(),
        }
    )
    write_json(path, data)
    print_json(data["gaps"][-1])


def add_failure(args: argparse.Namespace) -> None:
    path = path_for(args.target, "known-failures")
    data = load_json(path, default={"schema_version": 1, "failures": []})
    data.setdefault("failures", []).append(
        {
            "id": f"failure-{len(data.get('failures', [])) + 1}",
            "summary": args.summary,
            "control_needed": args.control_needed,
            "created_at": now_iso(),
        }
    )
    write_json(path, data)
    print_json(data["failures"][-1])


def add_source(args: argparse.Namespace) -> None:
    path = path_for(args.target, "index")
    data = load_json(path, default={"schema_version": 1})
    section = data.setdefault(args.section, [])
    item = parse_json_arg(args.data_json) or {}
    item.setdefault("path", args.path)
    item.setdefault("reason", args.reason)
    item.setdefault("freshness", "unverified")
    item.setdefault("updated_at", now_iso())
    section.append(item)
    data["updated_at"] = now_iso()
    write_json(path, data)
    print_json(item)


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    show_parser = sub.add_parser("show")
    show_parser.add_argument("--target", default=".")
    show_parser.add_argument("--artifact", choices=["index", "known-failures", "control-gaps"], default="index")
    show_parser.set_defaults(func=show)
    gap = sub.add_parser("add-gap")
    gap.add_argument("--target", default=".")
    gap.add_argument("--type", required=True)
    gap.add_argument("--summary", required=True)
    gap.add_argument("--severity", default="medium")
    gap.set_defaults(func=add_gap)
    failure = sub.add_parser("add-known-failure")
    failure.add_argument("--target", default=".")
    failure.add_argument("--summary", required=True)
    failure.add_argument("--control-needed", default="")
    failure.set_defaults(func=add_failure)
    source = sub.add_parser("add-source")
    source.add_argument("--target", default=".")
    source.add_argument("--section", choices=["architecture", "testing", "domain", "tools", "decisions", "quality"], required=True)
    source.add_argument("--path", required=True)
    source.add_argument("--reason", required=True)
    source.add_argument("--data-json", default="")
    source.set_defaults(func=add_source)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_guard(run)
