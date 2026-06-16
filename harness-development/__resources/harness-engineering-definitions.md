# Harness Engineering Definitions

Research date: 2026-06-15

## Working Definition

Harness engineering is the practice of designing, codifying, and continuously improving the non-model system around an autonomous software-development agent so the agent's work is steerable, observable, auditable, and increasingly hard to get wrong in known ways.

For coding agents, the harness includes repository instructions, project memory, task state, tool registries, command runners, MCP servers, permission boundaries, sandboxes, verification scripts, linters, tests, review agents, trace logs, and the human approval process. The model supplies latent capability. The harness turns that capability into controlled software-engineering behavior.

## Definitions From Current Sources

| Source | Definition or emphasis | Practical meaning for development |
| --- | --- | --- |
| IEEE software-engineering glossary, classic test-harness usage | A test driver invokes the module under test, provides inputs, controls and monitors execution, and reports results. "Test harness" is listed as a synonym for test driver. | Harness thinking starts with controlled execution and measured results. The AI-agent version expands this from testing code to governing the agent that changes code. |
| Mitchell Hashimoto, "My AI Adoption Journey" | Harness engineering is the practice of engineering a solution whenever an agent makes a mistake so the agent does not repeat that mistake. He identifies two concrete forms: better implicit prompting through files such as `AGENTS.md`, and actual programmed tools such as screenshot scripts and filtered test runners. | Treat every repeated agent failure as a missing control. Add a rule, tool, fixture, or verifier so the next run gets faster, safer feedback. |
| OpenAI, "Harness engineering: leveraging Codex in an agent-first world" | The engineer's role shifts toward repository knowledge, agent legibility, architecture enforcement, validation, review, feedback handling, recovery, and recurring cleanup. | The repository becomes the system of record for how agents work. Humans design control systems and validate outcomes rather than manually writing every line. |
| LangChain, "The Anatomy of an Agent Harness" | "Agent = Model + Harness." A harness is every piece of code, configuration, and execution logic that is not the model itself: prompts, tools, infrastructure, orchestration, hooks, middleware, state, feedback loops, and constraints. | A model alone is not an agent. An agent becomes useful when the surrounding harness gives it memory, tools, execution ability, and enforceable constraints. |
| Martin Fowler / Thoughtworks, "Harness engineering for coding agent users" | A coding-agent harness combines feedforward guides and feedback sensors to regulate the codebase toward a desired state. Useful categories include maintainability harnesses, architecture fitness harnesses, and behavior harnesses. | A mature harness is not one thing. It is a control system with different sensors for code quality, architecture, runtime behavior, and human judgment. |
| "AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents" preprint | A harness is a runtime substrate that manages context, tools, project memory, task state, observability, failure attribution, verification, permissions, and maintenance state so latent model coding capability becomes auditable behavior. | The harness is the runtime interface between the model and the development environment. Its job is to make work traceable and evidence-backed, not merely generated. |
| Software Improvement Group, "What is harness engineering?" | Harness engineering designs the full environment an AI agent operates within: the rules it follows, checks it must pass, and feedback loops that prevent the same mistake from recurring. | Harness engineering closes the gap between deploying agents and governing what they produce. |

## Boundary With Related Terms

| Term | Scope | Difference from harness engineering |
| --- | --- | --- |
| Prompt engineering | Shapes a single model interaction through instructions, examples, and phrasing. | A harness governs the full development episode across many model calls, tools, files, checks, approvals, and feedback loops. |
| Context engineering | Controls what the model can see: retrieved docs, memory, compressed history, examples, and task context. | Context engineering is one layer of the harness. A full harness also controls action, permissions, verification, observability, and maintenance. |
| Test harness | Invokes and measures software under test. | A development harness also shapes the behavior of the agent doing the implementation. Testing remains one important feedback layer. |
| Agent framework | Provides reusable infrastructure for agent loops, tool calling, orchestration, memory, or routing. | A harness is the project-specific configuration of supports, constraints, evidence, and policies exposed to an agent. It can be built on top of an agent framework. |
| DevOps or platform engineering | Provides infrastructure for builds, deployment, environments, CI/CD, and operational workflows. | A harness uses those systems but focuses specifically on the runtime relationship between autonomous agents and the software-development environment. |

## Core Components

- Model: the probabilistic reasoning and code-generation engine.
- Agent loop: the repeated observe, plan, act, inspect, and revise cycle.
- Project memory: architecture, conventions, known failure modes, domain rules, test strategy, runbooks, and prior decisions.
- Tool surface: code search, file editing, shell commands, browser control, test runners, build tools, package managers, debuggers, profilers, static analyzers, and deployment tools.
- Permission boundary: what the agent may read, edit, run, delete, install, publish, merge, or escalate.
- Verification system: deterministic checks, test suites, fixtures, visual tests, type checks, security scans, performance checks, and explicit evidence reports.
- Observability system: action traces, tool logs, command outputs, screenshots, videos, runtime traces, metrics, and failure-attribution logs.
- Human governance: prioritization, acceptance criteria, product judgment, risk decisions, approval gates, and post-run review.
- Entropy control: recurring cleanup, drift detection, stale documentation checks, dependency audits, and refactoring tasks.

## Development-Phase Lifecycle

1. Intake: the human or product system gives a task, scope, constraints, and acceptance criteria.
2. Context selection: the agent reads relevant project memory, architecture rules, tests, and known failure modes.
3. Planning: the agent records a plan, assumptions, inspected files, open questions, and verification strategy.
4. Action: the agent edits code through allowed tools in an isolated branch or worktree.
5. Local feedback: fast checks run while the agent works, such as type checks, targeted tests, linters, screenshots, static analysis, and runtime probes.
6. Failure attribution: when a check fails, the agent records what failed, why it believes it failed, and the next diagnostic action.
7. Completion verification: the agent maps each acceptance criterion to evidence, including tests run, behavior observed, risks checked, and regressions considered.
8. Review and merge: human and/or agent reviewers inspect the diff, evidence, risk profile, and residual uncertainty.
9. Harness update: repeated mistakes, avoidable human interventions, missing tools, unclear docs, and weak checks are converted into durable harness improvements.

## Source Index

- IEEE Std 610.12-1990, software-engineering glossary: https://www.nist.gov/system/files/documents/2025/04/29/61012-1990.pdf
- Mitchell Hashimoto, "My AI Adoption Journey": https://mitchellh.com/writing/my-ai-adoption-journey
- OpenAI, "Harness engineering: leveraging Codex in an agent-first world": https://openai.com/index/harness-engineering/
- LangChain, "The Anatomy of an Agent Harness": https://www.langchain.com/blog/the-anatomy-of-an-agent-harness
- Martin Fowler / Thoughtworks, "Harness engineering for coding agent users": https://martinfowler.com/articles/harness-engineering.html
- "AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents": https://arxiv.org/html/2605.13357v1
- Software Improvement Group, "What is harness engineering?": https://www.softwareimprovementgroup.com/blog/what-is-harness-engineering/

