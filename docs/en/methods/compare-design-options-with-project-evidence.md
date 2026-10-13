# Compare Proposed Design Options with Project Evidence

> Japanese Source of Truth: [提示された設計案をプロジェクトの根拠で比較する](../../jp/手法/提示された設計案をプロジェクトの根拠で比較する.md)

When you ask an AI whether design A or B is better, a generic list of pros and cons does not tell you which option fits the current project. The useful comparison is to apply **the same decision criteria to every option and support the comparison with the project's current specifications, code, configuration, and tests**.

Use this method when the requester already has a small set of candidate options. The AI investigates the evidence needed for each candidate and separates verified facts, inferences from those facts, and unresolved questions.

The AI does not need authority to make the final decision. If a person owns the decision, ask the AI for an evidence-backed recommendation.

## When to use it

Examples include:

- JSON file versus SQLite for settings storage;
- extending an existing component versus adding a new module;
- keeping a synchronous path versus introducing asynchronous processing;
- choosing between two or three libraries under project constraints;
- checking which of several human-proposed approaches best fits the current architecture.

If only one option exists and the constraints are obvious, a comparison table may add unnecessary work. If you do not have candidate options yet, first clarify the goal and constraints and generate candidates separately.

## 1. Provide candidates and non-negotiable conditions first

Give the AI:

- the candidate options;
- the goal;
- mandatory conditions;
- what may change;
- whether new candidates may be introduced;
- whether the AI recommends or makes the final decision.

Example:

```text
Compare these settings-storage options.

Candidates:
A) Keep the current JSON file
B) Move to SQLite
C) Store settings on a server

Goal:
Keep settings maintainable as the number of fields grows.

Mandatory conditions:
- Settings must remain readable without network access.
- Account creation must not become mandatory.
- Existing users must not lose their saved settings.

Do not add new candidates.
Investigate the project specifications, code, configuration, and tests needed for the comparison.
Recommend an option, but I will make the final decision.
```

If candidate expansion is not specified, an AI may keep adding alternatives and dilute the requested comparison. When none of the proposed candidates can satisfy the constraints, have the AI report that fact instead of silently replacing the option set.

## 2. Derive decision criteria from this task

Build criteria from the goal and mandatory conditions rather than from a generic architecture checklist.

For the example above:

| Criterion | What to verify |
| --- | --- |
| Offline use | Can reads and writes work without a network? |
| Existing-data compatibility | What is the current format and what migration would be needed? |
| Fit with current implementation | Can existing persistence code be reused? |
| Dependencies | Does an option require a new library, runtime, or service? |
| Test impact | Which existing tests change and what new checks are needed? |
| Maintenance burden | What new code, migration logic, and operations are introduced? |

Do not use vague criteria such as "modern," "popular," or "fast" without connecting them to a project requirement.

If performance matters, identify the actual target and measurement method. Do not invent numerical scores for unmeasured performance.

## 3. Investigate original project evidence for every option

Depending on the decision, inspect:

- current specifications;
- design documents and decision records;
- relevant implementation;
- configuration;
- callers;
- related tests;
- dependency manifests;
- measured runtime results when needed.

Do not compare option A from project source while describing option B only from general knowledge. For criteria that apply to all candidates, use comparable project evidence where possible.

Ask the AI to return the file and section or symbol used for each important claim.

```text
For each criterion, list the specification, code, configuration, and tests you inspected,
including file names and the relevant section or symbol.
Do not make the decision from search-result snippets alone; inspect the original locations used as evidence.
```

[Evidence Budget](../evidence-budget.md) can help define the evidence needed before investigation expands.

## 4. Separate fact, inference, and unknown

### Verified fact

A statement directly supported by a specification, implementation, test, configuration, or measured result.

```text
Fact: docs/settings.md requires settings to be readable without network access.
Fact: src/settings/store.py currently reads and writes a JSON file.
Fact: requirements.txt contains no added SQLite package.
```

### Inference from evidence

A conclusion based on verified facts.

```text
Inference: A server-only option cannot satisfy the offline-read requirement.
Inference: Reusing the current JSON storage likely requires less migration work than replacing it with SQLite.
```

Keep inferences visibly separate and state their conditions.

### Unknown

Something the available evidence does not establish.

```text
Unknown: How many settings fields are expected in two years.
Unknown: Startup performance after an SQLite migration has not been measured.
```

If an unknown could change the recommendation, the AI should request another source, measurement, or answer from the user.

## 5. Compare every option using the same rows

A useful comparison table uses the same criteria for each candidate.

