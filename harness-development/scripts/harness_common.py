#!/usr/bin/env python3
"""Shared utilities for the harness-development skill scripts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
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
    "Planning Standard",
    "Decomposition Map",
    "Dependency Graph",
    "Implementation Strategy",
    "Implementation Slices",
    "Decision Records",
    "Verification Strategy",
    "Verification Matrix",
    "Premortem Risks",
    "Complexity Classification",
    "Sequencing Rationale",
    "Parallelization Boundaries",
    "Risks",
    "Open Questions",
]

TASKS_MARKERS = ["Task:", "Acceptance:", "Verify:", "Dependencies:", "Files:"]

PLANNING_FRAMEWORK_IDS = ["wbs", "invest", "smart", "adr", "rapid", "cynefin", "gherkin", "premortem"]

TASK_REQUIRED_FIELDS = [
    "Task",
    "Outcome",
    "Exact Scope",
    "Non-Scope",
    "Size",
    "Acceptance",
    "Scenario",
    "Verify",
    "Dependencies",
    "Files",
    "Risk Notes",
    "Rollback/Repair",
    "Parallelization",
]

ALLOWED_TASK_SIZES = {"XS", "S"}

PLACEHOLDER_PATTERNS = [
    r"\bplaceholder\b",
    r"\breplace\b",
    r"\btbd\b",
    r"\btodo\b",
    r"\bto be filled\b",
    r"\bto be defined\b",
    r"\bto be discovered\b",
    r"\bidentify likely\b",
    r"\bfill in\b",
    r"\?\?\?",
    r"\[[A-Za-z][^\]\n]+\]",
]

INTAKE_TASK_TYPES = [
    "feature",
    "bug",
    "refactor",
    "ui_runtime",
    "security_reliability",
    "review",
    "harness_improvement",
    "maintenance",
    "unknown",
]

INTAKE_REQUIRED_FIELDS = [
    "objective",
    "task_type",
    "audience",
    "desired_outcome",
    "success_criteria",
    "non_goals",
    "constraints",
    "permissions",
    "verification_expectations",
]

INTAKE_FIELD_LABELS = {
    "objective": "Objective",
    "task_type": "Task type",
    "audience": "Audience or user",
    "desired_outcome": "Desired outcome",
    "success_criteria": "Success criteria",
    "non_goals": "Non-goals",
    "constraints": "Constraints",
    "permissions": "Permissions",
    "verification_expectations": "Verification expectations",
}


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


def intake_path(target: str | Path, request_id: str) -> Path:
    return request_dir(target, request_id) / "intake.md"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or "request"


def make_request_id(title: str) -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-{slugify(title)}"


def default_intake(task_type: str = "unknown") -> dict[str, Any]:
    return {
        "status": "incomplete",
        "task_type": normalize_task_type(task_type),
        "required_fields": list(INTAKE_REQUIRED_FIELDS),
        "answered_fields": [],
        "waived_fields": [],
        "question_rounds": [],
        "answers": {},
        "waivers": {},
    }


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
        "intake": default_intake(),
        "planning_quality": default_planning_quality(),
        "next_action": "Run intake interview and complete intake before spec approval.",
        "created_at": stamp,
        "updated_at": stamp,
    }


def load_state(target: str | Path, request_id: str) -> dict[str, Any]:
    return load_json(state_path(target, request_id))


def save_state(target: str | Path, request_id: str, state: dict[str, Any]) -> None:
    state["updated_at"] = now_iso()
    write_json(state_path(target, request_id), state)


def normalize_task_type(value: str | None) -> str:
    task_type = (value or "unknown").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "ui": "ui_runtime",
        "runtime": "ui_runtime",
        "security": "security_reliability",
        "reliability": "security_reliability",
        "harness": "harness_improvement",
        "improvement": "harness_improvement",
    }
    task_type = aliases.get(task_type, task_type)
    return task_type if task_type in INTAKE_TASK_TYPES else "unknown"


def _unique_strings(values: Iterable[Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result


def default_planning_quality() -> dict[str, Any]:
    return {
        "plan": {"status": "unchecked", "frameworks": [], "validated_at": ""},
        "tasks": {"status": "unchecked", "minimum_size": "XS/S", "validated_at": "", "task_count": 0},
    }


def ensure_planning_quality_state(state: dict[str, Any]) -> dict[str, Any]:
    quality = state.get("planning_quality")
    if not isinstance(quality, dict):
        quality = {}
    default = default_planning_quality()
    for key, value in default.items():
        existing = quality.get(key)
        if not isinstance(existing, dict):
            quality[key] = dict(value)
            continue
        for subkey, subvalue in value.items():
            existing.setdefault(subkey, subvalue)
    state["planning_quality"] = quality
    return quality


def ensure_intake_state(state: dict[str, Any]) -> dict[str, Any]:
    intake = state.get("intake")
    if not isinstance(intake, dict):
        intake = {}
    intake.setdefault("status", "incomplete")
    if intake["status"] not in {"incomplete", "complete"}:
        intake["status"] = "incomplete"
    intake["task_type"] = normalize_task_type(str(intake.get("task_type", "unknown")))

    required = _unique_strings(intake.get("required_fields", []))
    for field in INTAKE_REQUIRED_FIELDS:
        if field not in required:
            required.append(field)
    intake["required_fields"] = required
    intake["answered_fields"] = _unique_strings(intake.get("answered_fields", []))
    intake["waived_fields"] = _unique_strings(intake.get("waived_fields", []))
    intake.setdefault("question_rounds", [])
    if not isinstance(intake["question_rounds"], list):
        intake["question_rounds"] = []
    intake.setdefault("answers", {})
    if not isinstance(intake["answers"], dict):
        intake["answers"] = {}
    intake.setdefault("waivers", {})
    if not isinstance(intake["waivers"], dict):
        intake["waivers"] = {}
    state["intake"] = intake
    return intake


def incomplete_intake_fields(state: dict[str, Any]) -> list[str]:
    intake = ensure_intake_state(state)
    completed = set(intake.get("answered_fields", [])) | set(intake.get("waived_fields", []))
    return [field for field in intake.get("required_fields", []) if field not in completed]


def intake_gate_problems(state: dict[str, Any]) -> list[str]:
    intake = ensure_intake_state(state)
    missing = incomplete_intake_fields(state)
    problems: list[str] = []
    if missing:
        problems.append("missing required fields: " + ", ".join(missing))
    if intake.get("status") != "complete":
        problems.append(f"status is {intake.get('status', 'incomplete')}")
    return problems


def render_intake_document(state: dict[str, Any]) -> str:
    intake = ensure_intake_state(state)
    answers = intake.get("answers", {})
    waivers = intake.get("waivers", {})
    request_id = state.get("request_id", "unknown")
    lines = [
        f"# Intake: {request_id}",
        "",
        "## Normalized Summary",
        "",
        f"- Status: {intake.get('status', 'incomplete')}",
        f"- Task type: {intake.get('task_type', 'unknown')}",
        f"- Objective: {state.get('objective', '') or 'To be confirmed.'}",
        "",
        "## Required Fields",
        "",
    ]
    completed = set(intake.get("answered_fields", [])) | set(intake.get("waived_fields", []))
    for field in intake.get("required_fields", []):
        mark = "x" if field in completed else " "
        label = INTAKE_FIELD_LABELS.get(field, field.replace("_", " ").title())
        lines.append(f"- [{mark}] `{field}` - {label}")
    lines += ["", "## Answers", ""]
    if answers:
        for field, record in answers.items():
            kind = record.get("kind", "answer") if isinstance(record, dict) else "answer"
            value = record.get("value", "") if isinstance(record, dict) else str(record)
            lines += [f"### {field}", "", f"- Kind: {kind}", f"- Value: {value}", ""]
    else:
        lines.append("- None recorded yet.")
    lines += ["", "## Waivers", ""]
    if waivers:
        for field, record in waivers.items():
            reason = record.get("reason", "") if isinstance(record, dict) else str(record)
            lines += [f"- `{field}`: {reason}"]
    else:
        lines.append("- None recorded.")
    lines += ["", "## Question Rounds", ""]
    rounds = intake.get("question_rounds", [])
    if rounds:
        for item in rounds:
            lines.append(f"- {item.get('timestamp', '')}: {item.get('batch', '')} ({', '.join(item.get('question_ids', []))})")
    else:
        lines.append("- No question batches recorded yet.")
    lines += ["", "## Open Questions", ""]
    open_questions = state.get("open_questions", [])
    lines += [f"- {question}" for question in open_questions] or ["- None recorded."]
    return "\n".join(lines) + "\n"


def intake_template(request_id: str, objective: str) -> str:
    state = default_state(request_id, objective)
    return render_intake_document(state)


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


def markdown_section_map(markdown_path: Path, level: int = 2) -> dict[str, str]:
    if not markdown_path.exists():
        raise HarnessError(f"Missing artifact: {markdown_path}")
    text = markdown_path.read_text(encoding="utf-8")
    pattern = re.compile(rf"^{'#' * level}\s+(.+?)\s*$", flags=re.MULTILINE)
    matches = list(pattern.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[title] = text[start:end].strip()
    return sections


def _plain_content(value: str) -> str:
    lines = []
    for line in value.splitlines():
        text = line.strip()
        text = re.sub(r"^[-*]\s+", "", text)
        text = re.sub(r"^\d+[.)]\s+", "", text)
        text = text.strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


def _has_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(re.search(pattern, lowered) for pattern in PLACEHOLDER_PATTERNS)


def validate_plan_artifact(target: str | Path, request_id: str) -> dict[str, Any]:
    path = plan_path(target, request_id)
    missing_sections = require_sections(path, PLAN_SECTIONS)
    sections = markdown_section_map(path)
    quality_problems: list[str] = []

    for section in PLAN_SECTIONS:
        if section in {"Open Questions"} or section in missing_sections:
            continue
        content = _plain_content(sections.get(section, ""))
        if len(content) < 20:
            quality_problems.append(f"{section}: section must contain concrete planning detail")
        elif _has_placeholder(content):
            quality_problems.append(f"{section}: section contains placeholder text")

    planning_standard = sections.get("Planning Standard", "").lower()
    frameworks = [framework for framework in PLANNING_FRAMEWORK_IDS if framework in planning_standard]
    missing_frameworks = [framework for framework in PLANNING_FRAMEWORK_IDS if framework not in frameworks]
    if missing_frameworks:
        quality_problems.append("Planning Standard: missing framework ids: " + ", ".join(missing_frameworks))

    dependency_graph = sections.get("Dependency Graph", "").lower()
    if dependency_graph and not any(marker in dependency_graph for marker in ["->", "depends on", "before", "after"]):
        quality_problems.append("Dependency Graph: must state ordering or dependency relationships")

    decisions = sections.get("Decision Records", "").lower()
    for marker in ["decision:", "rationale:", "consequences:"]:
        if decisions and marker not in decisions:
            quality_problems.append(f"Decision Records: missing {marker}")

    verification = sections.get("Verification Matrix", "").lower()
    if verification and not all(marker in verification for marker in ["criteria", "evidence", "command"]):
        quality_problems.append("Verification Matrix: must map criteria to evidence and command")

    premortem = sections.get("Premortem Risks", "").lower()
    if premortem and not all(marker in premortem for marker in ["failure mode", "mitigation"]):
        quality_problems.append("Premortem Risks: must include failure mode and mitigation")

    complexity = sections.get("Complexity Classification", "").lower()
    if complexity and not any(domain in complexity for domain in ["clear", "complicated", "complex", "chaotic"]):
        quality_problems.append("Complexity Classification: must include a Cynefin domain")

    parallelization = sections.get("Parallelization Boundaries", "").lower()
    if parallelization and not all(marker in parallelization for marker in ["parallel", "sequential"]):
        quality_problems.append("Parallelization Boundaries: must distinguish parallel and sequential work")

    return {
        "missing_sections": missing_sections,
        "quality_problems": quality_problems,
        "frameworks": frameworks,
    }


def validate_spec(target: str | Path, request_id: str) -> list[str]:
    return require_sections(spec_path(target, request_id), SPEC_SECTIONS)


def validate_plan(target: str | Path, request_id: str) -> list[str]:
    result = validate_plan_artifact(target, request_id)
    return [f"missing section: {item}" for item in result["missing_sections"]] + list(result["quality_problems"])


def task_blocks(text: str) -> list[dict[str, str]]:
    pattern = re.compile(r"^##\s+Task\s+(.+?)\s*$", flags=re.MULTILINE)
    matches = list(pattern.finditer(text))
    blocks: list[dict[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append({"title": match.group(1).strip(), "content": text[start:end].strip()})
    return blocks


def task_field_value(block: str, field: str) -> str:
    pattern = re.compile(rf"^\s*(?:[-*]\s*)?(?:\*\*)?{re.escape(field)}(?:\*\*)?\s*:\s*(.*)$", flags=re.IGNORECASE | re.MULTILINE)
    match = pattern.search(block)
    if not match:
        return ""
    start = match.end()
    next_field = re.search(r"^\s*(?:[-*]\s*)?(?:\*\*)?[A-Za-z][A-Za-z /-]{1,40}(?:\*\*)?\s*:\s+", block[start:], flags=re.MULTILINE)
    end = start + next_field.start() if next_field else len(block)
    value = (match.group(1) + "\n" + block[start:end]).strip()
    return value


def validate_tasks_artifact(target: str | Path, request_id: str) -> dict[str, Any]:
    path = tasks_path(target, request_id)
    if not path.exists():
        raise HarnessError(f"Missing artifact: {path}")
    text = path.read_text(encoding="utf-8")
    missing_markers = [marker for marker in TASKS_MARKERS if marker not in text]
    blocks = task_blocks(text)
    quality_problems: list[str] = []

    if not blocks:
        quality_problems.append("tasks.md: define each task with a '## Task <id>: <title>' heading")

    if _has_placeholder(text):
        quality_problems.append("tasks.md: contains placeholder text")

    for index, item in enumerate(blocks, start=1):
        title = item["title"]
        content = item["content"]
        label = f"Task {title or index}"
        missing_fields = [field for field in TASK_REQUIRED_FIELDS if not task_field_value(content, field)]
        if missing_fields:
            quality_problems.append(f"{label}: missing fields: {', '.join(missing_fields)}")
            continue

        size = task_field_value(content, "Size").upper()
        normalized_size = re.sub(r"[^A-Z/]", "", size)
        if normalized_size not in ALLOWED_TASK_SIZES:
            quality_problems.append(f"{label}: size must be XS or S")

        files = task_field_value(content, "Files")
        if "`" not in files and "/" not in files and "." not in files:
            quality_problems.append(f"{label}: Files must name likely paths or path patterns")

        verification = task_field_value(content, "Verify").lower()
        if not any(marker in verification for marker in ["run ", "python", "npm", "pytest", "unittest", "manual", "evidence", "command"]):
            quality_problems.append(f"{label}: Verify must name command or evidence")

        scenario = task_field_value(content, "Scenario").lower()
        if scenario and not all(marker in scenario for marker in ["given", "when", "then"]):
            quality_problems.append(f"{label}: Scenario must use Given/When/Then")

    return {
        "missing_markers": missing_markers,
        "quality_problems": quality_problems,
        "task_count": len(blocks),
    }


def validate_tasks(target: str | Path, request_id: str) -> list[str]:
    result = validate_tasks_artifact(target, request_id)
    return [f"missing marker: {item}" for item in result["missing_markers"]] + list(result["quality_problems"])


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


def sonar_project_identity(target: str | Path, project_key: str | None = None, project_name: str | None = None) -> dict[str, str]:
    root = target_root(target)
    name = project_name or root.name
    key_source = project_key or name
    key = re.sub(r"[^A-Za-z0-9_.:-]+", "-", key_source).strip("-") or "project"
    return {"project_key": key, "project_name": name}


def sonar_compose_project_name(target: str | Path) -> str:
    root = target_root(target)
    slug = re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-") or "project"
    digest = hashlib.sha1(str(root).encode("utf-8")).hexdigest()[:8]
    return f"harness-sonar-{slug[:32]}-{digest}"


def sonar_properties(
    target: str | Path,
    stack: dict[str, Any],
    project_key: str | None = None,
    project_name: str | None = None,
) -> str:
    identity = sonar_project_identity(target, project_key=project_key, project_name=project_name)
    primary = stack["primary"]
    lines = [
        f"sonar.projectKey={identity['project_key']}",
        f"sonar.projectName={identity['project_name']}",
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


def sonar_compose(host_port: int = 9000) -> str:
    return f"""services:
  sonarqube:
    image: sonarqube:community
    ports:
      - "{host_port}:9000"
    environment:
      SONAR_ES_BOOTSTRAP_CHECKS_DISABLE: "true"
      SONAR_FORCEAUTHENTICATION: "false"
    volumes:
      - sonar_data:/opt/sonarqube/data
      - sonar_extensions:/opt/sonarqube/extensions
      - sonar_logs:/opt/sonarqube/logs

  sonar-scanner:
    image: sonarsource/sonar-scanner-cli:latest
    depends_on:
      - sonarqube
    environment:
      SONAR_HOST_URL: "http://sonarqube:9000"
    volumes:
      - ../..:/usr/src
    working_dir: /usr/src
    command: sonar-scanner -Dproject.settings=.harness/sonar/sonar-project.properties -Dsonar.qualitygate.wait=true

