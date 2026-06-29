# Tools Reference

Command registry entries live in `.harness/config/command-registry.json`.

Required command fields:

- `id`
- `command`
- `workdir`
- `purpose`
- `when_to_run`
- `expected_runtime`
- `risk`
- `approval_required`
- `required_before_completion`
- `success_signal`
- `failure_protocol`

Tool protocol:

- Prefer registered commands over guessed commands.
- Record command, working directory, purpose, result, output path, and next action.
- Require approval for commands that mutate state, pull images, use credentials, deploy, publish, access production, or run expensive workflows.
- Treat tool output as evidence only for what it actually proves.
- Preserve raw logs in request evidence when useful.
- Keep `evidence/manifest.md` present for every request and refresh it when command, runtime, review, or verification evidence changes.

MCP tools should be discovered before use and treated with the same purpose, risk, permission, and evidence rules as shell commands.
