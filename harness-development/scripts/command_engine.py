#!/usr/bin/env python3
"""Validate and run registered commands with evidence capture."""

from __future__ import annotations

import argparse
import os
import re

from harness_common import (
    HarnessError,
    append_history,
    command_by_id,
    harness_dir,
    load_state,
    main_guard,
    now_iso,
    print_json,
    refresh_continuation_handoff,
    refresh_evidence_manifest,
    request_dir,
    run_shell,
    save_state,
    skill_scripts_path,
    target_root,
    validate_registry,
)


def validate(args: argparse.Namespace) -> None:
    problems = validate_registry(args.target)
    print_json({"valid": not problems, "problems": problems})


def run_command(args: argparse.Namespace) -> None:
    command = command_by_id(args.target, args.id)
    if command.get("approval_required") and not args.approved:
        raise HarnessError(f"Command {args.id} is approval-required; rerun with --approved after approval is recorded")
    root = target_root(args.target)
    workdir = (root / command.get("workdir", ".")).resolve()
    env = {
        "HARNESS_TARGET": str(root),
        "HARNESS_REQUEST_ID": args.request_id or "",
        "HARNESS_SKILL_SCRIPTS": str(skill_scripts_path()),
    }
    result = run_shell(command["command"], workdir, env=env)
    safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "-", args.id)
    evidence_root = request_dir(root, args.request_id) / "evidence" / "commands" if args.request_id else harness_dir(root) / "reports"
    evidence_root.mkdir(parents=True, exist_ok=True)
    log_path = evidence_root / f"{now_iso().replace(':', '-')}-{safe_id}.log"
    log_path.write_text(
        f"$ {command['command']}\n\n# stdout\n{result.stdout}\n\n# stderr\n{result.stderr}\n",
        encoding="utf-8",
    )
    payload = {
        "command_id": args.id,
        "command": command["command"],
        "workdir": str(workdir),
        "returncode": result.returncode,
        "log_path": str(log_path),
    }
    if args.request_id:
        state = load_state(root, args.request_id)
        state.setdefault("commands_run", []).append(payload)
        state["next_action"] = "Review command result and continue workflow."
        save_state(root, args.request_id, state)
        append_history(root, args.request_id, "command.run", f"Ran {args.id}", **payload)
        refresh_evidence_manifest(root, args.request_id)
        refresh_continuation_handoff(root, args.request_id)
    print_json({"ok": result.returncode == 0, **payload})
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--target", default=".")
    validate_parser.set_defaults(func=validate)
    runner = sub.add_parser("run")
    runner.add_argument("--target", default=".")
    runner.add_argument("--request-id", default=os.environ.get("HARNESS_REQUEST_ID", ""))
    runner.add_argument("--id", required=True)
    runner.add_argument("--approved", action="store_true")
    runner.set_defaults(func=run_command)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_guard(run)
