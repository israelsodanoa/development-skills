#!/usr/bin/env python3
"""Audit project-memory links, ownership, and freshness hints."""

from __future__ import annotations

import argparse
from pathlib import Path

from harness_common import harness_dir, load_json, main_guard, now_iso, print_json, target_root


def audit(args: argparse.Namespace) -> None:
    root = target_root(args.target)
    index_path = harness_dir(root) / "memory" / "memory-index.json"
    data = load_json(index_path, default={})
    problems = []
    sections = ["architecture", "testing", "domain", "tools", "decisions", "quality"]
    for section in sections:
        for item in data.get(section, []):
            rel = item.get("path", "")
            if rel and not (root / rel).exists():
                problems.append({"section": section, "path": rel, "problem": "missing"})
            if not item.get("owner"):
                problems.append({"section": section, "path": rel, "problem": "missing owner"})
            if item.get("freshness") in {"stale", "unverified", ""}:
                problems.append({"section": section, "path": rel, "problem": f"freshness={item.get('freshness', 'unset')}"})
    report = {
        "generated_at": now_iso(),
        "index": str(index_path),
        "problem_count": len(problems),
        "problems": problems,
    }
    output = Path(args.output) if args.output else harness_dir(root) / "reports" / "docs-freshness.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(__import__("json").dumps(report, indent=2) + "\n", encoding="utf-8")
    print_json(report)


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    audit(args)


if __name__ == "__main__":
    main_guard(run)
