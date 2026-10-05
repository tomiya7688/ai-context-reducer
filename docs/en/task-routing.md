# Task Routing Guide

> Japanese Source of Truth: [作業別の案内表](../jp/作業別の案内表.md)

A task routing guide connects types of work to the documentation, code, and tests to inspect first. It reduces the amount of unrelated material read by avoiding the repeated search for starting points on recurring tasks.

## Example: fix an error message for CSV import

Suppose you repeatedly search for the format description, import code, and related tests each time you fix a CSV import error message. Record the starting points in a table so the next task can begin there.

```text
| Task type | Documentation | Code | Check |
|---|---|---|---|
| CSV import | docs/csv-format.md | src/csv/importer.py | tests/csv/test_importer.py |
```

The listed locations do not have to be the whole investigation. If the change also affects another feature, inspect its callers, additional tests, or design documents. The table marks where to start; it does not set a fixed boundary for the investigation.

## What to include and how to update it

Choose recurring kinds of work and record for each:

- the explanation or specification to read first
- candidate code or modules to change
- the tests or execution steps to use after the change

You do not need to categorize every small task or list every document in the project. When the target code and tests are obvious, reading those locations directly is enough.

When code or tests move, update the guide in the same change. If a row is out of date or no row fits the task, expand the investigation with search and the original materials. Current code and tests take precedence over an old guide.

## When it helps

This guide fits projects with several features or documents where recurring task types lead to different starting points. In a small project with only a few kinds of work and obvious source and tests, a short note in an existing guide is enough; a separate table may not be useful.
