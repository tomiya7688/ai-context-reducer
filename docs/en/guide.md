# AI Context Reducer - Basic Guide

> Japanese Source of Truth: [基本方針](../jp/基本方針.md)

## 1. Purpose

`ai-context-reducer` collects ideas and methods that help an AI reach the required information through a short path instead of rereading an entire repository on every task.

Priority:

```text
correctness > speed of reaching the work target > context reduction > amount of automation
```

## 2. Core principles

### Search first, read second

Use search, indexes, changed files, and task metadata to narrow candidates before reading original sources.

### Summaries are indexes

Summaries, Current State, Context Packs, and structure indexes are not replacements for the Source of Truth. Return to source / tests / docs / diff when needed.

### Exploration-stop conditions

Stop broad exploration when the following are known at an implementation-ready level:

- Goal
- Required constraints
- Acceptance
- Working set

Resume exploration only when a concrete unknown appears during implementation or validation.

### Do not mix unrelated work

Do not mix unrelated refactors, legacy cleanup, or future work into the current task.

## 3. Responsibilities of information sources

```text
README -> human-facing overview
AI_CONTEXT / agent guide -> AI routing / index
Current State -> current capabilities and constraints
Detailed docs -> contracts / specification
Issues / tasks -> requirements / priority
Source / tests -> implementation / executable truth
Generated artifacts -> consulted only when needed
```

Avoid copying the same details into multiple locations.

## 4. Minimal core

The following applies to almost every project:

- a small AI entry point
- Search first, read second
- Source of Truth
- exploration-stop conditions
- targeted validation
- explicit Unverified areas
- normally exclude generated output / logs / broad history

For a small repository, this may be enough.

## 5. Add only when needed

Possible additions include:

- Current State
- Task Routing
- Change Routing Map
- Responsibility Map
- Remote Delta First
- Source Structure Index
- changed-symbol routing
- Validation Routing
- Policy Routing / compact checker
- headless-first validation
- disposable validation workspace
- deterministic seam
- artifact validation
- Boilerplate Generation

See [Adaptive Adoption](adoption-priority.md) for adoption priority and project fit.

## 6. Context Pack

A Context Pack is a temporary packet for the current task.

Minimal structure:

```text
Task
Out of Scope
Working Set
Required Constraints
Routed References
Validation
Change Summary
Exploration Status
```

If it becomes long, split it into small files. Do not make the Context Pack itself a long-lived Source of Truth.

## 7. Validation

Choose evidence based on the change type.

```text
change type -> smallest sufficient validation -> evidence validity check
```

Examples:

- pure logic -> targeted tests
- GUI / editor -> headless checks + visual confirmation when required
- random / time dependent -> fixed input / deterministic seam
- packaged app -> artifact smoke
- export / conversion -> disposable workspace
- rule-heavy code -> compact policy checker

A successful command that did not actually inspect a target, such as `0 tests` or an empty scan, is not valid evidence.

## 8. Large repositories

When reaching the target area repeatedly requires broad exploration, prioritize Responsibility Map, Task / Change Routing, and Current State.

Add Source Structure Index, changed-symbol routing, and split Context Pack only when the repository is large enough to justify them.

When multiple AIs, chats, or people update the same remote, prioritize Remote Delta First regardless of repository size.

## 9. AI-driven adoption

```text
README + adoption-priority + AI_CONTEXT template
        ↓
target repo shallow inspection
        ↓
project signals classification
        ↓
adopt Core
        ↓
add only high-value Optional methods
        ↓
report Adopted / Skipped / Why
```

Do not start by reading all source, all docs, or all Issues.

## 10. Avoid

- continuous whole-repository scanning
- one huge AI-specific document
- generations of summaries of summaries
- large numbers of AI-only files
- excessive routing/index structures in a small repository
- automation whose value cannot be explained
- unrelated refactors
- guessing to fill unverified areas

## 11. Adoption rule

Add a method only when:

```text
expected repeated context saving > adoption + maintenance cost
```

`ai-context-reducer` itself should keep the Core small and allow Optional methods to be added conditionally.
