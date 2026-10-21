# Check only the rules that apply to this task
> Japanese version: [今回の作業に関係する決まりだけ確認する](../../jp/手法/今回の作業に関係する決まりだけ確認する.md)


Even when a project has many rules, you do not need to give all of them to the AI for every task. First identify the feature being changed, then tell the AI to read the rules that apply to it. Include background and detailed explanations only when they help with a decision.

## Example: fix a date bug

Suppose an app has these rules:

- Do not change the format of saved data.
- Add a description to every screen button.
- Use blue colors for new screens.

If a date read from a table file is one day off, first check the rule about saved data. The button and color rules do not apply if the fix does not change the screen.

## Separate requirements from recommendations

Some rules must never be broken. Others are usual guidance that can be changed with a reason. Treating them as equally strict can make the AI treat a recommendation as an absolute ban or miss a real requirement.

| Kind | Meaning | Example |
| --- | --- | --- |
| Required | The change cannot be accepted if this is broken | Preserve the saved data format |
| Recommended | Usually follow it; explain why if you do not | Reuse existing screen components |
| Reference | Use it to help decide; do not call it a violation | Where a similar bug appeared before |

## Find the rules that apply

1. Identify the feature or files being changed from the work request.
2. Tell the AI which required rules apply to that feature.
3. Ask the AI to read recommendations or background only when they affect a decision.
4. Review automatic check results related to this change, or ask the AI to report them.

Passing an automatic check does not prove that every rule was followed. Review rules that cannot be checked automatically yourself, or ask the AI to compare the relevant code with the explanation.

You do not need to make every rule machine-checkable. Add a new automated check only when the rule is worth checking repeatedly and can be evaluated without unreliable guesses.

If you find that the change affects another feature, or that two rules conflict, read the additional sections you need. Do not skip a rule just to reduce reading when you cannot tell whether it applies.

## When an exception is needed

If a required rule must be changed for this task, note which rule is excepted, why, and the limited scope. Keep a link to the original rule. Do not extend an exception to unrelated files or future work.

## Tell the AI what to do

```text
Use the task to identify which feature is changing.
Read the rules that apply to that feature; check background guidance only when it affects a decision.
Run relevant automatic checks and review any applicable rules those checks cannot judge.
```

## Why this reduces context

By telling the AI which feature is changing, you can leave unrelated rules out of the request. Ask it to check additional guidance only when needed, and review any rules that require human judgment.

## Optional helper tools

- [policy-index](../../../tools/common/medium/policy-index/README.md) finds candidate clauses and their source locations in a rule document. Use it when the rules are long.
- [policy-check](../../../tools/common/medium/policy-check/README.md) checks files against rules that can be expressed mechanically. Treat its result as evidence only for what it checked.

## Terms

- **Policy Routing**: Finding the rules that apply to the current task and checking them first.
- **Required rule**: A condition that must be met for a change to be accepted.
- **Recommendation**: Guidance that should usually be followed but may be changed with a reason.
- **Automatic check**: A program that examines rules and reports possible violations or problem locations.

