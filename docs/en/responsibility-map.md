# Responsibility Map / Policy Check

> Japanese Source of Truth: [ファイルとモジュールの役割表](../jp/ファイルとモジュールの役割表.md)

This document defines a standard approach for using a short responsibility map to understand what files own before reading all source, while moving mechanically decidable policy rules into compact checker output.

The key is to separate the responsibility index from machine-checkable policy and create a short path to implementation candidates relevant to the current task.

## 1. Responsibility Map

In a large repository, do not force the AI to infer responsibility from filenames alone. Keep a short responsibility map when useful.

Example:

```text
File / module            Responsibility
src/lexer.*              source -> token stream
src/parser.*             token stream -> syntax tree
src/diagnostic.*         diagnostic representation
```

Keep descriptions short. Do not turn the map into a list of helper functions.

The AI uses the map to narrow candidate files for the current task before reading detailed implementation.

## 2. Responsibility Map as an architecture signal

A responsibility map can also reveal structural growth.

If one record cannot be explained in one short sentence and starts requiring descriptions such as `A and B and C`, review whether the file / class / module has accumulated too many responsibilities.

This is not an automatic instruction to split it. Treat it as a signal to re-check responsibility boundaries.

## 3. Keep the map current

When using a Responsibility Map, update it in the same change set when:

- adding a major file / module
- moving a responsibility to another file
- splitting or merging files
- changing public architectural ownership

A stale responsibility map creates incorrect routing. If it cannot be maintained, do not treat it as an authoritative routing source.

## 4. Mechanical policy checks

Move mechanically decidable coding rules into a checker / lint / static analysis instead of making the AI reread the entire policy on every task.

Examples:

- size thresholds
- forbidden placement
- naming patterns
- required documentation
- generated-path exclusion

Keep normal AI-facing output compact.

```text
OK policy-check
```

When findings exist:

```text
W path:line RULE short message
E path:line RULE short message
NG policy-check: 2
```

## 5. Do not pretend architecture is fully machine-checkable

Do not force responsibility separation, semantic ownership, design boundaries, and similar rules that are difficult to prove mechanically into a checker.

Recommended split:

```text
mechanically decidable rules
  -> checker / lint

architectural / semantic rules
  -> responsibility map + targeted review
```

This reduces constant policy loading without introducing avoidable false positives.

## 6. Scoped exceptions

When a checker needs exceptions, define them by path / rule rather than weakening the policy itself.

Examples:

```text
path generated/**
rule DOC third_party/**
```

Keep exception lists small and limited to cases with clear reasons such as legacy, generated, or third-party code.

## 7. Context routing with responsibility data

A Responsibility Map can be combined with Change Routing Map and Source Structure Index.

```text
Task / changed area
  -> Responsibility Map
  -> candidate files
  -> changed symbols / structure index
  -> matching tests
  -> source details only if needed
```

For a small project, do not create a dedicated map when a short table in `AI_CONTEXT.md` or an existing architecture document is enough.

## 8. Implementation options

The format is not fixed. Markdown tables, JSON, generated indexes, or existing architecture metadata are all valid if they provide a short path from the current task to the responsible area.

Likewise, do not create a custom policy checker when existing lint/static analysis is sufficient. If you do create one, return only findings that can be decided reliably and leave semantic ownership or similar judgments to targeted review.

## 9. Standard recommendations

- use a short Responsibility Map as a routing source in large projects when useful
- treat an expanding responsibility description as a signal for structural review
- update the map in the same change set as source responsibility changes
- move mechanically decidable policy into compact checker output
- keep only the result for successful checks rather than long logs
- do not force architecture / semantic rules into machine checks
- scope exceptions explicitly by path / rule
