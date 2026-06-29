# State And Memory Reference

Task state is request-local and lives in `.harness/requests/<request_id>/state.json`.

Required state fields:

- `request_id`, `objective`, `phase`, `status`
- `approvals.spec`, `approvals.plan`, `approvals.tasks`
- `intake.status`, `intake.task_type`, `intake.required_fields`, `intake.answered_fields`, `intake.waived_fields`, `intake.question_rounds`
- `planning_quality.plan.status`, `planning_quality.plan.frameworks`, `planning_quality.plan.validated_at`
- `planning_quality.tasks.status`, `planning_quality.tasks.minimum_size`, `planning_quality.tasks.validated_at`, `planning_quality.tasks.task_count`
- `memory.working.retrieved_sources`, `memory.working.skipped_sources`, `memory.working.active_notes`, `memory.working.last_retrieved_at`
- `memory.episodic.history_path`, `memory.episodic.reflections`
- `memory.long_term.promotions`, `memory.long_term.pruning_log`
- `memory.policy.retrieve_before_action`, `memory.policy.promotion_requires_evidence`, `memory.policy.prune_requires_reason`
- `acceptance_criteria`, `non_goals`, `risk_level`, `permissions`
- `context_sources`, `inspected_files`, `changed_files`
- `decisions`, `assumptions`, `open_questions`
- `commands_run`, `verification_status`, `failure_attributions`, `interventions`
- `artifacts.evidence_manifest`, `artifacts.prompt_packets`, `artifacts.continuation_handoff`, `artifacts.last_synced_at`
- `next_action`, `created_at`, `updated_at`

Project memory is durable and lives under `.harness/memory/`.

Memory classes:

- Working memory: request-local state needed for the current phase, including retrieved sources, skipped sources, active notes, next action, open questions, and verification status. It lives in `.harness/requests/<request_id>/state.json`.
- Episodic memory: chronological request events, command evidence, failures, decisions, interventions, and reflections. It lives in `.harness/requests/<request_id>/history.jsonl` with reflection summaries mirrored in `state.json`.
- Semantic memory: durable project facts, architecture, testing, domain, tool, decision, and quality references. It lives in `.harness/memory/memory-index.json`.
- Procedural memory: durable controls, anti-patterns, known failures, missing guardrails, and repair protocols. It lives in `.harness/memory/known-failures.json`, `.harness/memory/control-gaps.json`, and procedural entries in `memory-index.json`.

Request intake lives in `.harness/requests/<request_id>/intake.md` and `state.json`. Request creation starts as a draft; the agent then asks adaptive interview questions. Planning stays blocked until required intake fields are answered or explicitly waived and `intake.status` is `complete`.

Required request artifacts live beside the state file. `evidence/manifest.md` indexes acceptance, command, runtime, review, and waiver evidence. `prompt-packets/*.md` stores phase-specific restart prompts. `handoffs/continuation.md` stores stable resume state and is refreshed after phase changes, command evidence, and verification updates. Validation and phase transitions must backfill missing required artifacts so older requests do not stay incomplete.

Plan and task quality evidence lives in `state.json` under `planning_quality`. It records whether the strict plan and task gates have passed, which planning frameworks were represented, the required XS/S task size floor, validation timestamps, and task count. Top-level `decisions`, `assumptions`, `open_questions`, `risk_level`, and `verification_status` remain the authoritative implementation state.

Memory artifacts:

- `memory-index.json`: project map, architecture, testing, domain, tools, decisions, and quality references.
- `known-failures.json`: repeated mistakes, local pitfalls, flaky checks, misleading docs, bad patterns.
- `control-gaps.json`: missing guides, sensors, scripts, commands, permissions, reviews, or entropy controls.

Memory lifecycle:

1. Retrieve: before acting in a phase, select relevant semantic/procedural memory and record selected and skipped sources with `memory_engine.py retrieve`.
2. Apply: use selected memory as feedforward control, then update working memory fields when files, assumptions, risks, or next actions change.
3. Reflect: after evidence, failures, reviews, or important decisions, record the lesson with `memory_engine.py reflect`.
4. Promote: move only evidence-backed facts or controls into long-term semantic/procedural memory with `memory_engine.py promote`.
5. Prune: record stale, misleading, superseded, or low-confidence memory with `memory_engine.py prune`; do not silently delete user-edited memory.

Context selection:

1. Identify task category and affected modules.
2. Load the compact memory index.
3. Search concrete local files and examples.
4. Record selected and skipped sources with reasons.
5. Mark missing or stale context as a gap.
