# Decide When to Stop Exploring

> Japanese Source of Truth: [調査を止める条件を決める](../jp/調査を止める条件を決める.md)

When asked to investigate a problem, an AI may keep reading related files "just in case" even after it has enough information to proceed. Decide in advance what facts are needed to start or finish the task. Once those facts are confirmed, move on to the next step.

## Example: Fixing a CSV date bug

Suppose a CSV import shifts dates by one day. Before investigating, set these conditions:

- Reproduce which input causes the shift and what the result looks like.
- Find the code that converts the date and the test that checks its behavior.
- Confirm that the fix preserves the date and the related test passes.

Start with the bug report, the date conversion code, and its test. Once you have confirmed how the input relates to the implementation, the test result, and that they agree with the requirement, stop exploring and begin the fix. There is no need to read every date-related document or commit in the repository.

## Set a stop condition

Before investigating, write down three things:

1. **Goal**: what needs to change.
2. **Facts needed to decide**: what must be known to confirm the cause or begin work.
3. **How to verify completion**: what will show that the fix works.

Identify and check only the sources and tests needed to establish those facts. When the facts are available, consistent, and the completion check is clear, stop searches that would only confirm the same conclusion. This is not a cap on search count or tokens. It marks the point at which the next useful step is clear.

## When to investigate further

Resume investigating when work reveals a new dependency, sources conflict, or a test fails. Check only the sources needed to resolve that question, then stop again when you have the needed facts.

Do not present unknowns as verified. If information needed to decide completion is unavailable, record it as unverified and ask for clarification or pause the work as appropriate. Resolve security or compatibility questions when they could affect the current change.

## When to use this

This approach helps when an investigation could spread across many files and it is unclear how much to read. A small change with an obvious target and verification method does not need a written stop condition.

If it is unclear which evidence is needed in the first place, see [Decide What Evidence to Collect](evidence-budget.md).

## Example request to the AI

> Before investigating, restate the completion and stop conditions. Stop when the required evidence is available; investigate further only if a check fails, sources conflict, or a new affected area appears. Report what is verified and what is not.

## Optional tools and terminology

If useful, [exploration-stop-check](../../tools/common/medium/exploration-stop-check/README.md) checks whether a task note has the minimum information needed to begin. Its check is heuristic, so verify missing details against the request and original sources. This method is called **Exploration Stop** or a stop condition.
