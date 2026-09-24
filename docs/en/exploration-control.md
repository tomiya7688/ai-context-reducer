# Exploration Control / Stop Conditions

> Japanese Source of Truth: [探索を止める条件を決める](../jp/探索を止める条件を決める.md)

This document defines a standard policy for preventing an AI from continuously widening repository exploration "just in case."

The important point is to define not only how exploration starts, but also when it must stop once the necessary information is available.

## 1. Search first, read second

Do not start with full-file reads. Narrow candidates with search, indexes, changed files, and Issue metadata, then read only the necessary original sources.

```text
Search / metadata / index
    ↓
Candidate files / symbols
    ↓
Target source + matching tests
    ↓
Detailed docs only if needed
```

Search results and structure indexes are entry points for narrowing what to read, not replacements for original sources.

## 2. Exploration Stop Condition

Context reduction requires deciding not only what to read but when to stop reading.

Recommended minimum conditions before proceeding to implementation:

- Goal: what must be achieved is understood
- Required: mandatory constraints are known
- Acceptance: completion / validation conditions are known
- Working set: target source / tests / docs are identified
- Deferred scope: what is not being done now is explicit when needed

When these are sufficient, stop additional exploration.

Retrieve more original-source context only when a new unknown appears during implementation or validation.

## 3. Evidence Budget / Bounded Evidence Collection

For tasks where "enough" is unclear and exploration tends not to stop, separate Required and Optional evidence.

Example:

```text
Required evidence:
- current task / issue requirements
- target implementation
- matching tests
- applicable policy / design source

Optional evidence:
- history
- adjacent modules
- broad docs
```

A new read / search should normally:

- fill missing Required evidence
- resolve conflicting evidence
- support an Acceptance / validation decision
- investigate a newly discovered dependency or impact
- identify the cause of a failure
- close an important security / compatibility unknown

Stop "just in case" exploration that satisfies none of these.

When useful, keep a short Evidence Ledger.

```text
Known:
- implementation: src/foo.py
- tests: tests/test_foo.py
- policy: docs/foo.md

Missing:
- none

Unverified:
- Windows packaging
```

This is not a hard token cap. Do not sacrifice correctness merely to remain under a numeric limit.

See [Evidence Budget](evidence-budget.md) for details.

## 4. Explicit deferred scope

A task may state not only what is being done, but also what is explicitly not being done now.

Example:

```text
Goal: add legal move generation
Deferred: repetition / search / optimization
```

Do not expand exploration or changes into deferred behavior / out-of-scope modules unless they are required to complete the current task.

This does not reject future work. It fixes the current Context Pack boundary. Keep a reference to future work in an Issue or formal plan.

## 5. Non-task filtering

An Issue tracker often contains items that are not implementation tasks.

Examples:

- roadmap
- backlog
- index
- policy
- meta Issue
- umbrella Issue

When selecting the next task mechanically, filter these out before producing implementation candidates.

Do not make the AI reread all Issues on every selection just to determine which ones are actionable.

## 6. Acceptance-first task packet

In a Task Capsule / Context Pack, prioritize the following over the entire Issue body:

```text
Task ID
Priority
Title
Goal
Required constraints
Acceptance / completion conditions
Deferred / out of scope
Relevant files / symbols
Source of truth reference
```

Having Acceptance and deferred scope early establishes exploration-stop conditions, validation conditions, and boundaries at the same time.

## 7. Reproducible split packet

A Context Pack does not need to be one file.

If it becomes long, split it into small reproducible components.

```text
context/<task-id>/
├─ task.md
├─ files.txt
├─ symbols.txt
├─ constraints.md
└─ diff.patch
```

This allows only the necessary parts to be read and machine-generated components to be refreshed independently. The directory and filenames are not part of the standard.

## 8. Changed symbols

When class / function / method symbols can be extracted mechanically from changed files, use them.

This can narrow the working set before reading a large changed file in full.

## 9. Bounded diff

If a Task Packet contains a diff, do not copy the entire diff without limit.

- inspect changed files / diff stat first
- cap diff excerpts when appropriate
- make truncation explicit
- return to the full original diff when required for a decision

## 10. Unverified areas

Do not read an entire repository merely for safety. State what has not been verified.

```text
Validation
- targeted tests: passed
- full integration test: not run
- platform-specific path: unverified
```

Even when Evidence Budget is used, do not explore merely to force Unverified to zero. Promote only unknowns that are required for correctness of the current task into Required evidence.

## 11. Scope containment

Do not mix unrelated refactors into the current task.

Also avoid speculative performance optimization before tests or contracts establish the correctness boundary of the behavior. Fix correctness first; treat optimization as a later task when necessary.

This reduces change volume, review volume, and context, and prevents optimization work from expanding exploration into unsettled behavior.

## 12. Standard recommendations

- Search first, read second
- use Goal / Required / Acceptance as exploration-stop conditions
- separate Required / Optional evidence when a task tends not to stop exploring
- if the next read/search cannot be tied to a missing item, conflict, or Acceptance check, prefer stopping
- keep an Evidence Ledger short and pointer-based
- do not sacrifice correctness to a hard token cap
- state Deferred / Out of Scope when useful
- filter non-implementation items before next-task selection
- include Acceptance early in the Context Pack
- use changed symbols to narrow the working set when available
- bound diffs and logs when appropriate
- state unverified areas explicitly
- do not mix unrelated refactors into the current task
- do not expand into unnecessary optimization before a correctness boundary exists
