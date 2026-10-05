# Check the Rules That Apply to This Change

> Japanese Source of Truth: [今回の変更に関係する規則を確認する](../jp/規則の確認先を絞る.md)

When development rules are extensive, first find the rules that apply to the current change. Checking the relevant sections and any existing automated checks means you do not have to reread unrelated design or style guidance for every task.

## Example: adding an API

Suppose the rules say, "APIs require authentication unless they are explicitly marked public" and "error responses must not include secret information." For a new API, start with these two rules and how to verify them. You can leave rules about screen colors or document formatting unread unless the change makes them relevant.

If an existing check verifies authentication, inspect its result. To verify that error responses do not reveal secrets, which the check may not cover, inspect the implementation and tests. A passing check proves only what that check covers; it does not prove that every rule was followed.

## Choose the applicable rules

Use the changed area and the nature of the change to find applicable mandatory rules. If you cannot tell whether a rule applies, read the relevant explanation or original policy. Recommendations and reference material can wait unless they affect the current decision.

Read additional sections when the change turns out to affect another feature or when rules conflict. Do not skip an unclear requirement just to reduce reading.

## Automated checks

Use an existing automated check when it can decide a rule reliably. Treat its result as evidence only for the items it checks. Inspect failures and rules the check cannot evaluate by reviewing the relevant code and tests.

There is no need to automate every rule. Add a new check only when the rule is worth checking repeatedly and can be evaluated without unreliable guesses.

## Example request to the AI

> Find the mandatory rules that apply to this change in their original source, and show only the relevant clauses and evidence. For machine-checkable rules, report what the check covers and its result. For rules needing human judgment, inspect the relevant code or tests.

## Optional tools and terminology

Use [policy-index](../../tools/common/medium/policy-index/README.md) to find clauses and [policy-check](../../tools/common/medium/policy-check/README.md) for supported automated checks. This method is called **Policy Routing**.
