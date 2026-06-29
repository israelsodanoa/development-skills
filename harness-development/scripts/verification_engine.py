#!/usr/bin/env python3
"""Render requirement-level verification reports."""

from __future__ import annotations

import argparse

from harness_common import (
    append_history,
    load_state,
    main_guard,
    now_iso,
    print_json,
    refresh_continuation_handoff,
    refresh_evidence_manifest,
    save_state,
    verification_path,
)


def render_report(state: dict) -> str:
    criteria = state.get("acceptance_criteria") or [{"id": "AC-001", "text": "See spec.md", "status": "unverified", "evidence": []}]
    lines = [
        f"# Verification Report: {state.get('request_id')}",
        "",
        f"Generated: {now_iso()}",
        f"Objective: {state.get('objective')}",
        f"Summary status: {state.get('status')}",
        "",
        "## Acceptance Criteria",
        "",
    ]
    for criterion in criteria:
        cid = criterion.get("id", "AC-unknown")
        lines += [
            f"### {cid}",
            "",
            f"- Text: {criterion.get('text', '')}",
            f"- Status: {criterion.get('status', 'unverified')}",
            f"- Evidence: {criterion.get('evidence', [])}",
            f"- Residual risk: {criterion.get('residual_risk', '')}",
            "",
        ]
    lines += ["## Commands", ""]
    for command in state.get("commands_run", []):
        lines.append(f"- `{command.get('command_id', command.get('command', ''))}`: {command.get('returncode')} ({command.get('log_path', '')})")
    lines += ["", "## Failed Checks", ""]
    for failure in state.get("failure_attributions", []):
        lines.append(f"- {failure}")
    lines += ["", "## Approvals", ""]
    for gate, approved in state.get("approvals", {}).items():
        lines.append(f"- {gate}: {approved}")
    lines += ["", "## Residual Risks", ""]
    risks = state.get("residual_risks", [])
    lines += [f"- {risk}" for risk in risks] or ["- None recorded."]
    return "\n".join(lines) + "\n"


def render(args: argparse.Namespace) -> None:
    state = load_state(args.target, args.request_id)
    path = verification_path(args.target, args.request_id)
    path.write_text(render_report(state), encoding="utf-8")
    state["status"] = "verification_reported"
    state["next_action"] = "Review verification report and close out when complete."
    save_state(args.target, args.request_id, state)
    append_history(args.target, args.request_id, "verification.rendered", "Rendered verification report", path=str(path))
    refresh_evidence_manifest(args.target, args.request_id)
    refresh_continuation_handoff(args.target, args.request_id)
    print_json({"request_id": args.request_id, "path": str(path)})


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".")
    parser.add_argument("--request-id", required=True)
    args = parser.parse_args()
    render(args)


if __name__ == "__main__":
    main_guard(run)