| Criterion | A: JSON | B: SQLite | C: Server |
| --- | --- | --- | --- |
| Offline use | Supported by current implementation | Possible with a local database | Server-only storage fails the mandatory condition |
| Existing data | Current format continues | JSON migration is required | Local settings need a transfer format |
| Current implementation | Existing read/write path can be reused | Persistence layer changes | Networking and authentication are new responsibilities |
| Dependencies | No new dependency | SQLite implementation must be confirmed | Service and authentication dependencies are needed |
| Unknowns | Maintainability at much larger scale | Performance with real data | Operational requirements for the service |

For important cells, retain a pointer to the project source that supports the statement.

If you use scores, state who defined the scale and weights. Do not generate arbitrary values such as "A=90, B=75" simply to make the comparison look precise.

## 6. Handle failed mandatory conditions before tradeoffs

An option that violates a mandatory condition is different from an option that merely has a disadvantage.

If offline operation is mandatory, a server-only design should be reported explicitly:

```text
Option C fails the mandatory requirement to read settings without network access.
Unless that requirement changes, exclude C from the recommendation set.
```

When every proposed candidate fails a mandatory condition, do not force a recommendation:

```text
None of A-C satisfies mandatory condition X.
If I may introduce an additional candidate, I can investigate alternatives that meet X.
```

## 7. State what would change the recommendation

A recommendation is easier to review when it includes its boundary conditions.

```text
Recommendation: A

Reasons:
- It satisfies the offline requirement with the current implementation.
- Existing user data needs no migration.
- It adds no external dependency.

Weakness:
- Maintainability with a much larger settings schema is not yet verified.

The recommendation may change if:
- multiple processes must update settings concurrently;
- future requirements need queries or updates that the current JSON format cannot support.
```

This shows the user where the conclusion remains valid.

## Example request to the AI

```text
Recommend the option that best fits the current project.

Candidates:
A) ...
B) ...
C) ...

Goal:
...

Mandatory conditions:
...

Allowed change scope:
...

Do not add candidates.
I will make the final decision.

First derive the comparison criteria from the goal and mandatory conditions.
Then inspect the specifications, design documents, code, configuration, and tests needed for those criteria,
and cite the project files and locations used for important judgments.

Compare every candidate using the same criteria.
Separate verified facts, inferences, and unknowns.
Do not invent scores or weights.

If an unknown could change the recommendation, list the source, measurement, or question needed to resolve it.
Identify candidates that fail mandatory conditions.
If all candidates fail, do not force a winner.

Finally report the recommendation, evidence, weaknesses, conditions that would change the recommendation, and anything not verified.
```

## How a person reviews the recommendation

Check at least these points:

1. The original candidate set was not silently changed.
2. Mandatory conditions appear in the comparison.
3. All candidates use the same criteria.
4. Important claims have project evidence.
5. Facts and inferences are not mixed.
6. Unmeasured performance or effort has not been assigned invented numbers.
7. Unknowns that could change the conclusion are visible.
8. A candidate that fails a mandatory condition is not rescued by a vague overall score.

After a human accepts a recommendation, use [Give the AI decision reasons](share-decision-reasons.md) when the rationale should be reusable in future work. This guide is about **comparison before a decision**; that guide is about **recording and reusing a decision after it has been made**.

## Why this can reduce context, and its limit

Providing the candidates, goal, and mandatory conditions first prevents the AI from exploring every imaginable architecture. Once criteria are known, investigation can focus on the specifications, code, configuration, and tests that answer those criteria.

Returning the recommendation together with evidence can also reduce repeated follow-up questions such as "why A?" and "what is wrong with B?"

Reducing reading is not proof that the recommendation is correct. If a necessary criterion was omitted, a small context can still produce a bad recommendation. Expand the investigation when an important unknown requires more source evidence or measurement.

## Relationship to existing methods

A **trade study** also compares alternatives against goals, requirements, effectiveness, cost, and selection criteria. NASA's Systems Engineering Handbook describes documenting alternatives, data sources, measures, uncertainty, and the recommended alternative.

For larger software-architecture evaluations, the Software Engineering Institute's **Architecture Tradeoff Analysis Method (ATAM)** examines risks and tradeoffs among quality attributes such as modifiability, security, performance, and availability. You do not need the full ATAM process for an everyday comparison between two or three options; this guide reuses the simpler idea of explicit quality conditions and comparable risks.

After a decision, an **Architectural Decision Record (ADR)** records the decision, its context, and consequences. ADRs preserve decisions; they are not themselves the investigation-and-comparison procedure in this guide.

- [NASA Systems Engineering Handbook: Decision Analysis / Trade Study](https://www.nasa.gov/reference/system-engineering-handbook-appendix/)
- [Software Engineering Institute: The Architecture Tradeoff Analysis Method](https://www.sei.cmu.edu/library/the-architecture-tradeoff-analysis-method/)
- [AWS Prescriptive Guidance: Architectural decision record process](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)
