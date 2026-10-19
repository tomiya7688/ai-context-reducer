# Decide what the AI usually does not need to read

> Japanese source: [AIに普段読ませないファイルを決める](../../jp/手法/AIに普段読ませないファイルを決める.md)

When you ask the AI to fix an app, do not give it unrelated logs or temporary files by default. Set a default reading scope that leaves those files out while keeping the code and tests it needs.

This decides what information the AI receives while working. It does not delete files or change which files are shared or recorded by the project.

## Decide what the AI usually does not need to read

The following files and folders are often unrelated to a task, so they may be marked as things the AI usually does not need to read:

- output files created when building the app
- logs, investigation records, and large reports
- downloaded third-party libraries
- temporary files and caches
- work saves and backups
- old change history unrelated to the task
- files created automatically by an editor or development tool

Use these examples as a starting point. Do not tell the AI to skip a file based only on its folder name: a project may rely on something that looks like generated output or a log.

## Let the AI read what the task needs

Before deciding that a file can usually be skipped, check:

1. Is it an official source for a requirement or behavior?
2. Is it part of the change being requested?
3. Is it needed to check or test this change?
4. Is it important project-specific data?
5. Do you know how to recreate it when needed?

If any answer is yes, do not blindly exclude it. Let the AI read it for tasks that need it. If you cannot tell, leave it undecided.

### Example: checking a packaged app

For an ordinary code change, the AI may need the app's code and tests, but not a packaged copy made earlier. For a task that asks whether the packaged app starts, the AI must inspect that package.

The same file can be unnecessary for one task and essential for another. “Usually skip” does not mean “never read.”

## Do not confuse skipping a file with deleting it

You can tell the AI to skip a file while keeping it in the project. This is different from changing a setting such as `.gitignore` to stop sharing or recording the file.

```text
usually skip it for the AI
  → limit what the AI reads during a task

exclude it from sharing or recording
  → change project settings or file handling
```

There is no need to delete a log or generated file just because the AI usually skips it. Before changing project settings, separately check that the file is not needed for a release or test.

## How to treat common file types

| File type | Usual approach | Example when it is needed |
| --- | --- | --- |
| Build output | Usually skip | Check that a release package was built correctly |
| Logs and activity records | Read only the relevant part | Find the cause of a failure |
| Third-party libraries | Usually skip | Investigate a project patch or a security issue |
| Temporary files and caches | Usually skip | Fix a bug caused by cached data |
| Old change history | Usually skip | Find when a bug first appeared |
| Test sample data | Read when a test needs it | Check behavior with that data |

## Keep the rule short in small projects

A few lines in the project-wide guide may be enough:

```text
Usually skip:
- temporary build files
- logs unrelated to this task
- old change history unrelated to this task

Read a file if the task or its tests need it.
```

Create a separate list or automatic checker only when repeatedly sorting out these files becomes a real burden.

## Where to put the exclusion and how to tell the AI

To actually keep files out of the AI's automatic reading scope, use the project-level exclusion setting supported by the AI product. The setting's filename and location vary, so check that product's instructions. `.gitignore` controls Git tracking; it does not tell an AI what to read. If the AI product has no exclusion setting, write a rule in the root `AGENTS.md` such as “Usually skip this path, but read it when the change or its tests need it,” and repeat that instruction in the task request. This guides the AI but does not technically prevent it from opening the files.

## Tell the AI what to do

```text
Before opening logs, temporary files, or generated output, check whether this task needs them.
Do not exclude files needed for the implementation, requirements, tests, or package checks.
If you cannot tell whether a file is needed, leave it available and explain why.
```

## Why this reduces context

The AI no longer receives unrelated logs or generated files for every task. When a task needs one, ask the AI to read it; the rule should not hide evidence needed to check the result.

## Terms

- **File usually skipped by the AI**: A file or folder unnecessary for many tasks but needed for a particular task.
- **Sharing or recording settings**: Settings such as `.gitignore` that control whether project files are shared or recorded. These are separate from what the AI reads.

## Optional helper tool

- If useful, `ignore-candidates` lists files the AI may not need for ordinary tasks. Use it to find candidates to exclude from the usual reading scope. It does not decide what is unnecessary, delete files, or change sharing settings.
