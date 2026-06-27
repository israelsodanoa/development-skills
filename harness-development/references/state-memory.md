# State And Memory Reference

Task state is request-local and lives in `.harness/requests/<request_id>/state.json`.

Required state fields:

- `request_id`, `objective`, `phase`, `status`
- `approvals.spec`, `approvals.plan`, `approvals.tasks`
- `intake.status`, `intake.task_type`, `intake.required_fields`, `intake.answered_fields`, `intake.waived_fields`, `intake.question_rounds`
- `planning_quality.plan.status`, `planning_quality.plan.frameworks`, `planning_quality.plan.validated_at`
- `planning_quality.tasks.status`, `planning_quality.tasks.minimum_size`, `planning_quality.tasks.validated_at`, `planning_quality.tasks.task_count`
- `acceptance_criteria`, `non_goals`, `risk_level`, `permissions`
- `context_sources`, `inspected_files`, `changed_files`
- `decisions`, `assumptions`, `open_questions`
- `commands_run`, `verification_status`, `failure_attributions`, `interventions`
- `next_action`, `created_at`, `updated_at`

Project memory is durable and lives under `.harness/memory/`.

Request intake lives in `.harness/requests/<request_id>/intake.md` and `state.json`. Request creation starts as a draft; the agent then asks adaptive interview questions. Planning stays blocked until required intake fields are answered or explicitly waived and `intake.status` is `complete`.

Plan and task quality evidence lives in `state.json` under `planning_quality`. It records whether the strict plan and task gates have passed, which planning frameworks were represented, the required XS/S task size floor, validation timestamps, and task count. Top-level `decisions`, `assumptions`, `open_questions`, `risk_level`, and `verification_status` remain the authoritative implementation state.

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
