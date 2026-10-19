# Write a short note for the current task
> Japanese version: [今回の作業に必要なことを短くまとめる](../../jp/手法/今回の作業に必要なことを短くまとめる.md)


When work takes several days or must be handed to another person or AI, write a short note with what to change, where to look, and how to know it is done. For example, for a date error in a table file, point to the date-reading code and related test, and say to confirm that the correct date appears after the fix.

This note guides the current task. It is not a place to copy full specifications or decisions.

## What to include

```text
Work to do:
  Fix the bug that shows dates one day early in a table file

Where to start:
  Date-reading code, related test, date rules

What to preserve:
  Do not change other dates or saved data behavior

How to know it is done:
  The same input shows the correct date and the related test passes

Not part of this task:
  Rewriting table-file handling as a whole

Detailed information:
  Links to the date specification and work request
```

Add only material that the task needs. There is no need to paste long specifications, full source files, or logs. Link to the issue or work request for task conditions, the design document for agreed requirements, and source code or tests for current behavior.

## Keep detailed information in its own place

| Information | Where it belongs |
| --- | --- |
| Current goal, starting points, constraints, and completion check | Current task note |
| Long-lived requirements and decisions | Guide or design document |
| Work requests and unfinished items | Work request or task list |
| Actual behavior | Program and tests |

The reference depends on the information: use the issue or work request for what was asked and its completion conditions, the design document for agreed requirements, and source code and tests for current behavior. There is no single document that is the source for every kind of information.

If the note disagrees with a linked document, do not assume which one is outdated. Compare the request, design document, code, and tests. If the intended behavior is still unclear, ask before changing it.

## Clean up when the task is done

Do not carry task-specific information into the next task unchanged. Record decisions and unfinished work that still matter in the relevant guide or work tracker, and link to them from the note. If the note gets long, keep only what is needed for the current task.

## Use only the sections you need

Not every task needs every section. For a small change, the goal and check may be enough. For work spanning several days or being handed over, constraints and out-of-scope items can prevent misunderstandings.

## Tell the AI what to do

For work spanning several days, copy the [task note template](../../../templates/CONTEXT_PACK.md) to the repository root as `CONTEXT_PACK.md` and fill in the needed sections. In the next request, say “Read `CONTEXT_PACK.md` first” and give its path. If the AI uses a separate working directory, put the file there and provide that path. For a short, one-time task, put the conditions directly in the request instead of creating another file.

```text
Read the task note first. Confirm the goal, starting points, and completion check before working.
Check the issue or work request for what was asked, the linked design document for agreed requirements, and source code and tests for current behavior.
Do not guess conditions that are missing from the note. Ask about anything unclear.
```

## Why this reduces context

Give the AI one short note with the current goal and starting files so it does not have to search the conversation or older task history. Keep task conditions in the issue or request, agreed requirements in the design document, and actual behavior in the code and tests. Have the AI open only the relevant source when needed.

## Terms

- **Task note**: A short guide to the current goal, where to look, constraints, and how to check the work.
- **Context Pack**: A name for giving the AI a task note together with the information and checks needed for that task.
