#!/usr/bin/env python3
"""Run and record request intake interviews."""

from __future__ import annotations

import argparse
import re

from harness_common import (
    HarnessError,
    INTAKE_REQUIRED_FIELDS,
    append_history,
    ensure_intake_state,
    incomplete_intake_fields,
    intake_path,
    load_state,
    main_guard,
    normalize_task_type,
    now_iso,
    print_json,
    render_intake_document,
    save_state,
    write_if_absent,
)


COMMON_QUESTIONS = [
    {"id": "objective", "field": "objective", "question": "What exactly should change, in user-visible terms?"},
    {"id": "task_type", "field": "task_type", "question": "What type of work is this: feature, bug, refactor, UI/runtime, security/reliability, review, harness improvement, or maintenance?"},
    {"id": "audience", "field": "audience", "question": "Who is the user, operator, reviewer, or system that needs this change?"},
    {"id": "desired_outcome", "field": "desired_outcome", "question": "What outcome should be true when the work is complete?"},
    {"id": "success_criteria", "field": "success_criteria", "question": "Which concrete, testable acceptance criteria must pass?"},
    {"id": "non_goals", "field": "non_goals", "question": "What should remain explicitly out of scope?"},
    {"id": "constraints", "field": "constraints", "question": "What constraints, compatibility needs, deadlines, dependencies, or project conventions matter?"},
    {"id": "permissions", "field": "permissions", "question": "Which actions are always allowed, ask-first, or forbidden for this request?"},
    {"id": "verification_expectations", "field": "verification_expectations", "question": "What evidence should prove the result: tests, build, browser/API checks, screenshots, logs, review, or waiver?"},
]


TYPE_QUESTIONS = {
    "feature": [
        {"id": "feature_user_flow", "field": "feature_user_flow", "question": "What is the expected end-to-end user flow?"},
        {"id": "feature_contracts", "field": "feature_contracts", "question": "Which APIs, data contracts, events, or storage shapes are affected?"},
        {"id": "feature_compatibility", "field": "feature_compatibility", "question": "What existing behavior must stay compatible?"},
    ],
    "bug": [
        {"id": "bug_expected", "field": "bug_expected", "question": "What was the expected behavior?"},
        {"id": "bug_actual", "field": "bug_actual", "question": "What is the actual behavior?"},
        {"id": "bug_reproduction", "field": "bug_reproduction", "question": "What reproduction steps, logs, traces, or failing checks demonstrate the bug?"},
        {"id": "bug_severity", "field": "bug_severity", "question": "How severe is the bug and who is affected?"},
    ],
    "refactor": [
        {"id": "refactor_boundary", "field": "refactor_boundary", "question": "What behavior-preservation boundary must not change?"},
        {"id": "refactor_motivation", "field": "refactor_motivation", "question": "What maintainability, architecture, or performance problem motivates the refactor?"},
        {"id": "refactor_checks", "field": "refactor_checks", "question": "Which checks prove behavior was preserved?"},
    ],
    "ui_runtime": [
        {"id": "ui_surfaces", "field": "ui_surfaces", "question": "Which screens, breakpoints, states, commands, APIs, or runtime surfaces are affected?"},
        {"id": "ui_visual_reference", "field": "ui_visual_reference", "question": "What visual, interaction, accessibility, or runtime evidence should be captured?"},
        {"id": "ui_error_states", "field": "ui_error_states", "question": "Which loading, empty, error, permission, or offline states matter?"},
    ],
    "security_reliability": [
        {"id": "security_threat", "field": "security_threat", "question": "What threat, vulnerability, incident, reliability risk, or audit finding is being addressed?"},
        {"id": "security_boundary", "field": "security_boundary", "question": "Which trust boundaries, data classes, credentials, or production systems are involved?"},
        {"id": "security_approval", "field": "security_approval", "question": "Which security, reliability, or release approvals are required?"},
    ],
    "review": [
        {"id": "review_subject", "field": "review_subject", "question": "What diff, PR, branch, commit, or artifact should be reviewed?"},
        {"id": "review_focus", "field": "review_focus", "question": "What should the review focus on: bugs, regressions, architecture, security, tests, UI, or evidence?"},
        {"id": "review_standard", "field": "review_standard", "question": "What standards, acceptance criteria, or known risks should findings be judged against?"},
    ],
    "harness_improvement": [
        {"id": "harness_failure_pattern", "field": "harness_failure_pattern", "question": "What repeated failure, avoidable intervention, or escaped defect should this prevent?"},
        {"id": "harness_control_type", "field": "harness_control_type", "question": "Which control type is missing: guide, sensor, tool, permission, memory, prompt, state, review, or entropy?"},
        {"id": "harness_success_signal", "field": "harness_success_signal", "question": "How will we verify the new harness control works?"},
    ],
    "maintenance": [
        {"id": "maintenance_area", "field": "maintenance_area", "question": "Which maintenance area is affected?"},
        {"id": "maintenance_risk", "field": "maintenance_risk", "question": "What operational, compatibility, or cleanup risk should be controlled?"},
        {"id": "maintenance_done", "field": "maintenance_done", "question": "What proves the maintenance work is complete?"},
    ],
}


