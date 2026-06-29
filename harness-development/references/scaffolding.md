# Scaffolding Reference

Use `.harness/` as the target project's persistent harness folder.

Required layout:

```text
.harness/
  config/
    harness.json
    command-registry.json
  memory/
    memory-index.json
    known-failures.json
    control-gaps.json
  sonar/
    docker-compose.sonar.yml
    sonar-project.properties
    .env.example
    sonar-config.json
  requests/
    <request_id>/
      spec.md
      intake.md
      plan.md
      tasks.md
      state.json
      history.jsonl
      handoffs/
        continuation.md
      prompt-packets/
        intake.md
        specify.md
        plan.md
        tasks.md
        implement.md
        failure.md
        review.md
        verify.md
        improve.md
        handoff.md
      evidence/
        manifest.md
        commands/
      verification-report.md
  reports/
```

Rules:

- Keep Python engine scripts in the skill package, not in target `.harness/`.
- Treat `.harness/requests/<request_id>/` as the source of truth for implementation work.
- Do not overwrite request history, handoffs, evidence, reports, or user-edited memory unless `--force` is explicitly passed.
- Scaffold updates are additive by default.
- Keep the local Sonar scaffold token-free; no `SONAR_TOKEN` is required for Docker-local scans.
- Store other secrets only as environment-variable names or redacted references.
- Record the skill engine path in `.harness/config/harness.json` so generated commands can locate the shared engine.
