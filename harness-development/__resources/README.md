# Harness Engineering Resources

Research date: 2026-06-15

This folder summarizes harness engineering for autonomous software-development agents. The term is new, but the underlying idea is familiar to software engineering: quality rises when the system around the work makes good behavior easy, bad behavior detectable, and repeated mistakes structurally harder to repeat.

## Documents

- [harness-engineering-definitions.md](harness-engineering-definitions.md) defines harness engineering, distinguishes it from test harnesses, prompt engineering, context engineering, agent frameworks, and DevOps, and gives a working definition for autonomous coding agents.
- [harness-control-layers.md](harness-control-layers.md) describes the control layers that wrap an agent during the development phase, including feedforward guides, feedback sensors, permissions, traceability, verification, and entropy control.
- [quality-through-autonomous-agent-harnesses.md](quality-through-autonomous-agent-harnesses.md) explains how the structure raises feature quality, what evidence a feature should produce, which metrics to track, and which failure modes each control catches.

## Working Summary

Harness engineering is the discipline of designing and continuously improving the non-model system around an autonomous coding agent: repository instructions, project memory, tool access, permissions, task state, observability, verification gates, review loops, and recurring maintenance controls.

In practice, it changes the role of the engineer. The engineer does less line-by-line implementation and more environment design: defining acceptance criteria, making project knowledge agent-readable, exposing safe tools, encoding architectural rules, requiring empirical proof of completion, and converting every repeated agent failure into a durable control.

The central quality mechanism is simple:

1. Tell the agent what good looks like before it starts.
2. Give it safe, high-signal tools while it works.
3. Require deterministic and reviewable evidence before completion.
4. Capture failures and interventions as changes to the harness.
5. Run continuous drift controls so quality does not decay after merge.
