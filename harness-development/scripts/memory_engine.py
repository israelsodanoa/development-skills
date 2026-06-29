#!/usr/bin/env python3
"""Maintain project memory, known failures, and control gaps."""

from __future__ import annotations

import argparse

from harness_common import (
    HarnessError,
    append_history,
    ensure_memory_state,
    harness_dir,
    load_json,
    load_state,
    main_guard,
    now_iso,
    parse_json_arg,
    print_json,
    save_state,
    write_json,
)


MEMORY_INDEX_SECTIONS = ["architecture", "testing", "domain", "tools", "decisions", "quality"]


def path_for(target: str, artifact: str):
    mapping = {
        "index": harness_dir(target) / "memory" / "memory-index.json",
        "known-failures": harness_dir(target) / "memory" / "known-failures.json",
        "control-gaps": harness_dir(target) / "memory" / "control-gaps.json",
    }
    return mapping[artifact]


def show(args: argparse.Namespace) -> None:
    print_json(load_json(path_for(args.target, args.artifact)))


def split_evidence(value: str) -> list[str]:
    return [item.strip() for item in value.replace("\n", ";").split(";") if item.strip()]


def load_request_memory(target: str, request_id: str) -> tuple[dict, dict]:
    if not request_id:
        raise HarnessError("--request-id is required for memory lifecycle actions")
    state = load_state(target, request_id)
    memory = ensure_memory_state(state)
    return state, memory


def save_request_memory(target: str, request_id: str, state: dict, event_type: str, summary: str, **payload) -> None:
    save_state(target, request_id, state)
    append_history(target, request_id, event_type, summary, **payload)


def retrieve(args: argparse.Namespace) -> None:
    state, memory = load_request_memory(args.target, args.request_id)
    stamp = now_iso()
    record = {
        "source": args.source,
        "reason": args.reason,
        "memory_type": args.memory_type,
        "status": args.status,
        "retrieved_at": stamp,
    }
    working = memory.setdefault("working", {})
    if args.status == "selected":
        working.setdefault("retrieved_sources", []).append(record)
        state.setdefault("context_sources", []).append(
            {
                "path": args.source,
                "reason": args.reason,
                "memory_type": args.memory_type,
                "selected_at": stamp,
            }
        )
    else:
        working.setdefault("skipped_sources", []).append(record)
    working["last_retrieved_at"] = stamp
    save_request_memory(
        args.target,
        args.request_id,
        state,
        f"memory.retrieve.{args.status}",
        f"Memory source {args.status}: {args.source}",
        source=args.source,
        reason=args.reason,
        memory_type=args.memory_type,
    )
    print_json(record)


def reflect(args: argparse.Namespace) -> None:
    evidence = split_evidence(args.evidence)
    if not evidence:
        raise HarnessError("--evidence is required for memory reflection")
    state, memory = load_request_memory(args.target, args.request_id)
    record = {
        "summary": args.summary,
        "lesson_type": args.lesson_type,
        "evidence": evidence,
        "confidence": args.confidence,
        "created_at": now_iso(),
    }
    memory.setdefault("episodic", {}).setdefault("reflections", []).append(record)
    save_request_memory(
        args.target,
        args.request_id,
        state,
        "memory.reflected",
        args.summary,
        lesson_type=args.lesson_type,
        evidence=evidence,
        confidence=args.confidence,
    )
    print_json(record)


def promote(args: argparse.Namespace) -> None:
    evidence = split_evidence(args.evidence)
    if not evidence:
        raise HarnessError("--evidence is required for memory promotion")
    state, memory = load_request_memory(args.target, args.request_id)
    stamp = now_iso()
    record = {
        "id": f"promotion-{len(memory.setdefault('long_term', {}).setdefault('promotions', [])) + 1}",
        "kind": args.kind,
        "summary": args.summary,
        "source": args.source,
        "evidence": evidence,
        "confidence": args.confidence,
        "request_id": args.request_id,
        "promoted_at": stamp,
    }

    if args.kind in {"semantic", "procedural"}:
        section = args.section or ("quality" if args.kind == "procedural" else "decisions")
        path = path_for(args.target, "index")
        data = load_json(path, default={"schema_version": 1})
        item = {
            "summary": args.summary,
            "source": args.source,
            "evidence": evidence,
            "confidence": args.confidence,
            "memory_kind": args.kind,
            "request_id": args.request_id,
            "updated_at": stamp,
        }
        data.setdefault(section, []).append(item)
        data.setdefault("promotion_log", []).append(record)
        data["updated_at"] = stamp
        write_json(path, data)
        record["artifact"] = str(path)
        record["section"] = section
    elif args.kind == "known-failure":
        path = path_for(args.target, "known-failures")
        data = load_json(path, default={"schema_version": 1, "failures": []})
        item = {
            "id": f"failure-{len(data.get('failures', [])) + 1}",
            "summary": args.summary,
            "control_needed": args.control_needed,
            "source": args.source,
            "evidence": evidence,
            "confidence": args.confidence,
            "request_id": args.request_id,
            "created_at": stamp,
        }
        data.setdefault("failures", []).append(item)
        write_json(path, data)
        record["artifact"] = str(path)
        record["entry_id"] = item["id"]
    elif args.kind == "control-gap":
        path = path_for(args.target, "control-gaps")
        data = load_json(path, default={"schema_version": 1, "gaps": []})
        item = {
            "id": f"gap-{len(data.get('gaps', [])) + 1}",
            "type": args.gap_type,
            "summary": args.summary,
            "severity": args.severity,
            "status": "open",
            "source": args.source,
            "evidence": evidence,
            "confidence": args.confidence,
            "request_id": args.request_id,
            "created_at": stamp,
        }
        data.setdefault("gaps", []).append(item)
        write_json(path, data)
        record["artifact"] = str(path)
        record["entry_id"] = item["id"]
    else:
        raise HarnessError(f"Unsupported promotion kind: {args.kind}")

    memory["long_term"]["promotions"].append(record)
    save_request_memory(
        args.target,
        args.request_id,
        state,
        "memory.promoted",
        args.summary,
        kind=args.kind,
        artifact=record.get("artifact"),
        evidence=evidence,
        confidence=args.confidence,
    )
    print_json(record)


