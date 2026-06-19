#!/usr/bin/env python3
"""Generate and run Docker-based Sonar quality controls."""

from __future__ import annotations

import argparse
import base64
import json
import urllib.error
import urllib.parse
import urllib.request

from harness_common import (
    HarnessError,
    append_history,
    detect_stack,
    fetch_sonar_status,
    generate_sonar_templates,
    harness_dir,
    main_guard,
    print_json,
    read_sonar_config,
    request_dir,
    require_docker_compose,
    run_shell,
    sonar_compose_project_name,
    start_sonarqube,
    stop_sonarqube,
    target_root,
    update_sonar_runtime_status,
)


def detect(args: argparse.Namespace) -> None:
    print_json({"target": str(target_root(args.target)), "stack": detect_stack(args.target)})


def configure(args: argparse.Namespace) -> None:
    result = generate_sonar_templates(
        args.target,
        force=args.force,
        host_port=args.sonar_port,
        project_key=args.sonar_project_key or None,
        project_name=args.sonar_project_name or None,
    )
    print_json(
        {
            "target": str(target_root(args.target)),
            "sonar_dir": str(harness_dir(args.target) / "sonar"),
            **result,
        }
    )


def up(args: argparse.Namespace) -> None:
    if not args.approved:
        raise HarnessError("Starting SonarQube is approval-required because it runs Docker containers")
    generate_sonar_templates(
        args.target,
        force=args.force,
        host_port=args.sonar_port,
        project_key=args.sonar_project_key or None,
        project_name=args.sonar_project_name or None,
    )
    print_json(start_sonarqube(args.target, timeout_seconds=args.sonar_timeout))


def status(args: argparse.Namespace) -> None:
    current = fetch_sonar_status(args.target, timeout=args.timeout)
    status_name = "running" if current.get("ok") else "unhealthy"
    config = update_sonar_runtime_status(args.target, status_name, last_error="" if current.get("ok") else str(current), extra={"last_health": current})
    print_json({"ok": current.get("ok"), "health": current, "config": config})
    if not current.get("ok"):
        raise SystemExit(1)


def down(args: argparse.Namespace) -> None:
    if not args.approved:
        raise HarnessError("Stopping SonarQube is approval-required because it changes Docker runtime state")
    print_json(stop_sonarqube(args.target))


def configured_host_port(config: dict, default: int) -> int:
    try:
        return int(config.get("docker", {}).get("host_port") or default)
    except (TypeError, ValueError):
        return default


def needs_local_template_refresh(compose: object, config: dict) -> bool:
    if config.get("required_environment"):
        return True
    if config.get("scanner_authentication") != "local_anonymous":
        return True
    if not config.get("quality_gate", {}).get("wait"):
        return True
    if not hasattr(compose, "exists") or not compose.exists():
        return True
    text = compose.read_text(encoding="utf-8")
    host_port = configured_host_port(config, 9000)
    return (
        "SONAR_TOKEN" in text
        or "SONAR_FORCEAUTHENTICATION" not in text
        or "sonar.qualitygate.wait=true" not in text
        or f'"{host_port}:9000"' not in text
    )


def sonar_api_request(root, path: str, data: dict[str, str] | None = None, timeout: int = 20) -> dict:
    config = read_sonar_config(root)
    base_url = config.get("urls", {}).get("host", "http://localhost:9000").rstrip("/")
    url = f"{base_url}{path}"
    body = urllib.parse.urlencode(data).encode("utf-8") if data is not None else None
    request = urllib.request.Request(url, data=body, method="POST" if data is not None else "GET")
    request.add_header("Authorization", "Basic " + base64.b64encode(b"admin:admin").decode("ascii"))
    if data is not None:
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8")
            return {"ok": 200 <= response.status < 300, "status": response.status, "body": text, "json": parse_json_body(text)}
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "body": text, "json": parse_json_body(text)}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "status": 0, "body": str(exc), "json": None}


def parse_json_body(text: str) -> object | None:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def response_mentions_existing(response: dict) -> bool:
    body = str(response.get("body", "")).lower()
    return "already exists" in body or "already have" in body


