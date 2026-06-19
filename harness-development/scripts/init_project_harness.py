#!/usr/bin/env python3
"""Install or update the persistent .harness scaffold in a target project."""

from __future__ import annotations

import argparse

from harness_common import (
    copy_scaffold,
    detect_stack,
    generate_sonar_templates,
    main_guard,
    print_json,
    sonar_config_data,
    start_sonarqube,
    target_root,
    update_harness_config,
    validate_registry,
    write_sonar_config,
)


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Target project root.")
    parser.add_argument("--force", action="store_true", help="Overwrite scaffold-managed files.")
    parser.add_argument("--skip-sonar", action="store_true", help="Do not configure or start SonarQube.")
    parser.add_argument("--sonar-timeout", type=int, default=180, help="Seconds to wait for SonarQube health.")
    parser.add_argument("--sonar-port", type=int, default=9000, help="Host port for the SonarQube server.")
    parser.add_argument("--sonar-project-key", default="", help="Override generated Sonar project key.")
    parser.add_argument("--sonar-project-name", default="", help="Override generated Sonar project name.")
    args = parser.parse_args()

    target = target_root(args.target)
    target.mkdir(parents=True, exist_ok=True)
    created = copy_scaffold(target, force=args.force)
    config = update_harness_config(target)
    sonar_created = any("/sonar/" in path for path in created)
    if args.skip_sonar:
        skip_config = sonar_config_data(
            target,
            detect_stack(target),
            host_port=args.sonar_port,
            project_key=args.sonar_project_key or None,
            project_name=args.sonar_project_name or None,
            status="skipped",
            last_error="SonarQube configuration and runtime verification skipped by --skip-sonar.",
        )
        write_sonar_config(target, skip_config)
        sonar = {"ok": True, "skipped": True, "config": skip_config}
    else:
        sonar_config = generate_sonar_templates(
            target,
            force=args.force or sonar_created,
            host_port=args.sonar_port,
            project_key=args.sonar_project_key or None,
            project_name=args.sonar_project_name or None,
        )
        sonar_runtime = start_sonarqube(target, timeout_seconds=args.sonar_timeout)
        sonar = {"ok": True, "configured": sonar_config, "runtime": sonar_runtime}
    registry_problems = validate_registry(target)

    print_json(
        {
            "target": str(target),
            "harness": str(target / ".harness"),
            "created_or_updated": created,
            "engine_scripts_path": config["engine"]["scripts_path"],
            "sonar": sonar,
            "registry_problems": registry_problems,
            "ok": not registry_problems and bool(sonar.get("ok")),
        }
    )


if __name__ == "__main__":
    main_guard(run)
