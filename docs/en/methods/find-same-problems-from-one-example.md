# Have the AI find the same problem from one example

> Japanese source: [一つの指摘から、同じ問題をAIに探させる](../../jp/手法/一つの指摘から、同じ問題をAIに探させる.md)

After you point out an unclear actor in one document, another page may still have the same gap. Instead of finding and explaining every location yourself, give the AI the example and criteria, then ask it to inspect other locations within a defined scope.

“Fix every similar sentence” may also change quoted AI requests or explanations with different meanings. First specify the problem, search scope, and similar cases that are excluded.

## When to use it and how to decide

- Use it when repeatedly pointing out the same explanation gap, code error under the same conditions, or missed configuration update.
- It fits when you can state conditions that apply beyond one example. If the concern is only “hard to read,” first identify what readers cannot determine.
- Matching words do not establish the same problem. Check context such as readers, actors, input conditions, and where settings are used.
- Start with one problem and one scope. If investigating different problems together, keep their criteria and results separate.

## Steps to use it

### 1. Provide the example, reason, and exclusions

For documentation, use a request like this. Replace fictional paths and headings with real ones.

```text
Example: “Check the settings” under “Actions” in docs/users/save.md.
Problem: A procedure for a person does not say whether the person checks or asks the AI to check.
This action is performed by the AI, so explain that the person should ask the AI to check settings.
Scope: Japanese Markdown under docs/users/.
Excluded: quoted requests addressed to the AI, descriptions of tool behavior, and specifications for other readers.
```

Have the AI read the surrounding text to establish why the example is a problem. “Check settings” in a quoted request is addressed to the AI and excluded under these criteria. Do not replace every occurrence of “check.”

Separate conditions for code and configuration in the same way.

| Target | Problem conditions | Similar but excluded cases |
| --- | --- | --- |
| Code | A specification says a key is optional, but access lacks handling for absence | Required-key access whose specification calls for an error when absent |
| Configuration | An endpoint changed, but current runtime settings still use the old value | Historical test fixtures or examples describing migration from old settings |
| Documentation | Instructions for people omit who performs an action delegated to the AI | Quoted requests to the AI or descriptions of tool processing |

Have the AI verify defaults or new endpoints against specifications or change records, rather than infer them from the example.

### 2. Have the AI restate brief criteria before searching

Ask for matching conditions, exclusions, necessary evidence, and scope. If multiple interpretations remain, have it ask before searching. Inspect the criteria yourself before proceeding.

For repeated use, save criteria in, for example, `docs/review/actor-clarity.md`.

```markdown
# Criteria for identifying unclear actors

- Target: instructions for people in Japanese Markdown under docs/users/
- Match: the text and context do not identify the actor for an action delegated to the AI
- Excluded: quoted requests addressed to the AI, tool behavior descriptions, specifications
- Evidence: intended reader, surrounding explanation, and who performs the action
- Fix: clarify what the reader should do; do not invent content
- Confirmed example: “Actions” in docs/users/save.md
```

When expanding criteria, decide the additional targets and exclusions again. Do not generalize conditions that cannot be established from the original example. For a single task, these fields can remain in the request.

### 3. Record the inventory and inspected scope

Split large scopes by folder or file type. Link criteria and results in, for example, `docs/review/actor-clarity-results.md`.

```markdown
# Investigation results for the same problem

- Criteria: docs/review/actor-clarity.md
- Version inspected or state when work began:
- Target file inventory:
- Excluded locations and reasons:
- Search coverage:
- Content inspected against the criteria:
- Uninspected files or sections and reasons:

| Classification | File and line or heading | Reason and evidence | Confirmed for correction? |
| --- | --- | --- | --- |
| Definite match / Needs confirmation / Excluded | | | |
```

Separate running searches from reading content against the criteria. Nonmatching files may contain the same issue with different wording. Identify whether hidden files, generated content, search exclusions, and unreadable files are in or out of scope.

Line numbers shift after editing; also provide function names, configuration keys, or headings. If criteria or target files change, record which criteria were applied where and reinspect affected locations.

### 4. Return candidates with evidence

| Classification | Meaning | Documentation example |
| --- | --- | --- |
| Definite match | Conditions and evidence establish the issue | Instructions for a person omit the actor of an action delegated to the AI |
| Needs confirmation | Some conditions or evidence are unknown | Context does not establish whether a person or the AI should act |
| Excluded | Similar appearance but outside agreed conditions | A quoted request directly tells the AI to check |

A definite match does not itself authorize editing. Inspect locations, context, and reasons, then identify candidates the AI may fix. Ask about unclear meaning instead of allowing speculative bulk changes. Summarize large excluded sets with representative examples and reasons while retaining necessary evidence.

