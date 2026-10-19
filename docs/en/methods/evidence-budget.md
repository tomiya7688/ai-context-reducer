# Before investigating, decide what checks can identify the cause
> Japanese version: [調査前に、原因を判断する確認項目を決める](../../jp/手法/調査前に、原因を判断する確認項目を決める.md)


When you ask an AI to investigate a bug, it may keep reading related material “just in case” instead of moving on to a fix. Decide in advance what you need to know to identify the cause, and include those checks in your request. Ask the AI to move on once it has checked them.

## Example: a date appears one day off

For a date bug, first check:

- what input causes the wrong date
- where the code converts dates
- whether there is a test for the same input
- what result should be correct after the fix

Once these checks agree and give you enough information to judge the likely cause and the correct result after the fix, stop searching broadly through unrelated files.

```text
Check first:
  - how to reproduce the bug
  - the date conversion code
  - related tests and the expected result

Check if needed:
  - code for nearby features
  - old change history
  - project-wide guides
```

For one task, put this short checklist in the work request. If the work spans several conversations, copy the [task note template](../../../templates/CONTEXT_PACK.md) to `CONTEXT_PACK.md` and tell the next AI to read that path. If the same checks apply to many tasks, keep them in `AGENTS.md` or a relevant guide under `docs/` and link to it from `AGENTS.md`.

## Ask why another search is needed

Before reading more files or history, ask: “What do we still not know?” and “What decision will this help us make?” If you can answer, check only what is needed to resolve that question. If the answer would not affect the work, do not expand the search.

## When to check more

Go beyond the initial list when:

- code and tests behave differently
- the cause is unclear and nearby code must be checked
- the change may affect another feature
- you cannot find how to confirm the work is complete

Once the added material answers the question, do not keep expanding the search. Move on to the fix or its verification. There is no need to keep reading history or guides once you know they do not affect the task.

## Write a short plan before starting

```text
Check for this task:
- how to reproduce the bug
- date conversion code
- related tests

Check more if:
- code and tests disagree; then inspect the caller too
```

For a small task, there is no need to make a separate document for this list. A few lines in a work note—or a quick mental check—may be enough.

## Tell the AI what to do

```text
Before starting, list what must be checked to understand the cause.
For each item, say what answer would let you proceed.
Stop broad searching once those checks agree. Search further only if a new question affects the decision.
```

## Why this reduces context

Deciding in advance what information is needed avoids reading loosely related material “just in case.” If the cause or completion check is still unclear, the AI investigates that question, so required evidence is not skipped.

## Terms

- **Scope of checks**: The code, tests, guides, and other material the AI reads to make a decision about the task.
- **Required evidence**: Inputs, code, and test results needed to make a decision or confirm that the fix works.
