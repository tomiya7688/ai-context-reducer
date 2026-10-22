# Summarize what your project supports and its limits

> Japanese source: [プロジェクトでできることと制限を短くまとめる](../../jp/手法/プロジェクトでできることと制限を短くまとめる.md)

When you ask an AI to change code, it may repeatedly look up **which features work, what is not yet supported, and what conditions must be preserved**. You can record those facts in a few lines of your existing README. If that would make the README too long, use a separate short note.

The note gives the AI the project's current state, rather than copying detailed specifications or the whole codebase.

## Example: importing tabular data

Imagine your application has the following features. This is an illustrative example.

```text
Works now: Importing tabular data
Limitation: Dates are treated as text; no time-zone conversion
Unsupported: Spreadsheet-specific file formats
Detailed rules: docs/date-format.md
```

Check your project's current code and specification before writing the note. The path `docs/date-format.md` is fictional; replace it with the actual source in your project.

## What you should record

Choose facts you or the AI keep looking up:

- Main features that currently work
- Limits and conditions that must be preserved
- Features not yet supported
- Locations of original specifications, code, or tests for more detail

Do not list every feature or copy old discussions. Put conditions for one specific task in its [task note](context-pack.md) or request instead.

## How to write the note

You can start by adding a few lines to your existing README. **No additional program or dedicated tool is required.**

If you prefer a separate file, copy the [project context template](../../../templates/PROJECT_CONTEXT.md) to the root of your project as `PROJECT_CONTEXT.md`. Fill only the fields that matter.

To have the AI load the note automatically, add a reference to the instructions file your AI actually reads (for example, `AGENTS.md`) for relevant tasks. **Not every AI reads that file automatically.** Check your product's behavior and provide the file path explicitly in your request when needed.

## Ask the AI to use the note

**Example message for you to send to the AI:**

```text
First read the note about what this project currently supports and its limits.
Use only the parts relevant to the current task to find code and tests.
Check the original linked sources for detailed behavior or requirements.
If the note disagrees with the sources or code, report the difference instead of guessing.
```

If your AI cannot open project files, give it the relevant note and original sources yourself. Check the AI's result against current specifications, code and tests rather than assuming the note is always accurate.

## When the project changes

You, or an AI you have authorized to edit files, should update the affected parts. Verify that the revised note accurately reflects current behavior and requirements.

A short note is useful when the same facts must be rediscovered repeatedly. For a one-off change or when the current README is already clear, you do not need another file.
