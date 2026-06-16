#!/usr/bin/env python3
"""Shared utilities for the harness-development skill scripts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


PHASES = ["SPECIFY", "PLAN", "TASKS", "IMPLEMENT", "VERIFY", "CLOSEOUT"]
PHASE_ORDER = {phase: index for index, phase in enumerate(PHASES)}
GATE_BY_TARGET_PHASE = {"PLAN": "spec", "TASKS": "plan", "IMPLEMENT": "tasks"}

SPEC_SECTIONS = [
    "Objective",
    "Tech Stack",
    "Commands",
    "Project Structure",
    "Code Style",
    "Testing Strategy",
    "Boundaries",
    "Success Criteria",
    "Open Questions",
]

PLAN_SECTIONS = [
    "Overview",
    "Implementation Strategy",
    "Verification Strategy",
    "Risks",
    "Open Questions",
]

TASKS_MARKERS = ["Task:", "Acceptance:", "Verify:", "Dependencies:", "Files:"]


class HarnessError(RuntimeError):
    """Raised for LLM-readable harness failures."""


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def fail(message: str, code: int = 1) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(code)


def load_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise HarnessError(f"Missing JSON file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HarnessError(f"Malformed JSON in {path}: {exc}") from exc


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.open("a", encoding="utf-8").write(json.dumps(event, sort_keys=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise HarnessError(f"Malformed JSONL in {path}:{line_no}: {exc}") from exc
    return events


def target_root(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def harness_dir(target: str | Path) -> Path:
    return target_root(target) / ".harness"


def ensure_harness(target: str | Path) -> Path:
    root = harness_dir(target)
    if not root.exists():
        raise HarnessError(f"No .harness folder found in {target_root(target)}. Run init_project_harness.py first.")
    return root


def config_path(target: str | Path) -> Path:
    return harness_dir(target) / "config" / "harness.json"


def command_registry_path(target: str | Path) -> Path:
    return harness_dir(target) / "config" / "command-registry.json"


def requests_root(target: str | Path) -> Path:
    return harness_dir(target) / "requests"


def request_dir(target: str | Path, request_id: str) -> Path:
    return requests_root(target) / request_id


def state_path(target: str | Path, request_id: str) -> Path:
    return request_dir(target, request_id) / "state.json"


def history_path(target: str | Path, request_id: str) -> Path:
    return request_dir(target, request_id) / "history.jsonl"


def spec_path(target: str | Path, request_id: str) -> Path:
    return request_dir(target, request_id) / "spec.md"


def plan_path(target: str | Path, request_id: str) -> Path:
    return request_dir(target, request_id) / "plan.md"


def tasks_path(target: str | Path, request_id: str) -> Path:
    return request_dir(target, request_id) / "tasks.md"


def verification_path(target: str | Path, request_id: str) -> Path:
    return request_dir(target, request_id) / "verification-report.md"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or "request"


def make_request_id(title: str) -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-{slugify(title)}"


def default_state(request_id: str, objective: str) -> dict[str, Any]:
    stamp = now_iso()
    return {
        "schema_version": 1,
        "request_id": request_id,
        "objective": objective,
        "phase": "SPECIFY",
        "status": "draft",
        "approvals": {"spec": False, "plan": False, "tasks": False},
        "acceptance_criteria": [],
        "non_goals": [],
        "risk_level": {"level": "unknown", "reason": ""},
        "permissions": {"always": [], "ask_first": [], "never": []},
        "context_sources": [],
        "inspected_files": [],
        "changed_files": [],
        "decisions": [],
        "assumptions": [],
        "open_questions": [],
        "commands_run": [],
        "verification_status": [],
        "failure_attributions": [],
        "interventions": [],
        "next_action": "Write and validate spec.md.",
        "created_at": stamp,
        "updated_at": stamp,
    }


def load_state(target: str | Path, request_id: str) -> dict[str, Any]:
    return load_json(state_path(target, request_id))


def save_state(target: str | Path, request_id: str, state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    write_json(state_path(target, request_id), state)


def history_event(event_type: str, summary: str, **payload: Any) -> dict[str, Any]:
    event = {
        "timestamp": now_iso(),
        "type": event_type,
        "summary": summary,
    }
    event.update({key: value for key, value in payload.items() if value is not None})
    return event


def append_history(target: str | Path, request_id: str, event_type: str, summary: str, **payload: Any) -> dict[str, Any]:
    event = history_event(event_type, summary, **payload)
    append_jsonl(history_path(target, request_id), event)
    return event


def require_sections(markdown_path: Path, sections: Iterable[str]) -> list[str]:
    if not markdown_path.exists():
        raise HarnessError(f"Missing artifact: {markdown_path}")
    text = markdown_path.read_text(encoding="utf-8")
    missing = []
    for section in sections:
        pattern = rf"^##\s+{re.escape(section)}\s*$"
        if not re.search(pattern, text, flags=re.MULTILINE):
            missing.append(section)
    return missing


def validate_spec(target: str | Path, request_id: str) -> list[str]:
    return require_sections(spec_path(target, request_id), SPEC_SECTIONS)


def validate_plan(target: str | Path, request_id: str) -> list[str]:
    return require_sections(plan_path(target, request_id), PLAN_SECTIONS)


def validate_tasks(target: str | Path, request_id: str) -> list[str]:
    path = tasks_path(target, request_id)
    if not path.exists():
        raise HarnessError(f"Missing artifact: {path}")
    text = path.read_text(encoding="utf-8")
    return [marker for marker in TASKS_MARKERS if marker not in text]


def ensure_request_dirs(target: str | Path, request_id: str) -> Path:
    root = request_dir(target, request_id)
    for name in ["handoffs", "prompt-packets", "evidence", "evidence/commands"]:
        (root / name).mkdir(parents=True, exist_ok=True)
    return root


def write_if_absent(path: Path, content: str, force: bool = False) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def detect_stack(target: str | Path) -> dict[str, Any]:
    root = target_root(target)
    markers = {
        "node": ["package.json"],
        "typescript": ["tsconfig.json"],
        "python": ["pyproject.toml", "setup.py", "requirements.txt"],
        "maven": ["pom.xml"],
        "gradle": ["build.gradle", "build.gradle.kts"],
        "go": ["go.mod"],
        "dotnet": [],
    }
    detected: list[str] = []
    evidence: dict[str, list[str]] = {}
    for stack, files in markers.items():
        found = [name for name in files if (root / name).exists()]
        if found:
            detected.append(stack)
            evidence[stack] = found
    csproj = [str(path.relative_to(root)) for path in root.glob("**/*.csproj") if ".harness" not in path.parts]
    if csproj:
        detected.append("dotnet")
        evidence["dotnet"] = csproj[:10]
    if not detected:
        detected.append("generic")
        evidence["generic"] = ["no known stack marker found"]
    primary = choose_primary_stack(detected)
    return {"primary": primary, "detected": detected, "evidence": evidence}


def choose_primary_stack(detected: list[str]) -> str:
    for candidate in ["maven", "gradle", "dotnet", "go", "typescript", "node", "python"]:
        if candidate in detected:
            return candidate
    return detected[0] if detected else "generic"


def sonar_properties(target: str | Path, stack: dict[str, Any]) -> str:
    root = target_root(target)
    project_name = root.name
    key = re.sub(r"[^A-Za-z0-9_.:-]+", "-", project_name).strip("-") or "project"
    primary = stack["primary"]
    lines = [
        f"sonar.projectKey={key}",
        f"sonar.projectName={project_name}",
        "sonar.sourceEncoding=UTF-8",
    ]
    if primary in {"node", "typescript"}:
        lines += [
            "sonar.sources=src",
            "sonar.tests=tests,__tests__,src",
            "sonar.test.inclusions=**/*.test.js,**/*.test.jsx,**/*.test.ts,**/*.test.tsx,**/*.spec.js,**/*.spec.ts",
            "sonar.javascript.lcov.reportPaths=coverage/lcov.info",
        ]
    elif primary == "python":
        lines += [
            "sonar.sources=.",
            "sonar.tests=tests",
            "sonar.python.coverage.reportPaths=coverage.xml",
        ]
    elif primary == "maven":
        lines += [
            "sonar.sources=src/main",
            "sonar.tests=src/test",
            "sonar.coverage.jacoco.xmlReportPaths=target/site/jacoco/jacoco.xml",
        ]
    elif primary == "gradle":
        lines += [
            "sonar.sources=src/main",
            "sonar.tests=src/test",
            "sonar.coverage.jacoco.xmlReportPaths=build/reports/jacoco/test/jacocoTestReport.xml",
        ]
    elif primary == "go":
        lines += [
            "sonar.sources=.",
            "sonar.tests=.",
            "sonar.go.coverage.reportPaths=coverage.out",
        ]
    elif primary == "dotnet":
        lines += [
            "sonar.sources=.",
            "sonar.cs.opencover.reportsPaths=coverage.opencover.xml",
        ]
    else:
        lines += ["sonar.sources=."]
    lines += [
        "sonar.exclusions=**/.git/**,**/.harness/**,**/node_modules/**,**/dist/**,**/build/**,**/coverage/**,**/__pycache__/**,**/bin/**,**/obj/**",
    ]
    return "\n".join(lines) + "\n"


def sonar_compose() -> str:
    return """services:
  sonarqube:
    image: sonarqube:community
    ports:
      - "9000:9000"
    environment:
      SONAR_ES_BOOTSTRAP_CHECKS_DISABLE: "true"
    volumes:
      - sonar_data:/opt/sonarqube/data
      - sonar_extensions:/opt/sonarqube/extensions
      - sonar_logs:/opt/sonarqube/logs

  sonar-scanner:
    image: sonarsource/sonar-scanner-cli:latest
    depends_on:
      - sonarqube
    environment:
      SONAR_HOST_URL: "${SONAR_HOST_URL:-http://sonarqube:9000}"
      SONAR_TOKEN: "${SONAR_TOKEN:?Set SONAR_TOKEN before running the scanner}"
    volumes:
      - ../..:/usr/src
    working_dir: /usr/src
    command: sonar-scanner -Dproject.settings=.harness/sonar/sonar-project.properties