### 5. Recheck with the same criteria after corrections

Specify confirmed targets and allowed changes when requesting fixes. Have the AI list changes and inspect whether the diff addresses the current problem.

Repeat both searches and content checks against the criteria. Do not finish merely because a word disappeared. Check that edited locations preserve meaning and satisfy the criteria, and inspect remaining candidates or unresolved items. For code or configuration, also inspect results of relevant existing checks and tests.

If files changed since inspection, return added or changed content to the review scope. When areas remain uninspected, report remaining matches within checked areas and list uninspected locations. Claim all items in a defined scope were checked only after inspecting every file in the declared inventory against the criteria. Even that is not a guarantee that every possible problem is absent.

## Example AI requests

The following requests investigation only. Replace the example and destinations with real locations.

```text
Find whether the following issue also occurs elsewhere in the specified scope.
Example: “Check the settings” under “Actions” in docs/users/save.md.
Problem: instructions for a person omit the actor of an action delegated to the AI.
Scope: Japanese Markdown under docs/users/.
Excluded: quoted AI requests, tool behavior descriptions, specifications.

First summarize matching conditions, exclusions, and necessary evidence.
If multiple interpretations remain, ask. Do not begin broad searching until I confirm the criteria.
Then save criteria in docs/review/actor-clarity.md.

Create a target file inventory and judge candidates using context and evidence.
Classify candidates as definite matches, needing confirmation, or excluded.
Record locations and reasons in docs/review/actor-clarity-results.md.
Separately report search coverage, content inspection, exclusions, and uninspected areas.
Make no changes in this task; return only the candidate list.
```

After checking candidates, follow with this request.

```text
Fix only candidates I marked as confirmed in the results.
Do not change unresolved or excluded candidates.
List corrected locations and changes, then recheck them and remaining candidates against the same criteria.
Report necessary check results, remaining issues, content inspected, and uninspected areas.
```

In a chat that cannot read files, attach or paste the example’s context, criteria, target inventory, and necessary content. Paths alone do not provide contents. Do not count unseen files as inspected.

For recurring checks, put a brief reference in, for example, `AGENTS.md`: when changing user instructions, read `docs/review/actor-clarity.md` and apply it to changed passages. Do not copy details or past candidate lists into the entry instructions. Explicitly provide the path and trigger when the AI does not load instructions automatically.

## Distinguish revising an explanation from investigating the same issue

For a single passage, identify what readers cannot understand and supply the missing explanation there. If that finding applies elsewhere, use this guide to define criteria and scope, inspect candidates, and then correct them.

[Make explanations understandable](make-explanations-understandable.md) supplies examples for criteria about information missing for readers. For reuse decisions before adding code, see [Inspect existing code before adding similar responsibilities](reuse-existing-code-before-adding.md).

## Why this can reduce context use, and its limits

Reusing an example and criteria can reduce repeated exchanges explaining the same issue at each location. Defining scope and conditions first can also reduce unrelated material supplied for inspection. Short candidate and evidence records reduce the need to reconstruct the investigation from the entire conversation later.

Investigation, candidate confirmation, and rechecking also consume input. Excessive scope or repeatedly outputting all excluded content can increase usage. Retain necessary evidence and checks while reducing repeated explanations and unrelated reading. Discovery accuracy and context savings for these requests have not been measured.

## Supporting tools

- **Text search:** Finds candidate words or processing matching the example. Read content to check other wording or different meanings of the same words.
- **Code search by structure:** Finds candidates through function or processing shapes. It may not establish specification exceptions or usage conditions.
- **Similar-code detection:** Shows similar code fragments. Inspect input conditions and users to determine whether they share the issue.
- **Git diff:** Shows corrected locations to check that only confirmed candidates changed and unrelated meaning changes did not enter.

## About this method

[Wu et al.’s paper](https://proceedings.mlr.press/v306/wu26bk.html) reports deriving error patterns from one patched example and finding similar bugs across a codebase. [1] The authors call bugs with the same root cause recurring across code segments **Recurring Pattern Bugs**.

The paper evaluates a system combining analysis of code relationships and other program properties with large language models (LLMs), AI models that generate and interpret text. It does not validate these general chat requests or their application to documentation and settings. Do not use its results as accuracy or context savings for this procedure.

## References

1. Qiushi Wu, Yue Xiao, Dhilung Kirat, Kevin Eykholt, Jiyong Jang, Douglas Lee Schales (2026). [One Bug, Hundreds Behind: LLMs for Large-Scale Bug Discovery](https://proceedings.mlr.press/v306/wu26bk.html). *Proceedings of the 43rd International Conference on Machine Learning*, PMLR 306:137140–137154.