RISK_QUESTIONS = [
    {"id": "risk_external_systems", "field": "risk_external_systems", "question": "Which external systems, credentials, network calls, or production-like resources are involved?"},
    {"id": "risk_destructive_actions", "field": "risk_destructive_actions", "question": "Could this involve migrations, deletes, deployment, generated code, Docker, package installation, or other approval-required actions?"},
    {"id": "risk_ambiguity", "field": "risk_ambiguity", "question": "Which product, architecture, or verification decisions are still ambiguous enough to block implementation?"},
]


RISK_KEYWORDS = [
    "credential",
    "delete",
    "deploy",
    "docker",
    "external",
    "migration",
    "network",
    "package",
    "production",
    "publish",
    "secret",
]


def split_items(value: str) -> list[str]:
    items: list[str] = []
    for line in value.splitlines():
        text = re.sub(r"^\s*(?:[-*]|\d+[.)]|\[[ xX]\])\s*", "", line).strip()
        if text:
            items.append(text)
    if not items and value.strip():
        items.append(value.strip())
    return items


def field_id(value: str) -> str:
    field = value.strip().lower().replace("-", "_").replace(" ", "_")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", field):
        raise HarnessError(f"Invalid field id: {value}")
    return field


def append_unique(items: list, value) -> None:
    if value not in items:
        items.append(value)


def remove_value(items: list, value) -> None:
    while value in items:
        items.remove(value)


def parse_permissions(value: str) -> dict[str, list[str]]:
    permissions = {"always": [], "ask_first": [], "never": []}
    current = "ask_first"
    for item in split_items(value):
        lower = item.lower()
        matched = False
        for key, labels in {
            "always": ["always", "allowed"],
            "ask_first": ["ask first", "ask_first", "approval", "approve"],
            "never": ["never", "forbidden", "do not"],
        }.items():
            for label in labels:
                if lower.startswith(label):
                    current = key
                    rest = item[len(label) :].lstrip(" :-")
                    if rest:
                        permissions[current].append(rest)
                    matched = True
                    break
            if matched:
                break
        if not matched:
            permissions[current].append(item)
    return permissions


def apply_answer_to_state(state: dict, field: str, value: str, is_assumption: bool = False) -> None:
    intake = ensure_intake_state(state)
    if field == "objective":
        state["objective"] = value.strip()
    elif field == "task_type":
        intake["task_type"] = normalize_task_type(value)
    elif field == "success_criteria":
        state["acceptance_criteria"] = [
            {"id": f"AC-{index:03d}", "text": item, "status": "unverified", "evidence": []}
            for index, item in enumerate(split_items(value), start=1)
        ]
    elif field == "non_goals":
        state["non_goals"] = split_items(value)
    elif field == "permissions":
        state["permissions"] = parse_permissions(value)
    elif field == "risk_level":
        words = value.strip().split(maxsplit=1)
        level = words[0].lower() if words else "unknown"
        if level not in {"low", "medium", "high", "critical", "unknown"}:
            level = "unknown"
        state["risk_level"] = {"level": level, "reason": words[1] if len(words) > 1 else value.strip()}
    elif field == "open_questions":
        state["open_questions"] = split_items(value)
    elif field == "assumptions" or is_assumption:
        for item in split_items(value):
            append_unique(state.setdefault("assumptions", []), {"field": field, "text": item})