volumes:
  sonar_data:
  sonar_extensions:
  sonar_logs:
"""


def scaffold_source() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "harness-scaffold"


def skill_scripts_path() -> Path:
    return Path(__file__).resolve().parent


def copy_scaffold(target: str | Path, force: bool = False) -> list[str]:
    src = scaffold_source()
    dest = harness_dir(target)
    created: list[str] = []
    if not src.exists():
        raise HarnessError(f"Missing scaffold assets: {src}")
    for path in src.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists() and not force:
            continue
        shutil.copy2(path, out)
        created.append(str(out))
    for name in ["requests", "reports", "memory", "config", "sonar"]:
        (dest / name).mkdir(parents=True, exist_ok=True)
    return created


def update_harness_config(target: str | Path) -> dict[str, Any]:
    path = config_path(target)
    data = load_json(path, default={"schema_version": 1})
    data.setdefault("schema_version", 1)
    data.setdefault("harness_version", "0.1.0")
    data.setdefault("workflow", {"phases": PHASES, "spec_required": True, "plan_required": True, "tasks_required": True})
    data.setdefault(
        "artifact_roots",
        {
            "requests": ".harness/requests",
            "memory": ".harness/memory",
            "reports": ".harness/reports",
            "sonar": ".harness/sonar",
        },
    )
    engine = data.setdefault("engine", {})
    engine["type"] = "codex-skill-python"
    engine["scripts_path"] = str(skill_scripts_path())
    engine.setdefault("initialized_at", now_iso())
    engine["last_updated_at"] = now_iso()
    write_json(path, data)
    return data


def generate_sonar_templates(target: str | Path, force: bool = False) -> dict[str, Any]:
    root = harness_dir(target) / "sonar"
    stack = detect_stack(target)
    compose_written = write_if_absent(root / "docker-compose.sonar.yml", sonar_compose(), force=force)
    props_written = write_if_absent(root / "sonar-project.properties", sonar_properties(target, stack), force=force)
    return {"stack": stack, "compose_written": compose_written, "properties_written": props_written}


def parse_json_arg(value: str | None) -> Any:
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def load_registry(target: str | Path) -> dict[str, Any]:
    data = load_json(command_registry_path(target), default={"schema_version": 1, "commands": []})
    if "commands" not in data or not isinstance(data["commands"], list):
        raise HarnessError("command-registry.json must contain a commands list")
    return data


def command_by_id(target: str | Path, command_id: str) -> dict[str, Any]:
    registry = load_registry(target)
    for command in registry["commands"]:
        if command.get("id") == command_id:
            return command
    raise HarnessError(f"Command not found in registry: {command_id}")


def validate_registry(target: str | Path) -> list[str]:
    required = [
        "id",
        "command",
        "workdir",
        "purpose",
        "when_to_run",
        "expected_runtime",
        "risk",
        "approval_required",
        "required_before_completion",
        "success_signal",
        "failure_protocol",
    ]
    problems: list[str] = []
    data = load_registry(target)
    seen: set[str] = set()
    for index, command in enumerate(data["commands"], start=1):
        missing = [field for field in required if field not in command]
        if missing:
            problems.append(f"commands[{index}] missing fields: {', '.join(missing)}")
        command_id = command.get("id")
        if command_id in seen:
            problems.append(f"duplicate command id: {command_id}")
        if command_id:
            seen.add(command_id)
        risky = str(command.get("risk", "")).lower()
        if any(word in str(command.get("command", "")).lower() for word in ["docker", "deploy", "publish", "migrate", "push"]):
            if not command.get("approval_required") and risky != "safe":
                problems.append(f"{command_id}: risky command should be approval_required")
    return problems


def run_shell(command: str, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(command, cwd=str(cwd), shell=True, text=True, capture_output=True, env=merged_env)


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=False))


def main_guard(fn: Any) -> None:
    try:
        fn()
    except HarnessError as exc:
        fail(str(exc))

