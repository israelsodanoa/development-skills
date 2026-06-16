#!/usr/bin/env python3
"""Install or update the persistent .harness scaffold in a target project."""

from __future__ import annotations

import argparse
from pathlib import Path

from harness_common import (
    copy_scaffold,
    generate_sonar_templates,
    main_guard,
    print_json,
    target_root,
    update_harness_config,
    validate_registry,
)


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Target project root.")
    parser.add_argument("--force", action="store_true", help="Overwrite scaffold-managed files.")
    parser.add_argument("--skip-sonar", action="store_true", help="Do not generate Sonar templates.")
    args = parser.parse_args()

    target = target_root(args.target)
    target.mkdir(parents=True, exist_ok=True)
    created = copy_scaffold(target, force=args.force)
    config = update_harness_config(target)
    sonar_created = any(path.endswith("sonar-project.properties") or path.endswith("docker-compose.sonar.yml") for path in created)
    sonar = None if args.skip_sonar else generate_sonar_templates(target, force=args.force or sonar_created)
    registry_problems = validate_registry(target)

    print_json(
        {
            "target": str(target),
            "harness": str(target / ".harness"),
            "created_or_updated": created,
            "engine_scripts_path": config["engine"]["scripts_path"],
            "sonar": sonar,
            "registry_problems": registry_problems,
            "ok": not registry_problems,
        }
    )


if __name__ == "__main__":
    main_guard(run)