def write_intake(args: argparse.Namespace, state: dict) -> bool:
    return write_if_absent(intake_path(args.target, args.request_id), render_intake_document(state), force=args.force)


def rewrite_intake(target: str, request_id: str, state: dict) -> None:
    intake_path(target, request_id).write_text(render_intake_document(state), encoding="utf-8")


def create(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    ensure_intake_state(state)
    save_state(args.target, args.request_id, state)
    wrote = write_intake(args, state)
    append_history(args.target, args.request_id, "intake.created" if wrote else "intake.exists", "Intake artifact checked")
    print_json({"request_id": args.request_id, "path": str(intake_path(args.target, args.request_id)), "written": wrote})


def asked_question_ids(state: dict) -> set[str]:
    intake = ensure_intake_state(state)
    asked: set[str] = set()
    for round_item in intake.get("question_rounds", []):
        asked.update(str(item) for item in round_item.get("question_ids", []))
    return asked


def needs_risk_questions(state: dict) -> bool:
    intake = ensure_intake_state(state)
    text_parts = [state.get("objective", "")]
    for record in intake.get("answers", {}).values():
        if isinstance(record, dict):
            text_parts.append(str(record.get("value", "")))
    haystack = "\n".join(text_parts).lower()
    return any(keyword in haystack for keyword in RISK_KEYWORDS)


def choose_questions(state: dict) -> tuple[str, list[dict[str, str]]]:
    intake = ensure_intake_state(state)
    asked = asked_question_ids(state)
    missing = set(incomplete_intake_fields(state))
    common = [question for question in COMMON_QUESTIONS if question["field"] in missing]
    if common:
        return "common", common
    task_type = intake.get("task_type", "unknown")
    type_questions = [question for question in TYPE_QUESTIONS.get(task_type, []) if question["id"] not in asked]
    if type_questions:
        return f"{task_type}_followup", type_questions
    risk_questions = [question for question in RISK_QUESTIONS if question["id"] not in asked]
    if needs_risk_questions(state) and risk_questions:
        return "risk_followup", risk_questions
    return "ready_for_spec", []


def record_question_round(target: str, request_id: str, state: dict, batch: str, selected: list[dict[str, str]]) -> None:
    intake = ensure_intake_state(state)
    if selected:
        intake["question_rounds"].append(
            {
                "timestamp": now_iso(),
                "batch": batch,
                "question_ids": [question["id"] for question in selected],
            }
        )
        save_state(target, request_id, state)
        rewrite_intake(target, request_id, state)
        append_history(target, request_id, "intake.questions", f"Asked {batch} intake questions", question_ids=[question["id"] for question in selected])


def questions(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    batch, selected = choose_questions(state)
    record_question_round(args.target, args.request_id, state, batch, selected)
    print_json({"request_id": args.request_id, "batch": batch, "questions": selected, "missing_fields": incomplete_intake_fields(state)})


def record(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    intake = ensure_intake_state(state)
    field = field_id(args.field)
    if args.waive:
        reason = (args.reason or args.answer or "").strip()
        if not reason:
            raise HarnessError("--reason or --answer is required when waiving a field")
        intake.setdefault("waivers", {})[field] = {"reason": reason, "recorded_at": now_iso()}
        append_unique(intake["waived_fields"], field)
        remove_value(intake["answered_fields"], field)
        event_type = "intake.waived"
        summary = f"Waived intake field {field}"
    else:
        value = (args.answer or "").strip()
        if not value:
            raise HarnessError("--answer is required unless --waive is used")
        kind = "assumption" if args.assumption else "answer"
        intake.setdefault("answers", {})[field] = {"value": value, "kind": kind, "recorded_at": now_iso()}
        append_unique(intake["answered_fields"], field)
        remove_value(intake["waived_fields"], field)
        intake.setdefault("waivers", {}).pop(field, None)
        apply_answer_to_state(state, field, value, is_assumption=args.assumption)
        event_type = "intake.recorded"
        summary = f"Recorded intake field {field}"
    if incomplete_intake_fields(state):
        intake["status"] = "incomplete"
    state["next_action"] = "Complete intake before approving spec.md." if intake["status"] != "complete" else state.get("next_action", "")
    save_state(args.target, args.request_id, state)
    rewrite_intake(args.target, args.request_id, state)
    append_history(args.target, args.request_id, event_type, summary, field=field)
    print_json({"request_id": args.request_id, "field": field, "missing_fields": incomplete_intake_fields(state), "status": intake["status"]})


def validate(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    ensure_intake_state(state)
    missing = incomplete_intake_fields(state)
    print_json({"request_id": args.request_id, "valid": not missing, "missing_fields": missing, "status": state["intake"]["status"]})


def complete(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    intake = ensure_intake_state(state)
    missing = incomplete_intake_fields(state)
    if missing:
        raise HarnessError(f"Cannot complete intake; missing fields: {', '.join(missing)}")
    intake["status"] = "complete"
    state["next_action"] = "Create, fill, validate, and approve spec.md."
    save_state(args.target, args.request_id, state)
    rewrite_intake(args.target, args.request_id, state)
    append_history(args.target, args.request_id, "intake.completed", "Completed intake interview")
    print_json({"request_id": args.request_id, "status": "complete"})


def interview(args: argparse.Namespace) -> None:
    create_args = argparse.Namespace(target=args.target, request_id=args.request_id, force=False)
    create(create_args)
    while True:
        state = load_state(args.target, args.request_id)
        batch, selected = choose_questions(state)
        if not selected:
            break
        record_question_round(args.target, args.request_id, state, batch, selected)
        for question in selected:
            answer = input(question["question"] + "\n> ").strip()
            if not answer:
                answer = input("No answer provided. Enter a waiver reason, or press Enter again to keep it missing.\n> ").strip()
                if answer:
                    record_args = argparse.Namespace(target=args.target, request_id=args.request_id, field=question["field"], answer="", reason=answer, waive=True, assumption=False)
                    record(record_args)
                continue
            record_args = argparse.Namespace(target=args.target, request_id=args.request_id, field=question["field"], answer=answer, reason="", waive=False, assumption=False)
            record(record_args)
    if args.complete:
        complete(argparse.Namespace(target=args.target, request_id=args.request_id))


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    create_parser = sub.add_parser("create")
    create_parser.add_argument("--target", default=".")
    create_parser.add_argument("--request-id", required=True)
    create_parser.add_argument("--force", action="store_true")
    create_parser.set_defaults(func=create)

    questions_parser = sub.add_parser("questions")
    questions_parser.add_argument("--target", default=".")
    questions_parser.add_argument("--request-id", required=True)
    questions_parser.set_defaults(func=questions)

    record_parser = sub.add_parser("record")
    record_parser.add_argument("--target", default=".")
    record_parser.add_argument("--request-id", required=True)
    record_parser.add_argument("--field", required=True)
    record_parser.add_argument("--answer", default="")
    record_parser.add_argument("--reason", default="")
    record_parser.add_argument("--assumption", action="store_true")
    record_parser.add_argument("--waive", action="store_true")
    record_parser.set_defaults(func=record)

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--target", default=".")
    validate_parser.add_argument("--request-id", required=True)
    validate_parser.set_defaults(func=validate)

    complete_parser = sub.add_parser("complete")
    complete_parser.add_argument("--target", default=".")
    complete_parser.add_argument("--request-id", required=True)
    complete_parser.set_defaults(func=complete)

    interview_parser = sub.add_parser("interview")
    interview_parser.add_argument("--target", default=".")
    interview_parser.add_argument("--request-id", required=True)
    interview_parser.add_argument("--complete", action="store_true")
    interview_parser.set_defaults(func=interview)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_guard(run)
