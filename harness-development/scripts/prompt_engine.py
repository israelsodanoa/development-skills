#!/usr/bin/env python3
"""Generate phase-specific prompt packets for harnessed implementation."""

from __future__ import annotations

import argparse

from harness_common import (
    PROMPT_PHASE_INSTRUCTIONS,
    append_history,
    main_guard,
    print_json,
    prompt_packet_path,
    render_prompt_packet,
)


def render(args: argparse.Namespace) -> str:
    return render_prompt_packet(args.target, args.request_id, args.phase)


def generate(args: argparse.Namespace) -> None:
    text = render(args)
    output = prompt_packet_path(args.target, args.request_id, args.phase)
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.write:
        output.write_text(text, encoding="utf-8")
        append_history(args.target, args.request_id, "prompt_packet.generated", f"Generated {args.phase.lower()} prompt packet", path=str(output))
    if args.print:
        print(text)
    else:
        print_json({"request_id": args.request_id, "phase": args.phase, "path": str(output), "written": args.write})


def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".")
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--phase", choices=sorted(PROMPT_PHASE_INSTRUCTIONS), required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--print", action="store_true")
    args = parser.parse_args()
    generate(args)


if __name__ == "__main__":
    main_guard(run)
