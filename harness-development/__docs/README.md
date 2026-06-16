# Harness Development Skill Functional Specification

Research date: 2026-06-15

This directory contains the functional requirements specification for a future Codex skill that uses harness engineering to manage project development with autonomous agents.

The specification is organized as a set of documents instead of one large file so the future skill can follow progressive disclosure: load the core operating requirements first, then load workflow, control, memory, prompt, tool, and evaluation details only when needed.

## Document Index

- [functional-requirements-specification.md](functional-requirements-specification.md): primary product and functional requirements for the Harness Development skill.
- [use-cases-and-workflows.md](use-cases-and-workflows.md): use cases and end-to-end operating workflows for feature, bug, refactor, UI, security, and maintenance work.
- [control-layer-requirements.md](control-layer-requirements.md): feedforward, feedback, permission, verification, observability, review, entropy, and governance controls.
- [state-memory-and-prompting-requirements.md](state-memory-and-prompting-requirements.md): agent state model, project memory controls, context-selection rules, prompting strategies, and handoff protocols.
- [tools-and-integration-requirements.md](tools-and-integration-requirements.md): required tools, command registries, scripts, MCP integrations, Codex skill packaging, and repository integration requirements.
- [evaluation-and-quality-requirements.md](evaluation-and-quality-requirements.md): acceptance criteria, evidence contracts, metrics, trace schema, maturity model, and completion audit requirements.

## Source Basis

The requirements are derived from the local `resources/` documents and current external references:

- OpenAI, "Harness engineering: leveraging Codex in an agent-first world": https://openai.com/index/harness-engineering/
- OpenAI Developers, "Agent Skills": https://developers.openai.com/codex/skills
- OpenAI Developers, "Codex web": https://developers.openai.com/codex/cloud
- OpenAI Cookbook, "Build an Agent Improvement Loop with Traces, Evals, and Codex": https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop
- OpenAI Cookbook, "Build iterative repair loops with Codex": https://developers.openai.com/cookbook/examples/codex/build_iterative_repair_loops_with_codex
- Martin Fowler / Thoughtworks, "Harness engineering for coding agent users": https://martinfowler.com/articles/harness-engineering.html
- LangChain, "How to Build a Custom Agent Harness": https://www.langchain.com/blog/how-to-build-a-custom-agent-harness
- Anthropic, "Building effective agents": https://www.anthropic.com/engineering/building-effective-agents
- Anthropic, "Harness design for long-running application development": https://www.anthropic.com/engineering/harness-design-long-running-apps
- "AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents": https://arxiv.org/pdf/2605.13357

## Assumptions

- The future skill name will be `harness-development` unless renamed before implementation.
- The skill will be used by Codex-style autonomous coding agents that can read files, edit code, run commands, use MCP tools, and report evidence.
- The skill will manage project development, not only generate code. Its responsibility includes task intake, planning, state management, verification, review loops, and harness improvement.
- The skill will support both new projects and existing repositories.
- The skill will not bypass human judgment for destructive actions, production access, security decisions, irreversible migrations, or ambiguous product requirements.

## Specification Status

This is a functional specification, not the final skill implementation. It defines the ideal operating scenario and implementation requirements for a future `SKILL.md`, bundled `references/`, optional `scripts/`, and optional `agents/openai.yaml`.

