# Check Changes from the Shared Repository First

> Japanese Source of Truth: [リモートとの差分を先に確認する](../jp/リモートとの差分を先に確認する.md)

When several people or AIs update the same repository, the shared code may change after you create your local copy. Check only the changes since your last review before starting work. This can reveal updates that affect your task without rereading every file that has not changed.

## Example: someone else changed the shared repository

Suppose you are about to change CSV loading while someone else updates date conversion and its tests. Checking the changes from the shared repository first shows the changed filenames and a summary, which reveals that date conversion may be relevant. Read those implementation and test changes to understand their effect on your work. You do not need to reread unchanged screens or unrelated features.

```text
compare the shared repository with the last reviewed state
  -> inspect the list and summary of changed files
  -> read changes related to the current task
  -> open related source files if the effect is unclear
```

## What to inspect first

After retrieving new changes from the shared repository, start with a summary. It can include short descriptions of updates, changed filenames, the amount of change, and short excerpts when needed. A diff is a view of lines added or removed between versions.

If the summary makes the effect clear, read the related changes and their direct dependencies. If the reason or result is unclear, expand the investigation to the full target file, design documents, or tests. Do not make a final decision from a short summary alone.

If a diff excerpt is shortened, state which parts were omitted and keep a way to inspect the original diff. A short display is a starting point for locating changes, not a complete review.

## Keep inspection separate from applying changes

Inspecting changes in the shared repository and applying them to your local copy are separate actions. To review a diff, use a method that does not overwrite work in progress. If an automated update finds unsaved local changes or a mismatch with the shared repository, stop and return the decision to a person.

## When to use this method

This helps when several people or AIs update a shared repository and changes may arrive since the last review. There is no need to add a diff mechanism for a short solo task when you know the shared repository has not changed. If a change summary does not reveal the effect, inspect the related files and required checks.

## Example request to the AI

> First inspect files changed on the shared remote since the known base, and show only diffs relevant to this task with reasons. Keep reviewing separate from applying changes; ask me before applying anything. At the end, report the diffs reviewed and anything not verified.

## Optional tools and terminology

Optional [remote-delta](../../tools/common/medium/remote-delta/README.md) summarizes changes. This method is called **Remote Delta** or delta-first review.
