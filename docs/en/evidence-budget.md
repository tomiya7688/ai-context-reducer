# Evidence Budget / Context Budget

> Japanese Source of Truth: [確認する根拠の量を決める](../jp/確認する根拠の量を決める.md)

Evidence Budget is an optional method for deciding in advance which categories of evidence are necessary for the current task so that an AI does not keep expanding search and reading "just in case."

It is not a mechanism for counting an exact number of tokens.

> Before additional exploration, be able to explain which missing evidence the next read/search will fill.

It is a form of **bounded evidence collection** that makes Exploration Control stop conditions easier to apply in practice.

## Basic principle

At task start, when useful, separate evidence into categories such as:

```text
Required evidence:
- current task / issue requirements
- target implementation
- matching tests
- authoritative design / policy source

Optional evidence:
- adjacent modules
- history
- broad documentation
- unrelated integration details
```

When Required evidence is present, non-contradictory, and sufficient to judge Acceptance, prefer stopping exploration.

## Not a numeric token budget

This method is not intended to impose a fixed rule such as "read at most 8000 tokens."

Strict token caps:

- differ between models
- do not reflect task complexity well
- risk prioritizing a hard cap over correctness

Therefore they are not a standard requirement.

Instead, manage **evidence categories and conditions for further exploration**.

## Conditions for additional exploration

A new read / search / fetch should normally satisfy at least one of these conditions:

1. fill missing Required evidence
2. resolve a conflict between existing evidence
3. support an Acceptance / validation decision
4. investigate a newly discovered dependency or impact during implementation
5. identify the cause of a failure
6. close an important unverified area such as security or compatibility

Stop lateral exploration that satisfies none of these and is only "just in case."

## Required / Optional evidence

### Required

Evidence necessary to implement and validate the current task correctly.

Examples:

- Goal / Required / Acceptance
- target source
- matching regression tests
- current interface / schema
- applicable architecture policy
- changed diff

### Optional

Evidence that may be useful but is not necessary for the current decision.

Examples:

- commit history
- neighboring subsystem documentation
- broad architecture overview
- historical design discussion
- unrelated Issues

Promote Optional evidence only when a question on the Required side makes it necessary.

## Evidence Ledger

For a complex task, keep a short temporary ledger.

```text
Known:
- implementation: src/foo.py
- tests: tests/test_foo.py
- policy: docs/foo-policy.md

Missing:
- error contract for FooError

Unverified:
- Windows packaging
```

Do not create a long summary. Prefer pointers, files, symbols, and Issue IDs.

### Known

Pointers to original sources that have been checked and are currently supporting the decision.

### Missing

Required evidence that is still absent.

When this becomes `Missing: none`, re-check whether there is a real reason broad exploration still needs to continue.

### Unverified

Areas that have not been checked but do not necessarily block completion of the current task.

You do not need to read the whole repository just to reduce Unverified to zero.

## Connection to stop conditions

Exploration Control uses stop conditions such as:

- Goal understood
- Required known
- Acceptance known
- Working set identified
- Deferred scope known

When Evidence Budget is used, also check:

```text
Required evidence missing: none
Evidence conflicts: none / resolved
Acceptance evidence: sufficient
Unverified areas: explicit
```

Once these are satisfied, proceed to implementation / validation.

## Triggers for renewed exploration

Stopping exploration is not permanent. Resume when new facts arise during implementation.

Examples:

- the target function turns out to be a shared public API
- a test failure reveals another module dependency
- a config schema change also affects a distribution artifact
- a design document conflicts with source

Even then, retrieve only the scope required for the newly discovered unknown.

```text
new unknown
  -> one evidence gap
  -> targeted search/read
  -> gap resolved
  -> stop again
```

## Evidence escalation

Do not start with the largest scope.

```text
current source + matching tests
        ↓ insufficient
one direct dependency / authoritative doc
        ↓ insufficient
subsystem context
        ↓ only if still required
broader repo/history
```

Every expansion should have a reason.

## Relationship with Context Pack

Do not turn the Context Pack into a large research notebook.

If you preserve an Evidence Ledger, this level is usually enough:

```text
Evidence
- Known: src/foo.py, tests/test_foo.py, docs/foo.md
- Missing: none
- Unverified: macOS packaging
```

Do not copy original contents into the Context Pack.

## Search results / summaries

Search output, summaries, and structure indexes may not themselves be authoritative Required evidence.

```text
index/search
  -> candidate selection
  -> authoritative source/test/doc
```

Return to the original source when an important decision requires it.

## Example: small bug fix

```text
Required:
- issue reproduction
- target function
- matching regression test

Optional:
- module history
- sibling modules
- full architecture docs
```

Once the three Required items are known, begin implementation without reading history or the full architecture documentation.

## Example: schema change

```text
Required:
- schema source
- producer
- direct consumers
- compatibility tests
- migration / versioning policy

Optional:
- unrelated package docs
```

Expand the Evidence Budget only if consumer impact proves broad.

## Example: package build failure

```text
Required:
- build metadata
- failing command/error excerpt
- generated artifact contents
- artifact smoke requirement

Optional:
- application runtime internals
```

Prioritize artifact-boundary evidence rather than broadly reading runtime internals first.

## Signals that it is useful

- exploration is long even for coding tasks
- the AI rereads the same nearby files repeatedly
- exploration spreads easily into history / broad docs
- the Context Pack becomes a research notebook
- "full repo inspection just in case" is common
- search continues after Required evidence is already available

## When not to use it

Do not create a formal ledger for every small task.

For example, a one-line fix with an obvious target file and test normally needs only the regular exploration-stop rule.

Do not let Evidence Budget itself become additional context overhead.

## Safety

Evidence Budget is not a hard cap that sacrifices correctness.

Allow more evidence when required by:

- security-relevant unknowns
- public contract impact
- migration / data-loss risk
- a user-requested comprehensive review

```text
correctness
    > evidence completeness for the task
    > context reduction
```

## Minimal rule

Even without formally adopting Evidence Budget, one question is useful:

> Which missing evidence, conflict, or Acceptance check requires the next read/search?

If there is no answer, prefer stopping exploration.