def prune(args: argparse.Namespace) -> None:
    state, memory = load_request_memory(args.target, args.request_id)
    stamp = now_iso()
    record = {
        "artifact": args.artifact,
        "entry_id": args.entry_id,
        "reason": args.reason,
        "replacement": args.replacement,
        "request_id": args.request_id,
        "recorded_at": stamp,
    }
    memory.setdefault("long_term", {}).setdefault("pruning_log", []).append(record)
    index_path = path_for(args.target, "index")
    index = load_json(index_path, default={"schema_version": 1})
    index.setdefault("pruning_log", []).append(record)
    index["updated_at"] = stamp
    write_json(index_path, index)
    save_request_memory(
        args.target,
        args.request_id,
        state,
        "memory.pruned",
        f"Recorded memory pruning for {args.entry_id}",
        artifact=args.artifact,
        entry_id=args.entry_id,
        reason=args.reason,
        replacement=args.replacement,
    )
    print_json(record)


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
    source.add_argument("--section", choices=MEMORY_INDEX_SECTIONS, required=True)
    source.add_argument("--path", required=True)
    source.add_argument("--reason", required=True)
    source.add_argument("--data-json", default="")
    source.set_defaults(func=add_source)
    retrieve_parser = sub.add_parser("retrieve")
    retrieve_parser.add_argument("--target", default=".")
    retrieve_parser.add_argument("--request-id", required=True)
    retrieve_parser.add_argument("--source", required=True)
    retrieve_parser.add_argument("--reason", required=True)
    retrieve_parser.add_argument("--status", choices=["selected", "skipped"], default="selected")
    retrieve_parser.add_argument("--memory-type", choices=["working", "episodic", "semantic", "procedural", "unknown"], default="semantic")
    retrieve_parser.set_defaults(func=retrieve)
    reflect_parser = sub.add_parser("reflect")
    reflect_parser.add_argument("--target", default=".")
    reflect_parser.add_argument("--request-id", required=True)
    reflect_parser.add_argument("--summary", required=True)
    reflect_parser.add_argument("--lesson-type", choices=["semantic", "procedural", "control", "failure", "decision"], default="control")
    reflect_parser.add_argument("--evidence", required=True)
    reflect_parser.add_argument("--confidence", choices=["low", "medium", "high"], default="medium")
    reflect_parser.set_defaults(func=reflect)
    promote_parser = sub.add_parser("promote")
    promote_parser.add_argument("--target", default=".")
    promote_parser.add_argument("--request-id", required=True)
    promote_parser.add_argument("--kind", choices=["semantic", "procedural", "known-failure", "control-gap"], required=True)
    promote_parser.add_argument("--summary", required=True)
    promote_parser.add_argument("--source", required=True)
    promote_parser.add_argument("--evidence", required=True)
    promote_parser.add_argument("--confidence", choices=["low", "medium", "high"], default="medium")
    promote_parser.add_argument("--section", choices=MEMORY_INDEX_SECTIONS, default="")
    promote_parser.add_argument("--control-needed", default="")
    promote_parser.add_argument("--gap-type", default="memory-control")
    promote_parser.add_argument("--severity", default="medium")
    promote_parser.set_defaults(func=promote)
    prune_parser = sub.add_parser("prune")
    prune_parser.add_argument("--target", default=".")
    prune_parser.add_argument("--request-id", required=True)
    prune_parser.add_argument("--artifact", choices=["index", "known-failures", "control-gaps", "state"], required=True)
    prune_parser.add_argument("--entry-id", required=True)
    prune_parser.add_argument("--reason", required=True)
    prune_parser.add_argument("--replacement", default="")
    prune_parser.set_defaults(func=prune)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_guard(run)
