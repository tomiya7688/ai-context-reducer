# Get shared changes before starting work
> Japanese version: [作業前に共有先で変わったファイルを確認する](../../jp/手法/作業前に共有先で変わったファイルを確認する.md)


Several people or AIs may update the same project in a shared place such as GitHub. The files on your computer may not contain the latest changes there.

> **Before starting work, get information about the latest shared changes and check which files changed. Read the relevant changes before editing.**

Checking and applying changes are separate actions. Checking alone does not rewrite your local files. After reviewing the changes, apply only the updates you decide are needed.

## Example: someone else changed the date handling

Suppose you are about to fix a CSV date-reading bug while someone else changes the date handling or its tests. Before editing, get the latest change information and check whether those files changed. If they did, read those changes before fixing the bug. You do not need to read unrelated screen changes.

## If you use Git

### 1. Check the shared changes

First check whether you have local work in progress.

```sh
git status --short
```

If nothing is listed, you have no unrecorded local changes. If anything is listed, keep those changes; do not delete or overwrite them. You can still check the shared changes while preserving your work.

Next, get the latest information from the shared repository.

```sh
git fetch
```

This gets information about shared changes without rewriting your working files. Use that information to list the changed files.

```sh
git diff --name-status 'HEAD...@{upstream}'
```

If Git says no comparison branch is configured, stop and find out which shared branch to compare against. Do not guess a branch name and continue. When you find a relevant file, read its changes.

```sh
git diff 'HEAD...@{upstream}' -- path/to/file
```

Replace `path/to/file` with a file from the list. If the short change summary is not enough, inspect the full file and related tests.

### 2. Apply the changes you reviewed

If you decide to apply the reviewed changes to your local files, first check whether you have any unsaved work.

```sh
git status --short
```

If anything is listed, save that work before proceeding. If you cannot save it, stop before applying the shared changes.

When there is no unsaved work and the shared update can be added as the next step in your current history, use:

```sh
git merge --ff-only '@{upstream}'
```

This proceeds only when Git can add the shared update directly after your current work. If you and the shared repository have made separate changes, do not combine them automatically. First decide how to bring them together. If you are unsure whether an update should be applied, keep checking instead of applying it automatically.

## Do this each time

- Get information about shared changes before starting work.
- Check which files changed and read the changes related to your task.
- Apply changes only after reviewing them and deciding they are needed.
- Never automatically overwrite or combine changes when local work or separate histories are present.

When using a system other than Git, also keep the action that checks shared changes separate from the action that applies them to your local files.

## Tell the AI what to do

```text
Before editing, get information about the latest shared changes.
Open only the changed files that relate to this task.
Do not overwrite local work. Apply shared changes only after checking their contents and the state of local work.
If the shared location is unclear, histories have diverged, or applying changes could overwrite work, stop and report the situation.
```

## Why this reduces context

Checking the changed-file list first lets the AI read only the relevant changes instead of reviewing the whole shared project. Separating the check from applying changes also helps prevent local work from being lost.

## Terms

Git is a tool for recording and sharing file changes. In this guide, the shared location means a place such as GitHub where people share changes. `fetch` gets change information without rewriting your working files. `merge` applies the changes you reviewed to your local files.
