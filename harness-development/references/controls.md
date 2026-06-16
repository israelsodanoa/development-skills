# Controls Reference

Use feedforward controls before action and feedback controls after action.

Feedforward controls:

- Accepted spec and success criteria.
- Project map and relevant architecture/testing/domain memory.
- Command registry with exact executable commands.
- Known failures and local anti-patterns.
- Permission policy for destructive, networked, credentialed, schema, dependency, CI, release, and production actions.

Feedback controls:

- Unit, integration, contract, E2E, type, lint, build, format, and architecture checks.
- Sonar, secrets, dependency, SAST, and security checks for risk-sensitive changes.
- Browser, screenshots, logs, traces, API probes, and metrics for runtime behavior.
- Self-review and specialist review for semantic risks.

Prefer deterministic controls when they cheaply express the requirement. Use inferential review for product fit, architecture tradeoffs, security reasoning, UI quality, and test meaning.

Permission tiers:

- Always: read/search files, inspect git state, run documented safe commands, create local evidence, update `.harness`.
- Ask first: dependencies, CI, migrations, external systems, credentials, publishing, deployment, public API compatibility changes, expensive Docker runs.
- Never without explicit override: commit secrets, fabricate evidence, remove failing tests to pass checks, rewrite unrelated user changes, claim production verification from local evidence.
