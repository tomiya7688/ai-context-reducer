# Decide when the AI should stop investigating
> Japanese version: [AIに調査を止めさせる条件を決める](../../jp/手法/AIに調査を止めさせる条件を決める.md)


Before the investigation, write down the input that reproduces the problem, where to find the code that handles it, and the correct result to check after the fix. Tell the AI to stop searching for more files and start fixing the bug once it knows these three things. If any point is still unclear, have it inspect only the places that can answer that question.

## Example: a loaded date is one day off

Suppose a table shows April 9 when its data says April 10. Once the following points are clear, stop investigating for now and start fixing it:

1. You can reproduce the problem with an example input.
2. You know where the code reads the date.
3. You have a way to check that the same input gives the correct date.
4. You know that showing April 10 after the fix means the problem is solved.

To fix this problem, there is no need to read every date guide or inspect all past changes.

## Stop when these three things are clear

- **What to fix:** The work being requested.
- **Where to check:** The related code, tests, or guides.
- **What counts as done:** The behavior or result that confirms the fix.

Writing one line for each before investigating helps the AI judge whether it has checked enough.

```text
Fix: a bug that loads a date one day early
Check: the date-reading code and its test
Done when: the same input displays April 10
```

## If something is still unclear, investigate that question

Continue investigating when:

- you cannot reproduce the problem or identify its cause
- the code and test results disagree
- the change may affect another feature
- you do not know what result would count as a fix

For each additional question, check only the files that can answer it. For example, if the date-reading code calls another function, check that function. Once the question is answered, return to fixing or checking the change.

## Decide what is outside this task

Do not expand the investigation or changes to unrelated features. If useful, write a note such as “Do not change the screen appearance in this task.” Leave future work in a separate request.

Put stop conditions for one bug in that task request. If the same conditions are reused, move them to the root `AGENTS.md` or a guide under `docs/` and say which tasks should use them. A single bug does not need a new instruction file.

## Report checks you could not do

If you cannot perform a check needed to judge completion, report what remains unchecked instead of saying the work is complete. Do not keep investigating solely to remove every unknown; check only what the current fix requires.

## Tell the AI what to do

```text
First confirm the goal, where to check, and what result counts as done.
Once these are clear, stop broad searches and begin the fix.
If a new question affects the fix, inspect only the files needed to answer it.
Report required checks that you could not perform as unverified.
```

## Why this reduces context

Tell the AI what information it needs before it can begin, and ask it to stop reading once it has that information. Have it search again only when a new, relevant question comes up, so unrelated material is not added to the task.

## Terms

- **Stop point for investigation**: The information needed before ending a search and moving on to a fix or verification.
- **Test**: A repeatable way to run a program with the same input and check whether it returns the expected result.
