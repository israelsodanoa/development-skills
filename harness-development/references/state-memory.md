# State And Memory Reference

Task state is request-local and lives in `.harness/requests/<request_id>/state.json`.

Required state fields:

- `request_id`, `objective`, `phase`, `status`
- `approvals.spec`, `approvals.plan`, `approvals.tasks`
- `intake.status`, `intake.task_type`, `intake.required_fields`, `intake.answered_fields`, `intake.waived_fields`, `intake.question_rounds`
- `acceptance_criteria`, `non_goals`, `risk_level`, `permissions`
- `context_sources`, `inspected_files`, `changed_files`
- `decisions`, `assumptions`, `open_questions`
- `commands_run`, `verification_status`, `failure_attributions`, `interventions`
- `next_action`, `created_at`, `updated_at`

Project memory is durable and lives under `.harness/memory/`.

Request intake lives in `.harness/requests/<request_id>/intake.md` and `state.json`. Request creation starts as a draft; the agent then asks adaptive interview questions. Planning stays blocked until required intake fields are answered or explicitly waived and `intake.status` is `complete`.

Memory artifacts:

- `memory-index.json`: project map, architecture, testing, domain, tools, decisions, and quality references.
- `known-failures.json`: repeated mistakes, local pitfalls, flaky checks, misleading docs, bad patterns.
- `control-gaps.json`: missing guides, sensors, scripts, commands, permissions, reviews, or entropy controls.

Context selection:

1. Identify task category and affected modules.
2. Load the compact memory index.
3. Search concrete local files and examples.
4. Record selected and skipped sources with reasons.
5. Mark missing or stale context as a gap.
