# Context Pack

> Japanese Source of Truth: [作業用メモ](../jp/作業用メモ.md)

A Context Pack is a temporary packet containing only the information an AI needs to perform the current task.

It is not a fixed large document. Rebuild it from the original sources using only the parts required for the task.

## Minimal structure

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

See `../../templates/CONTEXT_PACK.md` for the standard template.

## Highest-priority task fields

Start by establishing:

- Goal
- Required
- Acceptance

If the target source / tests and Out of Scope are also known, they can be used as exploration-stop conditions.

## Working Set

When possible, narrow not only to changed files but to changed symbols.

The normal read order is:

```text
target source
  -> matching tests
  -> direct dependencies
  -> detailed docs only if needed
```

## Validation

You do not need to fill every possible validation field.

Choose the smallest sufficient evidence for the change type, and explicitly list anything not checked under `Unverified areas`.

Do not treat `0 tests`, an empty scan, or a check that only found out-of-scope items as success evidence.

## Optional Extensions

Add these only when needed:

- Current State reference
- Remote Delta
- Policy Context / active exception
- Relevant Architecture
- headless / deterministic / visual validation
- disposable workspace
- structured runtime observation
- artifact validation
- performance measurement
- Source Excerpts

Project-specific fields may be added as long as they do not obscure the Core.

## Split Packet

If the packet becomes long, do not force everything into one file. Split it into small, reproducible components.

```text
task.md
files.txt
symbols.txt
constraints.md
diff.patch
```

The names and locations are not standardized.

## Not a Source of Truth

A Context Pack is a working snapshot.

Persist long-lived design decisions, specifications, and unfinished work in the official docs, Issues, source, tests, or other authoritative locations.

Do not keep appending generations of old Context Packs or repeatedly summarize them until they drift away from the original sources.

## Decision principle

If a Context Pack becomes large, first ask what can be removed rather than what else should be added.

```text
needed for the current task?
  yes -> keep
  no  -> omit / reference only
```

Preserve correctness while including only the information needed for the current decision.