def ensure_local_project(root) -> dict:
    config = read_sonar_config(root)
    project = config.get("project", {})
    project_key = project.get("project_key")
    project_name = project.get("project_name") or project_key
    if not project_key:
        raise HarnessError("Missing Sonar project key in sonar-config.json")

    global_grants: list[str] = []
    for permission in ["scan", "provisioning"]:
        grant = sonar_api_request(
            root,
            "/api/permissions/add_group",
            {"groupName": "anyone", "permission": permission},
        )
        if grant.get("ok") or response_mentions_existing(grant):
            global_grants.append(permission)
            continue
        raise HarnessError(f"Failed to grant local Sonar global {permission} permission: HTTP {grant.get('status')} {grant.get('body')}")

    query = urllib.parse.urlencode({"projects": project_key})
    search = sonar_api_request(root, f"/api/projects/search?{query}")
    if not search.get("ok"):
        raise HarnessError(f"Failed to inspect local Sonar project: HTTP {search.get('status')} {search.get('body')}")
    components = (search.get("json") or {}).get("components", []) if isinstance(search.get("json"), dict) else []
    created = False
    if not components:
        create = sonar_api_request(root, "/api/projects/create", {"project": project_key, "name": project_name, "visibility": "public"})
        if not create.get("ok") and not response_mentions_existing(create):
            raise HarnessError(f"Failed to create local Sonar project: HTTP {create.get('status')} {create.get('body')}")
        created = create.get("ok")

    granted: list[str] = []
    for permission in ["user", "scan"]:
        grant = sonar_api_request(
            root,
            "/api/permissions/add_group",
            {"groupName": "anyone", "permission": permission, "projectKey": project_key},
        )
        if grant.get("ok") or response_mentions_existing(grant):
            granted.append(permission)
            continue
        raise HarnessError(f"Failed to grant local Sonar {permission} permission: HTTP {grant.get('status')} {grant.get('body')}")

    payload = {"project_key": project_key, "created": created, "global_grants_to_anyone": global_grants, "project_grants_to_anyone": granted}
    update_sonar_runtime_status(root, "project_ready", extra={"last_project_bootstrap": payload})
    return payload


def run_sonar(args: argparse.Namespace) -> None:
    if not args.approved:
        raise HarnessError("Sonar execution is approval-required because it may pull Docker images and run services")
    root = target_root(args.target)
    sonar_dir = root / ".harness" / "sonar"
    compose = sonar_dir / "docker-compose.sonar.yml"
    properties = sonar_dir / "sonar-project.properties"
    config = read_sonar_config(root)
    refresh = needs_local_template_refresh(compose, config) if config else False
    if not compose.exists() or not properties.exists() or not config or refresh:
        generate_sonar_templates(root, force=refresh, host_port=configured_host_port(config, args.sonar_port))
    require_docker_compose(root)
    health = fetch_sonar_status(root)
    if not health.get("ok"):
        runtime = start_sonarqube(root, timeout_seconds=args.sonar_timeout)
        health = runtime["health"]
    project_bootstrap = ensure_local_project(root)
    if not compose.exists():
        raise HarnessError(f"Missing Sonar compose file: {compose}")
    command = f'docker compose -p "{sonar_compose_project_name(root)}" -f "{compose}" run --rm sonar-scanner'
    result = run_shell(command, root)
    evidence_root = request_dir(root, args.request_id) / "evidence" / "sonar" if args.request_id else root / ".harness" / "reports"
    evidence_root.mkdir(parents=True, exist_ok=True)
    log_path = evidence_root / "sonar-scan.log"
    log_path.write_text(f"$ {command}\n\n# stdout\n{result.stdout}\n\n# stderr\n{result.stderr}\n", encoding="utf-8")
    payload = {"command": command, "returncode": result.returncode, "log_path": str(log_path)}
    if args.request_id:
        append_history(root, args.request_id, "quality.sonar", "Ran Docker Sonar scanner", **payload)
    status_name = "scan_passed" if result.returncode == 0 else "scan_failed"
    update_sonar_runtime_status(root, status_name, last_error="" if result.returncode == 0 else result.stderr.strip() or result.stdout.strip(), extra={"last_scan": payload})
    print_json({"ok": result.returncode == 0, "health": health, "project_bootstrap": project_bootstrap, "config": read_sonar_config(root), **payload})
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def add_config_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target", default=".")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--sonar-port", type=int, default=9000)
    parser.add_argument("--sonar-project-key", default="")
    parser.add_argument("--sonar-project-name", default="")


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    detect_parser = sub.add_parser("detect")
    detect_parser.add_argument("--target", default=".")
    detect_parser.set_defaults(func=detect)
    configure_parser = sub.add_parser("configure")
    add_config_args(configure_parser)
    configure_parser.set_defaults(func=configure)
    generate_parser = sub.add_parser("generate")
    add_config_args(generate_parser)
    generate_parser.set_defaults(func=configure)
    up_parser = sub.add_parser("up")
    add_config_args(up_parser)
    up_parser.add_argument("--sonar-timeout", type=int, default=180)
    up_parser.add_argument("--approved", action="store_true")
    up_parser.set_defaults(func=up)
    status_parser = sub.add_parser("status")
    status_parser.add_argument("--target", default=".")
    status_parser.add_argument("--timeout", type=int, default=5)
    status_parser.set_defaults(func=status)
    down_parser = sub.add_parser("down")
    down_parser.add_argument("--target", default=".")
    down_parser.add_argument("--approved", action="store_true")
    down_parser.set_defaults(func=down)
    runner = sub.add_parser("run")
    runner.add_argument("--target", default=".")
    runner.add_argument("--request-id", default="")
    runner.add_argument("--sonar-port", type=int, default=9000)
    runner.add_argument("--sonar-timeout", type=int, default=180)
    runner.add_argument("--approved", action="store_true")
    runner.set_defaults(func=run_sonar)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_guard(run)
