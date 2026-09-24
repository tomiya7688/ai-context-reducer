# Validation Routing

> Japanese Source of Truth: [変更内容に応じて検証を選ぶ](../jp/変更内容に応じて検証を選ぶ.md)

Validation Routing selects only the validation methods required by the change.

The key is to make the required evidence explicit for each kind of change and begin with the smallest sufficient validation.

## Purpose

Do not run the same large validation set for every change, and do not assume unit tests are always enough. Select evidence that matches the nature of the change.

```text
Change type
  -> required evidence
  -> smallest sufficient validation
  -> evidence validity check
  -> additional evidence only if needed
```

## Evidence types

Representative forms of validation include:

- static / syntax checks
- targeted unit / regression tests
- deterministic runtime / smoke tests
- structured evaluation logs
- generated-data consistency checks
- distribution / packaged-artifact smoke tests
- visual / interactive confirmation
- performance measurement

Not every task needs all of them.

Syntax / parser health can be cheap evidence before a full build/test when an existing parser is available. Syntax success does not prove semantic correctness or task completion, so follow it with the targeted tests / compiler / runtime validation required by the change. Do not auto-install a parser only for this purpose. See [Syntax Health Validation](syntax-health-validation.md).

## Route by change type

Examples:

```text
Pure logic change
  -> targeted tests

Probabilistic / time-dependent behavior
  -> fixed seed / bounded runtime + structured log

UI / drawing / layout
  -> automated smoke + visual confirmation

Data contract change
  -> schema / parser tests + representative data validation

Distribution / package change
  -> build artifact + launch / required-files / initialization smoke

Performance change
  -> correctness tests + comparable measurement conditions
```

Do not infer properties that the test result cannot actually verify.

## Change Impact / Test Impact Routing

After selecting the evidence type, a repository with a large test suite can narrow execution from changed files / symbols / packages.

```text
changed files / symbols
        ↓
responsibility / dependency / ownership information
        ↓
likely affected tests
        ↓
smallest sufficient validation
        ↓
shared/public/unknown impact -> broader fallback
```

Useful inputs include:

- source ↔ test naming relationships
- explicit mapping tables
- Responsibility / Change Routing Maps
- import / dependency relationships
- changed-symbol routing
- existing coverage data as a supporting signal

A dedicated coverage SaaS or giant dependency graph is not required.

Always keep a conservative fallback:

- shared/core change -> subsystem-wide / broader tests
- public API / schema / config contract change -> producer + consumer / compatibility tests
- build/package change -> artifact-level validation
- unknown dependency relationship -> subsystem/full tests or `Unverified`
- low confidence in impact selection -> broader validation

See [Change / Test Impact Routing](change-impact-routing.md) for details.

## Evidence validity

An exit code of 0 is not sufficient evidence if the command did not actually inspect the target.

Examples:

- do not treat `0 tests` as successful feature validation
- do not use a checker that only scanned out-of-scope paths as success evidence
- do not infer that required files exist in a distribution merely because the build succeeded
- confirm that a smoke test actually reaches the target feature

When practical, keep a short count or target summary in the Context Pack. Full logs are unnecessary.

## Headless first

Even for a GUI / interactive application, first validate logic, storage formats, CLIs, and generated artifacts without launching the GUI when possible.

```text
headless checks
  -> finish if sufficient
  -> GUI confirmation only when visual / interactive acceptance exists
```

GUI launches can produce large execution logs, images, and manual interaction, so restrict them to changes that need them.

When UI / visual correctness itself is part of Acceptance, do not declare completion from headless checks alone.

## Disposable validation workspace

For save / conversion / export / initialization validation that creates files, use a temporary directory or disposable workspace when possible.

This:

- avoids leaving validation files in the working tree
- keeps generated files out of normal diffs
- makes the same initial state easier to reproduce
- prevents the AI from misreading unrelated generated artifacts as changed files

Move validation artifacts to a persistent location only when they must be retained.

## Generated / distribution artifact boundary

When the final artifact differs from the source tree, source validation alone may not be enough.

```text
source validation
  -> artifact generation
  -> artifact smoke
```

For a distribution build, direct artifact checks may include:

- it launches
- required files exist
- initialization / UserData can be created correctly
- it does not depend on development-machine absolute paths or unbundled dependencies

This provides direct evidence at the artifact boundary instead of making the AI infer packaging correctness from implementation details.

Generated artifacts are normally candidates for context exclusion, but when an artifact itself is Acceptance evidence it returns temporarily as a validation target. Do not exclude the Source of Truth, and do not keep the full artifact in normal context after validation. See [Context Exclusion](context-exclusion.md).

## Structured observation before broad code reading

For runtime behavior investigation, record coordinates, state, events, decisions, or similar signals as bounded structured logs when possible.

Inspect reproduction conditions and necessary observations instead of beginning with huge normal logs or all source code.

Do not keep full success logs in the Context Pack. Add only relevant ranges on failure.

## Deterministic reproduction

When behavior depends on randomness or time, fix as many of the following as practical:

- seed
- input
- timestep / frame count
- configuration
- target scenario

This reduces the need for the AI to compare large execution histories.

## Visual truth

Passing unit tests does not prove that screen placement, drawing, images, or animation are visually correct.

When visual correctness is part of Acceptance, make visual confirmation an explicit Completion Gate.

Do not add screenshots or manual visual checks to every change when visual behavior is irrelevant.

## Shared Source of Truth

When multiple entry points, such as an editor and runtime, operate on the same data, avoid opaque intermediate copies and reference one formal shared data contract when possible.

This reduces extra exploration to determine which representation is current.

## Standard recommendations

- route required validation evidence from the change type
- narrow large test suites with change/test impact routing
- use a broader fallback when impact is shared / public / unknown
- start with the smallest sufficient validation
- use syntax health as cheap evidence when available, but never as completion evidence by itself
- limit GUI / interactive validation to changes that need it and prefer headless checks first
- prefer disposable workspaces for validation that creates files
- confirm that evidence actually inspected the target
- do not treat `0 tests` or empty checks as success
- smoke-test generated artifacts directly when source and final artifact differ
- prefer fixed conditions + structured observation for random behavior
- do not retain full success logs
- visually confirm only changes where visual correctness matters
- do not guess properties that unit tests cannot verify
- do not create multiple Sources of Truth when multiple entry points share data
