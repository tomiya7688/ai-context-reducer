# Working Note (Context Pack)

> Japanese source of truth: [作業用メモ](../jp/作業用メモ（Context%20Pack）.md)

A Context Pack is a **short note that gives someone starting the current task its goal, target, constraints, and completion criteria**. It collects the information and links needed now, so the person doing the work does not have to reread a long conversation, Issue, or repository from the beginning.

## Example: Fixing CSV date conversion

An Issue that says only “CSV dates are shifted; fix it” leaves the person doing the work to find the parser, existing tests, supported date format, and allowed scope. A short note can provide the relevant details:

```markdown
# Current task
- Goal: Keep YYYY-MM-DD dates from shifting to the previous day when read from CSV
- Target: `src/csv/date_parser.py` and its related tests
- Constraints: Preserve existing CSV formats and the public API
- Completion: Add a test that reproduces the bug and pass the related tests
- Read first: The reproduction in this Issue and `src/csv/README.md`
- Out of scope: Redesigning CSV handling or adding time-zone support
```

The person can begin with the relevant parser and tests. Revisit the full conversation or Issue only if the listed references do not settle a required condition. If the target or completion criteria are unknown, record that they are unknown and check the original source instead of guessing.

## What to include

Keep only the fields needed for this task.

| Field | What to record | Example |
| --- | --- | --- |
| Goal | The state the change should achieve | Read dates without shifting them to the previous day |
| Target | Files, behavior, or tests to inspect first | The date parser and related tests |
| Constraints | Compatibility or scope that must be preserved | Keep the public API and existing CSV formats |
| Completion | A result or check that decides when the work is done | The reproduction and related tests pass |
| References | Entry points to authoritative sources | The Issue reproduction and feature README |
| Out of scope | Work that should not expand into this task | Adding time-zone support |

Not every task needs every field. For a small change, the goal, target, and completion criteria may be enough. State constraints explicitly when compatibility, safety, or another boundary matters.

## Relationship to original sources

A Context Pack is a guide for the current task, not a place to store specifications or project history. Keep the basis for decisions in the Issue, formal design docs, source code, tests, or other authoritative sources. The pack points to those sources and records the conditions selected for this task. Duplicating a specification in both places can make them disagree, so put lasting explanations in their authoritative source.

Do not carry a temporary pack forward by appending new work after the task ends. Record decisions that remain relevant and unfinished work in an Issue or formal document. If a pack grows, remove information that is not needed to judge completion before adding more.

## When to use one

A Context Pack helps when work spans several files or references, resumes across conversations, or has targets or completion criteria that are not clear from the request alone. For a one-file change with an obvious target and result, the instruction itself may be sufficient; a separate note would add little.

## Template

Keep only the fields that apply. Do not guess to fill blanks or add every field mechanically.

- [Context Pack template](../../templates/CONTEXT_PACK.md)

## Example request to the AI

The AI may not load a task note automatically. For a one-time task, attach the file or name its path in the request. For recurring use, verify the AI tool's actual instruction-loading settings.

> Follow the attached Context Pack's goal, constraints, and completion criteria. Ask about anything its references do not resolve instead of guessing. At the end, report the result for each completion criterion and anything not verified.

## Optional tools and terminology

Use [context-pack-builder](../../tools/common/medium/context-pack-builder/README.md) to draft a pack if helpful. A per-task note of goals, references, and completion criteria is called a **Context Pack**.
