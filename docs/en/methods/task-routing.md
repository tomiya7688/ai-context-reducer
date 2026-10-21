# Tell the AI where to start for each kind of work

> Japanese source: [作業の種類ごとに、AIに最初に読む場所を伝える](../../jp/手法/作業の種類ごとに、AIに最初に読む場所を伝える.md)

For example, when you ask the AI to fix a date error in a table file, direct it to the date-handling code, its tests, and the date rules. For a screen change, tell it which screen code and checks to start with. Recording these starting points saves you from directing the AI to search the whole project each time.

## Give each kind of work a guide

For each kind of work, list the places you want the AI to check first. When making a request, give it the matching row.

| Work | Where to tell the AI to start |
| --- | --- |
| Fix a date error in a table file | Date rules, date-handling code, date tests |
| Change a settings screen | Screen code, settings storage, screen tests |
| Change a communication format | Format description, sending and receiving code, related tests |

Use actual file names or links in a project guide. If the right locations are not known yet, look for the related code and tests before writing the guide. Do not guess from the task name alone.

For a guide used across tasks, save it as `docs/task-start-points.md`, for example, and link it from the root `AGENTS.md`. In each request, ask the AI to use only the matching row. If a change-check map already contains these starting points, add to that map instead of creating a duplicate. For one-time work, put the starting files in the request itself.

## Give the AI a short description of the work

When you give the AI a long work request, include a short starting note with:

- what to change
- what must stay as it is
- which documents or files to check first
- what must be confirmed before the work is complete
- where to find the original request or full specification

If the short description does not answer a question, tell the AI to check the original request or specification. The short description does not replace the original.

## Choose the next task from a list

When many tasks are open, you do not have to ask the AI to read every task and choose one. If the project has an agreed priority order, use it to decide which task to give the AI first.

```text
highest priority → next priority → lower priority
```

Follow the names and order used by the project. If no order exists, ask a person to decide instead of having the AI invent one.

To request one task per “next” signal, use [Advance one listed task per signal](run-one-task-per-signal.md) to define the list, priorities, scope, and stop conditions. This starting-point guide helps after the task has been chosen.

## Get the latest changes before starting

When another person or AI may have updated the shared project, get the latest changes yourself or ask the AI to get them before starting. Check the changed file names and a short summary, then direct the AI to read only changes that affect your task. You do not need to reread unrelated changes.

```text
get the latest shared changes
  → check changed file names and summary
  → read changes related to this task
  → start work
```

Getting changes and bringing them into your working copy are separate actions. If your work has unsaved changes, the same file was edited in both places, or bringing changes in could overwrite work, stop and inspect the situation first. See [Get shared changes before starting work](remote-context.md) for details.

## Check the result before handing the work over

Before handing the work over, run checks that match the change yourself, or tell the AI exactly which checks to run. For example, open the screen when needed after a screen change, and inspect the packaged file after changing something that affects a release.

Briefly report which checks ran and their results. Do not report something as successful if it was not checked or if no tests ran. When a check fails, keep only the part of the output needed to understand the failure.

## Example instruction for the AI

```text
Fix the one-day date error in the table data.
Start with the date rules, date-handling code, and related tests.
Check the callers only if the code and tests disagree or the effect on another operation is unclear.
Confirm that the same input now displays the correct date.
```

## Start with the simplest approach

Begin with a hand-written guide for recurring work. Add automatic task selection or automatic summaries only after the repeated effort is greater than the effort of maintaining those features.

## Why this reduces context

Give the AI the row for the kind of work so it starts from relevant locations instead of searching the whole project. Keep detailed sources linked rather than copying their contents into the guide.

## Terms

- **Original request**: The full work request or specification that a short description summarizes.
- **Task Routing**: Linking each kind of work to the explanation, code, and tests to check first.

## Optional helper tool

- [change-router](../../../tools/common/medium/change-router/README.md) suggests the tests and documents to check first from changed files. Verify its candidates against your guide table and original sources.
