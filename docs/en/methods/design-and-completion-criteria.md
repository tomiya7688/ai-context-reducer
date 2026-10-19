# Set the goal and finish conditions before work

> Japanese version: [作業を始める前に、目的と終わりを決める](../../jp/手法/作業を始める前に、目的と終わりを決める.md)

Before asking an AI to implement a change, briefly state what to change, what to preserve, and how to know it is done. A person or AI taking over can use that note and the related documents to continue.

## What to decide

Write only what matters for the task in its work request, task note, or design document.

1. **Goal:** Whose problem does the change solve?
2. **Change scope:** Which feature or files may change?
3. **Must preserve:** Which existing behavior or promises to other programs must remain?
4. **How to know it is done:** What should work, and what should be checked?
5. **Documents to read:** Where are the detailed requirements and current request?
6. **Human review:** What needs a person to judge, such as usability or appearance?

## Example to give the AI

```text
Goal: Save the language chosen on the settings screen.
Files: The settings screen and settings storage.
Must preserve: Do not break settings that are already saved.
Done when: The chosen language is saved and remains after restarting the app. Related tests pass.
Read: docs/settings.md and this task request.
Human review: Check whether the screen text is easy to read.

Read these conditions before starting. Do not guess missing requirements; ask first if an important detail is unclear.
```

For a small change, the goal and check in the task request may be enough. For work spanning days or people, include conditions to preserve and documents to read. Update the note when requirements change, so old and new decisions are not confused.

## Why this reduces context

If you do not give the AI a goal or finish line, it may search past conversations and broad areas of code to guess intent, scope, and tests. Give it a short note with a starting point and a way to check completion. Automate repeatable checks and share their brief results so you do not have to pass long procedures or successful logs each time.

## When to automate a check

Consider an automatic check when the same check is repeated, a broken user-facing promise must be caught, or the files actually delivered must be inspected. An automatic check is a build or test run by a computer before changes are shared. Do not add one if its upkeep and runtime cost more than the checking time it saves. Leave usability or other judgments that a computer cannot make reliably for human review.

## If an assumption changes

If an important condition is missing or the note disagrees with the code, update the note instead of guessing. If a required check cannot be performed, report it as unverified rather than complete.

