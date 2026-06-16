#!/usr/bin/env python3
"""Generate and run Docker-based Sonar quality controls."""

from __future__ import annotations

import argparse
import os
import shutil

from harness_common import (
    HarnessError,
    append_history,
    generate_sonar_templates,
    harness_dir,
    main_guard,
    print_json,
    request_dir,
    run_shell,
    target_root,
)


def detect(args: argparse.Namespace) -> None:
    result = generate_sonar_templates(args.target, force=False)
    print_json({"target": str(target_root(args.target)), "stack": result["stack"]})


def generate(args: argparse.Namespace) -> None:
    result = generate_sonar_templates(args.target, force=args.force)
    print_json(
        {
            "target": str(target_root(args.target)),
            "sonar_dir": str(harness_dir(args.target) / "sonar"),
            **result,
        }
    )


def run_sonar(args: argparse.Namespace) -> None:
    if not args.approved:
        raise HarnessError("Sonar execution is approval-required because it may pull Docker images and run services")
    if not shutil.which("docker"):
        raise HarnessError("Docker CLI not found; record Sonar execution as blocked or use template-only evidence")
    root = target_root(args.target)
    generate_sonar_templates(root, force=False)
    compose = root / ".harness" / "sonar" / "docker-compose.sonar.yml"
    if not compose.exists():
        raise HarnessError(f"Missing Sonar compose file: {compose}")
    command = f"docker compose -f {compose} run --rm sonar-scanner"
    result = run_shell(command, root, env={"SONAR_HOST_URL": os.environ.get("SONAR_HOST_URL", ""), "SONAR_TOKEN": os.environ.get("SONAR_TOKEN", "")})
    evidence_root = request_dir(root, args.request_id) / "evidence" / "sonar" if args.request_id else root / ".harness" / "reports"
    evidence_root.mkdir(parents=True, exist_ok=True)
    log_path = evidence_root / "sonar-scan.log"
    log_path.write_text(f"$ {command}\n\n# stdout\n{result.stdout}\n\n# stderr\n{result.stderr}\n", encoding="utf-8")
    payload = {"command": command, "returncode": result.returncode, "log_path": str(log_path)}
    if args.request_id:
        append_history(root, args.request_id, "quality.sonar", "Ran Docker Sonar scanner", **payload)
    print_json({"ok": result.returncode == 0, **payload})
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    detect_parser = sub.add_parser("detect")
    detect_parser.add_argument("--target", default=".")
    detect_parser.set_defaults(func=detect)
    generate_parser = sub.add_parser("generate")
    generate_parser.add_argument("--target", default=".")
    generate_parser.add_argument("--force", action="store_true")
    generate_parser.set_defaults(func=generate)
    runner = sub.add_parser("run")
    runner.add_argument("--target", default=".")
    runner.add_argument("--request-id", default="")
    runner.add_argument("--approved", action="store_true")
    runner.set_defaults(func=run_sonar)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_guard(run)