volumes:
  sonar_data:
  sonar_extensions:
  sonar_logs:
"""


def sonar_env_example(host_port: int = 9000) -> str:
    return f"""# No environment variables are required for local Sonar scans.
# The SonarQube UI is exposed at http://localhost:{host_port}.
# Keep this file token-free; credentials do not belong in .harness.
"""


def sonar_config_data(
    target: str | Path,
    stack: dict[str, Any],
    host_port: int = 9000,
    project_key: str | None = None,
    project_name: str | None = None,
    status: str = "configured_not_run",
    last_error: str = "",
) -> dict[str, Any]:
    root = target_root(target)
    identity = sonar_project_identity(root, project_key=project_key, project_name=project_name)
    sonar_root = harness_dir(root) / "sonar"
    return {
        "schema_version": 1,
        "status": status,
        "detected_stack": stack,
        "project": identity,
        "urls": {
            "host": f"http://localhost:{host_port}",
            "internal": "http://sonarqube:9000",
            "system_status": f"http://localhost:{host_port}/api/system/status",
        },
        "docker": {
            "compose_file": str(sonar_root / "docker-compose.sonar.yml"),
            "services": {
                "server": "sonarqube",
                "scanner": "sonar-scanner",
            },
            "compose_project": sonar_compose_project_name(root),
            "host_port": host_port,
        },
        "files": {
            "properties": str(sonar_root / "sonar-project.properties"),
            "env_example": str(sonar_root / ".env.example"),
        },
        "required_environment": [],
        "scanner_authentication": "local_anonymous",
        "quality_gate": {
            "wait": True,
            "timeout_seconds": 300,
        },
        "last_error": last_error,
        "updated_at": now_iso(),
    }


def sonar_config_path(target: str | Path) -> Path:
    return harness_dir(target) / "sonar" / "sonar-config.json"


def read_sonar_config(target: str | Path) -> dict[str, Any]:
    return load_json(sonar_config_path(target), default={})


def write_sonar_config(target: str | Path, data: dict[str, Any]) -> None:
    data["updated_at"] = now_iso()
    write_json(sonar_config_path(target), data)


def docker_available() -> bool:
    return shutil.which("docker") is not None


def require_docker_compose(target: str | Path) -> None:
    if not docker_available():
        raise HarnessError("Docker CLI not found; install Docker before running SonarQube")
    result = run_shell("docker compose version", target_root(target))
    if result.returncode != 0:
        raise HarnessError(f"Docker Compose is not available: {result.stderr.strip() or result.stdout.strip()}")


def sonar_status_url(target: str | Path) -> str:
    config = read_sonar_config(target)
    return config.get("urls", {}).get("system_status") or "http://localhost:9000/api/system/status"


def fetch_sonar_status(target: str | Path, timeout: int = 5) -> dict[str, Any]:
    url = sonar_status_url(target)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)
            return {"ok": data.get("status") == "UP", "status": data.get("status", "unknown"), "url": url, "body": data}
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "status": "unreachable", "url": url, "error": str(exc)}


def wait_for_sonar(target: str | Path, timeout_seconds: int = 180, interval_seconds: int = 5) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last = {"ok": False, "status": "not_checked"}
    while time.monotonic() < deadline:
        last = fetch_sonar_status(target, timeout=min(interval_seconds, 5))
        if last.get("ok"):
            return last
        time.sleep(interval_seconds)
    return last


def update_sonar_runtime_status(target: str | Path, status: str, last_error: str = "", extra: dict[str, Any] | None = None) -> dict[str, Any]:
    data = read_sonar_config(target)
    if not data:
        stack = detect_stack(target)
        data = sonar_config_data(target, stack, status=status, last_error=last_error)
    data["status"] = status
    data["last_error"] = last_error
    data["required_environment"] = []
    data["scanner_authentication"] = "local_anonymous"
    data.setdefault("quality_gate", {"wait": True, "timeout_seconds": 300})
    if extra:
        data.update(extra)
    write_sonar_config(target, data)
    return data


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


def generate_sonar_templates(
    target: str | Path,
    force: bool = False,
    host_port: int = 9000,
    project_key: str | None = None,
    project_name: str | None = None,
) -> dict[str, Any]:
    root = harness_dir(target) / "sonar"
    stack = detect_stack(target)
    compose_written = write_if_absent(root / "docker-compose.sonar.yml", sonar_compose(host_port=host_port), force=force)
    props_written = write_if_absent(
        root / "sonar-project.properties",
        sonar_properties(target, stack, project_key=project_key, project_name=project_name),
        force=force,
    )
    env_written = write_if_absent(root / ".env.example", sonar_env_example(host_port=host_port), force=force)
    config = sonar_config_data(
        target,
        stack,
        host_port=host_port,
        project_key=project_key,
        project_name=project_name,
        status="configured_not_run",
    )
    write_sonar_config(target, config)
    return {
        "stack": stack,
        "compose_written": compose_written,
        "properties_written": props_written,
        "env_written": env_written,
        "config": config,
    }


def start_sonarqube(target: str | Path, timeout_seconds: int = 180) -> dict[str, Any]:
    root = target_root(target)
    require_docker_compose(root)
    compose = harness_dir(root) / "sonar" / "docker-compose.sonar.yml"
    if not compose.exists():
        raise HarnessError(f"Missing Sonar compose file: {compose}")
    command = f'docker compose -p "{sonar_compose_project_name(root)}" -f "{compose}" up -d sonarqube'
    result = run_shell(command, root)
    payload = {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }
    if result.returncode != 0:
        update_sonar_runtime_status(root, "failed", last_error=result.stderr.strip() or result.stdout.strip(), extra={"last_start": payload})
        raise HarnessError(f"Failed to start SonarQube: {result.stderr.strip() or result.stdout.strip()}")
    status = wait_for_sonar(root, timeout_seconds=timeout_seconds)
    if not status.get("ok"):
        update_sonar_runtime_status(root, "failed", last_error=f"SonarQube did not become healthy: {status}", extra={"last_start": payload, "last_health": status})
        raise HarnessError(f"SonarQube did not become healthy before timeout: {status}")
    config = update_sonar_runtime_status(root, "running", extra={"last_start": payload, "last_health": status})
    return {"ok": True, "start": payload, "health": status, "config": config}


def stop_sonarqube(target: str | Path) -> dict[str, Any]:
    root = target_root(target)
    require_docker_compose(root)
    compose = harness_dir(root) / "sonar" / "docker-compose.sonar.yml"
    if not compose.exists():
        raise HarnessError(f"Missing Sonar compose file: {compose}")
    command = f'docker compose -p "{sonar_compose_project_name(root)}" -f "{compose}" down'
    result = run_shell(command, root)
    payload = {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }
    if result.returncode != 0:
        update_sonar_runtime_status(root, "stop_failed", last_error=result.stderr.strip() or result.stdout.strip(), extra={"last_stop": payload})
        raise HarnessError(f"Failed to stop SonarQube: {result.stderr.strip() or result.stdout.strip()}")
    config = update_sonar_runtime_status(root, "stopped", extra={"last_stop": payload})
    return {"ok": True, "stop": payload, "config": config}


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
