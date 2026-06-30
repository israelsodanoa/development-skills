# Controls Reference

Use feedforward controls before action and feedback controls after action.

Feedforward controls:

- Accepted spec and success criteria.
- Retrieved working, semantic, and procedural memory recorded with selected and skipped sources.
- Context budget, selected/skipped context ledger, priority, inclusion mode, placement, cache scope, and token estimate for sources that may enter a prompt.
- Project map and relevant architecture/testing/domain memory.
- Command registry with exact executable commands.
- Known failures and local anti-patterns.
- Permission policy for destructive, networked, credentialed, schema, dependency, CI, release, and production actions.

Feedback controls:

- Unit, integration, contract, E2E, type, lint, build, format, and architecture checks.
- Sonar, secrets, dependency, SAST, and security checks for risk-sensitive changes.
- Browser, screenshots, logs, traces, API probes, and metrics for runtime behavior.
- Self-review and specialist review for semantic risks.
- Reflection, promotion, and pruning events when evidence changes durable memory.

Prefer deterministic controls when they cheaply express the requirement. Use inferential review for product fit, architecture tradeoffs, security reasoning, UI quality, and test meaning.

Memory controls:

- Retrieve before action: record relevant `memory-index.json`, `known-failures.json`, `control-gaps.json`, docs, and files with `memory_engine.py retrieve`.
- Budget before broad reading: prefer path-plus-summary context, estimate tokens, and skip low-priority sources when selected context exceeds the target input budget.
- Reflect after evidence: record lessons with `memory_engine.py reflect` before promoting them.
- Promote selectively: write only evidence-backed semantic or procedural memory with `memory_engine.py promote`.
- Prune conservatively: record stale or superseded memory with `memory_engine.py prune`; prefer status/pruning logs over silent deletion.
- Treat missing, stale, conflicting, or low-confidence memory as a control gap when it can mislead a future agent.

Context economy controls:

- Keep stable reusable prompt material before volatile request data to improve cache reuse and reduce prompt churn.
- Put large logs, docs, screenshots, and command output behind artifact paths; summarize only the inspected result in the prompt.
- Repeat critical phase goals and gating rules at the end of long prompt packets.
- Compact into `handoffs/continuation.md`, split the task, or narrow retrieval when budget status is `above_target` or `compression_recommended`.

Permission tiers:

- Always: read/search files, inspect git state, run documented safe commands, create local evidence, update `.harness`.
- Ask first: dependencies, CI, migrations, external systems, credentials, publishing, deployment, public API compatibility changes, expensive Docker runs.
- Never without explicit override: commit secrets, fabricate evidence, remove failing tests to pass checks, rewrite unrelated user changes, claim production verification from local evidence.
