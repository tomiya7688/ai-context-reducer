# Guide work by the kind of change

> Japanese version: [変更内容ごとに読む場所と確認方法を一覧にする](../../jp/手法/変更内容ごとに読む場所と確認方法を一覧にする.md)


A screen-display change and a data-storage change call for different code and checks. Decide where to look based on the change so you can tell the AI where to start. The map lists the code or documents to read first, the initial check, and conditions that call for a wider investigation.

## Example map

| Change | Read first | Check first | Check more when |
| --- | --- | --- | --- |
| Screen display | Screen code and usage notes | Screen tests | Another feature uses the changed display |
| Save or load behavior | Save code and data-format notes | Save/load tests | Old saved data may be affected |
| Packaged files | Build settings and packaging instructions | Launch the packaged app | Other supported platforms may be affected |

Replace these examples with actual paths and checks from your project. Do not use labels like “screen code” without pointing to real files.

## Tell the AI what to do

```text
Choose the row that matches this change. Start with the documents and code listed there.
Run the listed check first. If you change shared code, saved-data formats, how another program uses this code, or cannot tell what else is affected, inspect and check the related areas too.
If no row fits, search for the changed code, decide what to read and check, and report that the map needs an entry.
```

## What to include

- Concrete examples that help identify each change type.
- The documents and code to read first.
- The first test or behavior check to run.
- Conditions that require a wider check.

Reuse existing folder ownership notes or file maps instead of creating a duplicate. A color change to one screen may not require reading save code. If the screen also changes saved data, include the save code and tests.

## Why this reduces context

Give the AI the row for the kind of change so it can start at the listed files instead of searching the whole project. Keep locations and purpose in the map, and have the AI open detailed sources only when needed. If the target is unclear or shared code changes, ask it to expand the search so the shorter starting list does not hide missing checks.

## How to use and update the map

1. Identify the behavior the request changes.
2. Find the closest kind of change in the map, then check its first code and tests.
3. If the change turns out to be wider than the row assumes, add the direct users and the related contract tests.
4. If no row fits, search normally; once you know a reliable place to check, update the map.

The map is an entry point. It does not guarantee that the listed files are always enough. If the map and the current code disagree, check the code and tests and fix the stale row. Fix the map in the same change that moves code or tests. If the project already divides responsibilities into screens, storage, or communication, use that division in the map instead of inventing a new one.

## When to use a map

A map helps when people repeatedly search for the same code and tests. A small project with only a few obvious change areas may not need one. Do not keep adding rows if updating the map costs more than finding the files.

## Where to save the map and how to point the AI to it

Save a reusable map as `docs/change-checks.md`, for example. Link to it from the root `AGENTS.md` and tell the AI to consult the matching row before starting. If your AI does not automatically read `AGENTS.md`, give it the map's path in the task request. For a one-time change, put the files and checks directly in the request instead of creating a map.

## Optional helper tool

- [change-router](../../../tools/common/medium/change-router/README.md) suggests the tests and documents to check first from changed files. Verify its candidates against the map and the original sources.

## Terms

- **Change Routing Map**: A table, and the way of using it, that links each kind of change to the first code to read, the tests to run first, and the explanations to read when needed.
