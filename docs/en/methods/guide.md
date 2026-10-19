# Basic steps for asking AI to work on a project

When you ask an AI to read an entire repository, it also receives information unrelated to the task, making the important files harder to find. This guide explains how to give it only the information needed for the work.

> Japanese version: [AIに作業を頼むときの基本手順](../../jp/手法/AIに作業を頼むときの基本手順.md)

## Decide what “done” means first

For example, suppose the task is “add a language selector to the settings screen.” Before starting, decide:

- **Goal:** Let people choose the display language from the settings screen.
- **Must preserve:** Do not break settings that are already saved.
- **Files to check:** The settings screen and the code that saves settings.
- **How to tell it is done:** The chosen language is saved and remains selected after reopening the app. Related tests pass.

Once these four points are clear, start by checking only the relevant files. If another question comes up, look up only the information needed to answer it.

## Choose where to look based on what you need to know

| What you need to know | Where to look first |
|---|---|
| Project overview | `README` |
| Rules for working in the project | Instructions such as `AGENTS.md` |
| What currently works or does not work | A document describing the current state |
| Specifications and agreements | Detailed design documents |
| What the software actually does | Source code and tests |
| Task goals and priority | Work request or task list |
| Generated files and logs | Only when the task requires them |

If descriptions disagree, check which document the project names as authoritative. Confirm actual behavior with the source code and tests.

## Find the files you need

1. Search by file name or a relevant phrase.
2. Read the results that relate to this task.
3. For large files, start with the relevant parts.

There is no need to open every file first. Skip generated files, logs, and old history when they are unrelated to the task. Keep any files needed to verify that the change works.

## Know when to stop searching

Stop broad searches when you know:

- what to change
- what must be preserved
- which files to check
- how to tell the work is complete

If something is unclear while making or checking the change, investigate that question only.

## Keep task notes temporary

For work that spans multiple days, a short note with the goal, files to change, things to preserve, and checks to run can help with handoffs. Use it to pass along the work; do not treat it as the official specification or copy the same explanation into other documents.

## Where to save information and how to point the AI to it

Choose a location based on how long the information will be used:

| Information | Where to save it | How to give it to the AI |
| --- | --- | --- |
| Goal, scope, and completion check for one task | The task request | Put it in the request. For work spanning several days, copy the template to `CONTEXT_PACK.md` and give the AI its path. Remove the temporary note when the task is done. |
| Rules that apply to project work | `AGENTS.md` at the repository root | Check whether the AI you use loads it automatically. If not, tell the AI to read `AGENTS.md` in the request. |
| Project features and limitations | `PROJECT_CONTEXT.md` at the repository root | Link to it from `AGENTS.md` and ask the AI to read it when relevant. |
| Reusable procedures or lists of documents | A clearly named document under `docs/` | Link to it from `AGENTS.md`, say when it applies, and have the AI open it only for relevant tasks. |

For example, if task-specific checks are listed in `docs/change-checks.md`, add a line to `AGENTS.md` saying to consult that file when choosing checks for a change. Merely creating a file does not ensure the AI will read it. Link it from the instruction file that serves as the AI's entry point, or give the path in the task request. See [Give the AI instructions that match the work location](hierarchical-context.md) and the [templates for AI instructions](../../../templates/README.md) for more details.

## Add only the tools and guides you need

A small project may need only a short guide and search. If the project grows and people repeatedly struggle to find the same files, add a task guide or a map of file responsibilities. Use these lists or automation only when they save more repeated search effort than they take to create and maintain. See [Choose only the methods you need](../adoption/adoption-priority.md) for details.

## Check the change

Run tests or checks that fit the change. For a screen change, inspect the actual screen when needed. For a change to a distributable package, check the package itself. A result that did not inspect anything—for example, zero tests run—is not evidence that the change works.

Say when something has not been checked; do not describe it as confirmed.

## Avoid

- Bundling unrelated changes with the task.
- Copying the same explanation into several documents.
- Adding lists or guides that a small project does not need.
- Guessing about things that have not been checked.

## Tell the AI what to do

```text
Check the root `AGENTS.md` for project instructions.
If project features or limitations matter to this task, read `PROJECT_CONTEXT.md` and follow only links relevant to the change.

Task:
Add a language selector to the settings screen.
Check the settings-saving code and related tests. Confirm the selected language remains after restarting the app.

Confirm what this task changes, what must stay the same, and how to tell it is done.
Search for related files and read only what is needed to decide and make the change.
Run checks that match the change and report anything you could not verify.
```

This gives the AI a clear starting point, so it does not need to read the whole project to infer the goal. Necessary code, requirements, and checks remain in scope.
