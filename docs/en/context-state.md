# Context State / Information Responsibilities

> Japanese Source of Truth: [現在の状態を短くまとめる](../jp/現在の状態を短くまとめる.md)

This document describes how to compress the current project state and separate responsibilities between information sources.

## Compressed Project State

Instead of rereading the whole project on every task, you may keep a short state summary containing only the current major capabilities, constraints, and known unimplemented items.

A state summary is not a replacement for detailed specifications. It is an entry point that helps an AI understand what the project can currently do.

Recommended content:

- currently available major capabilities
- current explicit constraints
- known unimplemented items
- the current highest-priority goal, when useful

## Separate stable policy from the current task

```text
AI_CONTEXT / agent guide
  -> long-lived policy, index, and routing

Current state summary
  -> current implementation capabilities and constraints

Task Capsule / Context Pack
  -> current task only
```

Prefer a structure where changing the task does not require rewriting long-lived policy.

## Information source responsibilities

Repeating the same detailed information in multiple places causes update drift and increases context. For detailed duplication control, see [Documentation Duplication Control](documentation-duplication-control.md).

Examples:

- README: human-facing overview, installation, and usage
- AI_CONTEXT.md: AI-facing index, read order, important constraints, and routing
- state summary: current implementation capabilities and constraints
- docs: detailed specifications and design contracts
- Issue tracker: requests, discussion, priority, and unfinished work
- source / tests: implementation and actual behavior
- generated artifacts: derived outputs consulted only when needed

## Read order

For implementation tasks, the following order is often useful:

```text
task area
  -> target source
  -> matching tests
  -> detailed docs when needed
```

When the primary task is specification judgment, prioritize the formal design documents. Define task-specific read order through Task Routing.

## Generated artifacts

Normally do not read automatically generated diagrams, reports, caches, or analysis results. Read them only when the generated output or generation logic is the target, or when they are needed for a decision.

## Completion gates

Make completion conditions configurable when appropriate.

Examples:

- tests
- compile / build
- generated document consistency
- diff sanity check

On success, keep only the result in the Context Pack. Add detailed output only when a check fails.

## Ambiguity

If a state or assumption is unclear, do not invent an answer merely to reduce context. Inspect the necessary original source instead.
