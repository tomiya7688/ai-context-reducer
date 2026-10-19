# Make a short list of where information lives

> Japanese version: [資料の場所を短い一覧にする](../../jp/手法/資料の場所を短い一覧にする.md)

For an app with many files, the AI may need only the date rules, the code that reads dates, and the related tests. A short list tells it where those files are instead of asking it to open every file.

| Where to look | What it explains |
| --- | --- |
| `docs/date-format.md` | Date rules |
| `src/data/date.py` | Code that reads and writes dates |
| `tests/data/test_date.py` | How date handling is checked |

Give the list to the AI and ask it to open the entries related to the task. Keep locations and short descriptions in the list instead of copying full documents into it.

## What belongs in the list

- A file, folder, or web address
- What information is there
- Which feature or kind of work it relates to
- A short note if useful, such as whether a file is generated or outdated

Do not copy code, full guides, long summaries, or logs into the list. When a decision needs more detail, open the original material.

## Keep each document's job clear

| Document | What belongs there |
| --- | --- |
| Project-wide guide | Where to have the AI start and the rules that apply across the project |
| [Summarize project capabilities and limitations](context-state.md) | What works now and what limits apply |
| This list | Where detailed information lives |
| [Write a short note for the current task](context-pack.md) | The goal, materials, and conditions for this task |
| Guides, work requests, code, and tests | Detailed requirements and actual behavior |

If a list disagrees with a guide, check the guide. Check the work request for decisions made there, and code or tests for actual behavior.

## Show the AI only relevant entries

If the list gets long, show only entries related to the current task. A date fix might need only the date rules, date-handling code, and related tests. An item being listed does not mean it must be opened. If a missing file is needed, search for it and add it to the task's reading list.

## When to make a list

Make one when people repeatedly search for the same files, or when the files needed for each task vary and are hard to find. Skip it when the request names the files, the project is small, or the task happens only once. Reuse an existing guide if it already shows where to look.

## Where to save it and how to point the AI to it

For a reusable list, save it as `docs/resource-list.md`, for example. Link it from the root `AGENTS.md` with a note about which tasks should use it. If your AI does not automatically read `AGENTS.md`, give it the path to `docs/resource-list.md` in the task request. For a one-time task, do not create a list; name the files to read in the request.

## Update it when things change

Update the list when a file moves or changes purpose. An old entry may point to the wrong place. If you are unsure whether an entry is current, search for the file instead of trusting the list. Update the original guide when its details change; do not keep adding those details to the list.

## The format can vary

A table in a document or an existing project list is enough. Include each location and its purpose so you can direct the AI to relevant material and ask it to open the original source for details.

## Tell the AI what to do

```text
Choose only the entries related to this task. Open the linked documents and check the relevant content.
If a needed file is missing or a link is out of date, search for it and report the missing entry.
Do not treat the list alone as proof of a requirement or behavior.
```

## Why this reduces context

Give the AI a short list of locations and purposes so it can open only relevant files instead of reading them all in sequence. Keep details and logs in the original documents rather than copying them into the list.

## Optional helper tool

- If useful, `context-manifest` lists files and details such as their size. Use it to find candidate files to read, then have the AI choose what to read based on the task.

A hand-written list or an existing search feature can serve the same purpose.
