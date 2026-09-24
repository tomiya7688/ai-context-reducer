# Change Impact / Test Impact Routing

> Japanese Source of Truth: [変更の影響範囲から検証対象を絞る](../jp/変更の影響範囲から検証対象を絞る.md)

This method narrows the required validation scope from changed files / symbols / packages.

> The goal is not to minimize the test count itself. Avoid the full suite and huge logs only while preserving all validation that is needed.

Treat existing ideas such as Test Impact Analysis / affected-test selection as lightweight routing that does not depend on a particular CI or coverage product.

## Basic flow

```text
changed files / symbols
        ↓
responsibility / dependency / ownership information
        ↓
likely affected tests
        ↓
smallest sufficient validation
        ↓
impact uncertainty / shared contract check
        ↓
broader / full validation when needed
```

While `Validation Routing` selects the evidence type from the nature of the change, this method decides **which test scope that evidence should cover**.

## Level 1: Static / Explicit Mapping

This is the lowest-cost level.

Example:

```text
src/parser/*      -> tests/parser/*
src/save/*        -> tests/save/*
apps/editor/*     -> tests/editor/*
package metadata  -> build + artifact smoke
```

Use source/test naming conventions, directory structure, and existing routing tables.

For a small to medium repository, this may be sufficient.

### Candidate inputs

- source ↔ test naming convention
- Change Routing Map
- Responsibility Map
- package / module ownership
- explicit test command table

## Level 2: Dependency / Symbol Based

When static mapping is ambiguous, use import / call / dependency / public contract information.

Example:

```text
changed symbol
  -> direct consumers
  -> tests covering those consumers
```

Do not require a huge complete call graph. Reuse an existing Source Structure Index or language-standard tool when it is sufficient.

In this repository, `source-structure-index affected` provides a lightweight fallback that derives the module/package containing a changed file and its transitive dependents from indexed `contains_file` / `depends_on` relationships. The Python and native Go versions use the same `acr-source-structure-index-v1`.

### Bounded output / complete internal closure

Do not stop internal traversal early in a way that creates false negatives.

- Compute the complete internal dependency closure
- Bound only the affected modules returned to the agent
- Treat results beyond the return limit as broad impact
- Fall back to broader validation when the index is truncated, a changed file is outside the index, or ownership is unknown

The agent context is bounded; internal analysis required for correctness is not.

## Level 3: Coverage-assisted

When trustworthy coverage data already exists, it may be used as a supporting signal.

```text
changed line / symbol
  -> tests that previously executed it
  -> targeted test candidates
```

Coverage shows only paths that were executed. It does not guarantee unmeasured paths or indirect impact.

Therefore:

- Do not use coverage as the only decision source
- Preserve a broader fallback for public contract / shared core changes
- Do not force adoption when collecting coverage is itself expensive

A dedicated CI SaaS or custom coverage engine is not required.

## Fallback rules

False negatives are the most dangerous failure in impact analysis.

For the following changes, do not default to completing with targeted tests alone.

### Shared / Core

- common library
- shared utility
- cross-package abstraction
- central parser / serializer
- cross-cutting infrastructure such as authentication / persistence

→ subsystem-wide or broader tests

### Public Contract / Schema

- public API
- DTO / schema
- config format
- protocol / wire format
- plugin interface

→ producer + consumer tests, and integration / compatibility tests when needed

### Build / Package / Distribution

- dependency metadata
- build scripts
- packaging config
- generated manifest

→ artifact-level validation in addition to source tests

### Unknown Dependency

- dependency relationships are unavailable
- dynamic import / reflection / code generation is significant
- test mapping confidence is low

→ subsystem/full tests or explicit `Unverified`

## When using confidence

A precise numeric score is unnecessary.

Example:

```text
high:
  direct file-to-test mapping exists

medium:
  candidates inferred from dependency relationships

low:
  dynamic behavior is significant and impact is unclear
```

Use broader validation for `low`.

## file -> test example

```text
changed:
  src/data/save.py

route:
  tests/data/test_save.py
  tests/data/test_load_roundtrip.py
```

If `src/data/schema.py` also changed, expand to broader data tests that include schema consumers.

## symbol -> test example

```text
changed:
  Parser.parse_config

route:
  symbol references
    -> ConfigLoader
    -> ProjectLoader

likely tests:
  test_parser.py
  test_config_loader.py
  test_project_loader.py
```

If reference exploration becomes too large, switch to the package test suite.

## package -> test example

```text
changed:
  packages/core/*

route:
  core unit tests
  direct downstream integration tests
```

If core changes a public API, expand to the downstream package as a whole or conformance tests.

## Validation escalation

When the first targeted validation fails, do not immediately expand to an unrelated full suite. Expand according to the failure cause.

```text
targeted failure
  -> direct dependency tests
  -> subsystem tests
  -> full suite if impact is broad / unclear
```

Conversely, even when targeted tests pass, do not skip broader validation when a fallback condition applies.

## External tool examples

For projects that already have a build graph / dependency graph, using an existing tool is preferable to building another impact analyzer.

- **Nx / `nx affected`**: calculates changed projects and dependents from Git differences and a project graph, then can run test / build / lint only for affected projects.
- **Pants / `--changed-since` + `--changed-dependents`**: can include direct / transitive dependents of Git-based changed targets when running tests and similar actions.

When these are already adopted, use their project graph / target graph as the Source of Truth and avoid implementing the same dependency analysis twice. Preserve the broader fallbacks in this document for cases such as dynamic dependencies or public contract changes where the graph alone is insufficient.

## Repository-local fallback

For repositories that do not adopt an external build-graph tool, this repository provides two lightweight fallback stages.

### file -> likely tests

- Python: `tools/python/medium/affected-tests/script/affected_tests.py`
- Go: `tools/go/medium/affected-tests/`

Supported scope:

- Git changed files / explicit changed files
- explicit source↔test mapping
- test candidates from naming conventions
- broader fallback from broad-impact patterns
- confidence / fallback reason
- direct-consumer assistance using `python-import-map` / `go-import-map` compatible JSON

### changed file -> dependent modules/packages

When a reusable structure index exists:

```text
source-structure-index affected
acr-toolbox structure-index affected
```

Supported scope:

- changed file -> containing module/package
- reverse `depends_on` traversal
- transitive dependents
- complete internal closure + bounded agent output
- broader fallback for index/truncation/mapping uncertainty

This is not a complete replacement for a high-precision project graph. Prefer Nx / Pants or similar tools when already available.

## Relationship to context reduction

The goal is not only test execution time.

- Do not send unnecessary test logs to the AI
- Keep failure candidates narrow
- Do not mix unrelated flaky tests into the current task
- Make the reason for a full-suite run explicit

On success, keep a short record of what and how many things were validated rather than the full logs.

## Signals that favor adoption

- test suite is large / slow
- monorepo / multiple packages
- source-to-test relationships are reasonably stable
- the full suite runs for every small change
- CI logs are large and consume AI context
- changed-symbol routing or dependency information already exists

## When adoption is unnecessary

- the test suite is small enough that a full run is cheap
- source-to-test relationships are simple and obvious
- impact-mapping maintenance cost exceeds the reduction benefit

A small repository does not need a dedicated impact analyzer.

## Minimal completion report

```text
Validation:
- targeted: tests/save (18 passed)
- broader: data package tests (42 passed; schema changed)
- artifact: not required
- unverified: none
```

A one-line explanation of why broader validation was added or omitted is sufficient.

## Principle

```text
correctness / false-negative avoidance
    > minimal test count
    > log reduction
```

When impact scope is uncertain, prefer the safer fallback over a higher reduction rate.
