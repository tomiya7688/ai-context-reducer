# Reference Catalog (Context Manifest)

> Japanese source of truth: [参照先の目録](../jp/参照先の目録（Context%20Manifest）.md)

A reference catalog is a **list of where to find commonly used documentation, code, and tests, and what each location is for**. It does not copy or summarize their contents. It makes it easier to find what exists and where to look.

For example, when asked to fix CSV date conversion, a developer could search the entire repository for `csv` or `date` and compare every result. A catalog can point to the format guide, import code, and related tests instead. The developer opens only the original sources relevant to this task, reducing the amount of unrelated code and outdated material read first.

## Example: Investigating CSV date conversion

A catalog might record:

| Location | Role | Use it to check |
| --- | --- | --- |
| `docs/csv-format.md` | CSV format guide | Date-column format and compatibility |
| `src/csv/importer.py` | Import implementation | Where strings are converted to dates |
| `tests/csv/test_importer.py` | Import tests | Existing inputs and expected results |

For a report that “CSV dates are shifted,” these three locations are likely starting points. The catalog does not decide the cause. Check the supported format in the guide, the conversion in the code, and current expectations in the tests. There is no need to open unrelated screens or documents for other formats first.

## What to record

The location and its purpose are enough. Do not put file contents or detailed requirements for a particular task in the catalog.

```text
Location                 Role             Use
docs/csv-format.md       Format guide     Column format and compatibility
src/csv/importer.py      Import code      Convert strings to values
tests/csv/               Related tests    Inputs and expected results
```

You can create a short list by hand or build it from the existing directory structure or a search tool. The goal is not to account for every file; it is to make recurring references easy to find. If the list becomes hard to scan, split it by feature or show only entries related to the current task.

## How to use it

1. Confirm the goal of the task.
2. Pick likely documentation, code, and test locations from the catalog.
3. Open those original sources and check what this task needs.
4. Skip candidates that do not apply. If the catalog is missing a useful location, find it through a normal search and update the catalog when appropriate.

An entry in the catalog does not mean you must read it every time. If a bug fix does not change the supported format, the relevant format guidance may already be clear. If the catalog lacks a source needed for the task, search normally and add the new reference.

## How it differs from other documents

| Document | Role |
| --- | --- |
| README / AI guide | Introduces the project and shows where to start |
| Current State | Describes available capabilities and known constraints |
| Reference catalog | Shows where recurring documentation, code, and tests live |
| [Working note](context-pack.md) | Records the sources selected and completion criteria for this task |
| Original source | Holds the specification, implementation, test, or other evidence |

The catalog lists candidate locations; the working note selects what this task will actually use. To confirm a specification or actual behavior, read the linked original source, not the catalog description. If a catalog entry disagrees with its source, follow the source.

## When a catalog helps—and when it does not

A catalog helps when the same feature is investigated repeatedly, people keep searching for the same starting points, or its code, specification, and tests are spread across the repository. Gathering these locations once saves repeated discovery work.

For a one-off change with named files, or a task with only a few obvious candidates, creating a catalog takes more effort than writing the references in the request. Create one when the repeated search it avoids costs more than creating and maintaining the list.

## Keep it current

Update a location and its description when files move or their roles change. An obsolete entry can send someone looking for a file that no longer exists. Keep the list small enough that a person or process can maintain it.

This repository also has an optional helper tool for building catalogs. Its output and ranking are leads for finding candidates; the task itself determines which sources are relevant.

## Example request to the AI

For a one-time task, attach this guide or name its path in the request. For recurring work, link it from project instructions the AI actually reads and check whether automatic loading is configured.

> Select only the specification, code, and test locations relevant to this change from the catalog. First give the paths and reasons, then open and check those original sources. At the end, report the files consulted and tests run.

## Optional tools and terminology

Use [context-manifest](../../tools/common/large/context-manifest/README.md) to build a catalog if useful; a manual list works too. This method is called a **Context Manifest** or reference catalog.
