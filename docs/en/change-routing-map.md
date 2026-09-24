# Change Routing Map

> Japanese Source of Truth: [変更内容ごとの案内表](../jp/変更内容ごとの案内表.md)

Keep a table that lets you go directly from the kind of change to the implementation to read first, the validation to run first, and the detailed documentation to consult only when needed.

The important idea is to reuse existing responsibility boundaries, dependency direction, and source/test relationships as routing sources instead of rediscovering related areas across the whole repository on every change.

## Purpose

Do not make the AI rediscover which files and tests matter by exploring the whole repository each time. Use the change category to determine the initial working set mechanically or semi-mechanically.

Example:

```text
Change area | Main implementation | Tests to run first | Docs if needed
Startup/UI  | src/app/*           | test_app_*         | docs/ui.md
Persistence | src/data/*          | test_save_*        | docs/data.md
AI logic    | src/ai/*            | test_ai_*          | docs/ai.md
```

## Source + Test routing

Task Routing applies not only to documents but also to implementation and validation.

Recommended order:

```text
Task type / changed area
  -> target source
  -> matching targeted tests
  -> direct dependencies
  -> detailed docs only if needed
  -> full test suite before completion when appropriate
```

For a small change, run targeted tests first, then proceed to the project's standard completion validation if there are no problems.

## Architecture-defined routing

If the architecture itself defines responsibilities and formal dependency paths, reuse those boundaries as input to the Change Routing Map.

For example, if an existing architecture clearly defines ownership and communication boundaries such as UI / Process / Data, Application / Domain / Infrastructure, or frontend / backend / storage, the change type can select only the relevant responsibilities first.

```text
UI display change
  -> UI responsibility
  -> inspect backend/data only if the contract changes

Data persistence change
  -> storage/data responsibility
  -> UI normally out of scope

Inter-layer message change
  -> sender boundary
  -> message contract
  -> receiver boundary
```

This does not standardize a particular layer structure. The point is to reuse responsibilities, dependency direction, and boundaries that the project already defines in order to reduce exploration.

## Start large documents with heading search

If README / SPEC / design documents are large, do not read them from the beginning by default. Search headings or keywords first, then read the relevant section.

```text
search headings / keywords
  -> relevant section
  -> surrounding section only if needed
```

## Baseline invariants

If there are known behaviors, compatibility conditions, or performance properties that a change must not break, keep them as short invariants in the AI entry point.

Do not duplicate the full specification. Keep only the invariants needed for change decisions.

## Sensitive / generated data routing

Exclude measured logs, evaluation output, save data, backups, and reference data from normal implementation-change context.

Read them only when needed, and let the project identify areas that must not be modified without explicit instruction.

## Reproducible transformations

For changes involving large amounts of data or mechanical transformation, prefer a rerunnable transformation over bulk manual editing.

When possible, provide:

- dry-run
- an explicit target scope
- before/after validation
- processing that is safe to rerun

This reduces the need for an AI to read and rewrite large data directly.

## Validation trust

Prefer exit codes, explicit pass/fail results, and required measured conditions over raw test counts or log volume.

For performance-related changes, when appropriate, compare under equivalent conditions such as the same seed, fixed timestep, or identical input and verify that the expected behavior trend is preserved.

## Final report

A completion report should summarize the following instead of reproducing a long work history:

- changed files
- compatibility / behavior impact
- validation performed
- unverified areas

When something remains unverified, it is acceptable to state it explicitly and hand it off instead of broadening exploration just to fill the gap.

## Standard recommendations

- route directly from change category to source / tests / docs
- reuse existing architectural responsibilities, dependency direction, and boundaries as routing sources
- search headings before reading large documents in full
- keep important invariants short at the entry point
- exclude measured output, saves, backups, and similar data from normal context
- prefer rerunnable transformations with dry-run for bulk changes
- use targeted tests first, then standard completion validation
- compress final reporting to changed files / impact / validation / unverified
