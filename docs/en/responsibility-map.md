# Responsibility Map

> Japanese Source of Truth: [ファイルとモジュールの役割表](../jp/ファイルとモジュールの役割表.md)

A responsibility map briefly states what major files or modules do. In a project where filenames do not make their roles clear, it narrows candidate files before you open source files one by one.

## Example: fix how CSV dates are displayed

Suppose you need to fix the display of dates read from a CSV. If a responsibility map says “CSV reader splits rows and extracts values” and “date conversion normalizes display formats,” you can start with the date conversion code and its tests. This saves the work of opening every unrelated file, such as the CSV reader or screens, to guess what each one owns.

```text
| Location | Responsibility |
|---|---|
| src/import/csv_reader.py | Reads CSV rows and extracts column values |
| src/date/normalize.py | Converts date values to the display format |
| tests/date/test_normalize.py | Checks date-conversion behavior |
```

## How to make the map

Choose major files or modules that change often and describe each responsibility in one sentence. Do not list every small function or reproduce implementation details; use the map as an entry point to the code. If a role is unclear, check the implementation or existing design documents instead of guessing from the name.

A responsibility map is not a detailed specification. Once you find candidates related to the current task, read the original source and tests. For selecting inspection locations by change type, see the [Change Routing Map](change-routing-map.md). For inspecting functions and dependencies in large source files, consider the [Source Structure Index](source-structure-index.md).

## Updates and when to use it

When a change adds, moves, splits, or combines a major responsibility, update the map in the same change. A stale map points to the wrong files; if it cannot be maintained, do not rely on it to identify current ownership and check the source instead.

In a small project where a few files and tests make their roles clear, a dedicated map is unnecessary; a short entry in an existing AI guide or design document is enough. Do not add a map when keeping it up to date would take more time than it saves in repeated investigation.

## Example request to the AI

Attach the map to the task or link it from instructions the AI actually reads. For a one-off request, say:

> Select the files and tests related to this change from the responsibility map. Check that the map matches the implementation, give the candidate paths and evidence, and inspect original sources only where ownership is unclear.

## Optional tools and terminology

Use [responsibility-candidates](../../tools/common/medium/responsibility-candidates/README.md) to draft a path list if useful, but verify responsibilities in original sources. This list is called a **Responsibility Map**.
