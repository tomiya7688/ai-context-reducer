# Responsibility Map

> Japanese Source of Truth: [ファイルとモジュールの役割表](../jp/ファイルとモジュールの役割表.md)

If you repeatedly ask which folder to inspect for a bug, briefly record the main locations and responsibilities by kind of work. For example, “investigate broken documentation links” should lead to the implementation that checks links and the tests that check its behavior.

You do not need an inventory of every file. Start with recurring work and record representative locations verified in actual code and tests. The map is an investigation entry point; establish current behavior and change correctness from original code and tests.

## When to use it and how to decide

| Current situation | Approach |
| --- | --- |
| You rediscover implementation and test locations whenever changing the same feature | Start with a row for that feature |
| Folder names do not establish responsibilities | Inspect behavior and users, then describe the responsibility in one sentence |
| Existing design or task guidance already identifies the same responsibilities and checks | Use it and supplement only missing locations |
| A few files make responsibilities and tests apparent | A few lines in existing guidance are enough; do not add a separate table |

Do not add rows solely because files are large or change frequently. The criterion is **whether someone starting this kind of work can reach the first implementation and checking locations**.

## Steps to build it from actual code

### 1. Choose one kind of recurring work

From recent requests or Issues, choose one behavior to investigate, such as “settings do not persist after saving” or “repair broken documentation links.” Labels like “other” or “common processing” do not identify a starting point; begin with the words users use to request work.

You do not need to classify the whole project first. Create rows needed for this work, adding others when another task needs guidance.

### 2. Find existing guidance and the processing entry point

Search the README, existing responsibility maps, and design documents for the same guidance. If there are no candidates, search code using the error message, screen label, operation name, or execution command.

Folder names help locate candidates. Do not assign responsibility from names alone: inspect who calls the processing, what values or files it receives, and what it returns or saves.

### 3. Establish responsibilities from implementation and tests

When delegating investigation to AI, have it check the following in code.

1. Open candidate function or class definitions and their users.
2. Identify which processing determines the target behavior, citing concrete conditions and inputs or outputs.
3. Open related tests and identify their inputs and expected results.
4. If processing delegates to another component, follow that definition and related tests.

Reading tests identifies expected behavior. Whether those tests currently pass requires execution results. If no test is found, record “checking test not identified” instead of inventing a path. When responsibility remains uncertain, separate established facts from gaps and do not list it as confirmed.

### 4. Example: investigate this repository’s documentation checks

This example comes from reading code as of October 18, 2026. Choose the task “repair broken documentation links or missing Japanese/English mappings” and inspect the following. These are not instructions to create identically named files in your project.

- In [the checking implementation](../../.github/scripts/validate_documentation.py), `load_mapping` reads `docs/DOCUMENT_MAP.json` and checks language and registration data. `validate` compares registered Japanese/English documents with actual files.
- In the same implementation, `validate_relative_links` reads relative links in documents and checks properties including destination existence.
- In [the related tests](../../.github/scripts/test_validate_documentation.py), `test_missing_english_file_is_detected` removes an English document and checks for an error; `test_broken_relative_link_is_detected` checks detection of a nonexistent destination.
- [The configuration for running checks on GitHub](../../.github/workflows/validate-documentation.yml) invokes those tests and documentation checks.

These findings can produce the following map.

| Kind of work | Main location | Responsibility and checking location |
| --- | --- | --- |
| Check Japanese/English document mappings | `.github/scripts/validate_documentation.py` | `load_mapping` and `validate` compare registration data and document existence. Check with `.github/scripts/test_validate_documentation.py` |
| Check relative documentation links | `.github/scripts/validate_documentation.py` | `validate_relative_links` inspects destinations. Check with the broken-link test in the same test file |
| Invoke checks on GitHub | `.github/workflows/validate-documentation.yml` | Defines how to run the tests and document checks. Establish execution success from the corresponding run results |

The evidence is the read destination, checking logic, test expectations, and execution configuration—not the folder name `.github/`. One file may support multiple kinds of work. Do not copy every function into the map.

### 5. Consolidate existing guidance and reference it from instructions the AI reads

Add verified rows to an existing map when available. An example new location is `docs/file-responsibilities.md`. Record the inspection date or commit, an identifier for a code revision, near the table to support later comparison. Recording a revision alone does not guarantee the map remains current.

For recurring use, put a short condition and map path in project instructions your AI reads. If the environment reads `AGENTS.md`, preserve existing rules and add something like:

```text
When locating implementation or tests, select the rows related to this work
from docs/file-responsibilities.md.
Read candidate implementation and related tests to check that the map matches current code.
If you find an unlisted relationship, expand investigation to the necessary processing.
```

Saving or linking a file does not ensure automatic AI reading. Check instruction-loading settings or name the map in the request. For a chat that cannot open files, attach or paste relevant rows and necessary code and tests.

## Example requests to the AI

When first asking for a map, supply investigation scope and completion criteria.

```text
The task category is “repair broken documentation links.”
First check whether the existing README, design documents, or responsibility map already provides this guidance.
Read implementation definitions and users, and related tests.
Establish responsibilities using inputs, outputs, conditions, and test expectations.

Create a short table of work categories, main locations, responsibilities, and related tests.
Choose representative starting locations instead of listing every file or function.
State the inspected revision and evidence. Do not assert uncertain responsibilities or invent missing tests.
Consolidate existing guidance where available; otherwise propose docs/file-responsibilities.md.
For this request, do not modify code or execute tests; return the proposal and unverified points.
```

Completion means the user can open implementation and checking locations from the table and explain each responsibility using processing behavior and test expectations. Do not mark unsupported rows as confirmed.

To use an existing map:

```text
Investigate why saved settings disappear after restarting.
Read docs/file-responsibilities.md and select candidates for saving, startup loading, and related tests.
Open those implementations and tests and check that they match the map.
Expand investigation where another component is involved.
First report candidates, evidence, discrepancies, and unverified points.
```

## When the map conflicts with actual code

Do not change code to fit an old map. Have the AI inspect current definitions, users, and related tests. If behavioral requirements also disagree, check current specifications or Issues for the intended behavior. The map alone cannot determine whether code or specifications are wrong.

Once the map is established as outdated, update its location or responsibility descriptions. If cause or ownership remains uncertain, retain that uncertainty and do not stop investigation at that row. Update the map in the same change when responsibilities are added, moved, or split.

For choosing inspection sources by change type, see the [Change Routing Map](change-routing-map.md). To locate definitions and callers within large source files, see the [Source Structure Index](source-structure-index.md).

## Why this can reduce reading

Recording entry points for recurring work can avoid repeatedly opening folders and inferring responsibilities. Having the AI follow relevant rows to code and tests can also limit unrelated feature code supplied as input.

Initial investigation and maintenance still cost effort. Supply additional sources when dependencies appear instead of omitting necessary information. A shorter table alone does not establish lower usage; compare actual read records or measured input usage when available.

## Supporting tools

- [responsibility-candidates](../../tools/common/medium/responsibility-candidates/README.md): Produces a table of code paths and sizes with responsibility fields left unfinished. It can help find missing candidates, but does not establish work categories or ownership; select useful rows and verify them in code and tests.

## About this method

A list that records main locations and responsibilities by kind of work and directs readers to relevant implementations and tests is called a **Responsibility Map**.
