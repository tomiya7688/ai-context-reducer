# Summarize project capabilities and limitations
> Japanese version: [プロジェクトでできることと制限を短くまとめる](../../jp/手法/プロジェクトでできることと制限を短くまとめる.md)


People starting work need to know what works, what is not supported yet, and what conditions they must follow. A short note with these facts saves them from searching the README and old issues every time.

This note does not replace detailed documentation or instructions for a specific task. Link to the original material so readers can find more detail when they need it.

## Example: reading tabular data

> Tabular data is supported. Dates are read as text. Excel-specific files are not supported. For detailed date rules, see `docs/date-format.md`.

This example makes supported input, date handling, and an unsupported format clear at a glance. Readers can follow the link for the detailed date rules.

## What to include

- Main features that work today
- Limits or conditions users must know
- Features that are not supported yet
- If useful, a goal that matters to upcoming work

Keep detailed specifications and task instructions in their original documents instead of copying them here.

## What belongs in other documents

- README: project overview and how to get started
- AI guide: rules for working on the project and where to find documents
- This note: working features, limits, and unsupported features
- Task note: what someone has been asked to do now
- Documentation and code: detailed specifications and actual behavior

## Update it when things change

Update this note when features or limits change. If it disagrees with the documentation or the code, check those sources and correct the note.

To get started, copy the [project context template](../../../templates/PROJECT_CONTEXT.md) to the repository root as `PROJECT_CONTEXT.md`. Keep only facts people repeatedly have to look up. Point to this file from the root `AGENTS.md` with a note to read it for relevant tasks. If the AI does not automatically read `AGENTS.md`, include both paths in the task request.

## Tell the AI what to do

```text
Read this short note about what the project can do and its limits before starting the task.
Open the linked guide and code if you need more detail about a feature or limit.
If the note disagrees with the code or tests, check them and update the note after the task.
```

## Why this reduces context

Give the AI one short note about the project's current features and limits so it does not have to search the README and old work requests. Include links and ask it to open detailed sources only when needed.

## Terms

- **Context State (project snapshot)**: Keeping a short record of what the project can do now, its constraints, and what it does not support yet. It needs no special tool; a README or a short note is enough to start.
