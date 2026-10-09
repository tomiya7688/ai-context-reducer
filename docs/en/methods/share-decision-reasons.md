# Give the AI the reasons behind specification and implementation decisions

“Save settings on the device” alone does not tell the AI whether a different storage method is acceptable. “We chose device storage so settings remain usable without a connection or account” lets it check the conditions that still matter for the current task.

Current behavior visible in code and the historical reason for choosing that behavior are different facts. Record reasons with the decision, then have the AI read only records relevant to the current work.

Japanese version: [仕様や実装を決めた理由をAIに渡す](../../jp/手法/仕様や実装を決めた理由をAIに渡す.md).

## Decide when to use it

- **Changing storage or interactions with other systems**: Provide reasons supporting the current choice, such as offline use or compatibility with existing data.
- **Replacing an existing implementation**: Have the AI check why timing or structure was chosen, such as loading once at startup.
- **Repeatedly investigating the same decision**: Point to its recorded reasons instead of supplying earlier conversations and history each time.

For a typo correction unaffected by design rationale, there is no need to load all design records. Start with one decision related to the behavior being changed or conditions being preserved.

## 1. Separate purpose, decision, reasons, and evidence

This example uses a fictional settings feature. Replace it with actual decisions and verifiable material in your project.

| Record | Example |
|---|---|
| Purpose | Use the user's selected language at the next startup |
| Chosen specification or implementation | Save the selected language in a settings file on the device and load it at startup |
| Conditions to preserve | Works offline; does not require an account |
| Reason for choosing it | Server storage would depend on a connection or account, so device storage was selected |
| Evidence location | The specification section requiring offline use and the Issue passage adopting this option |
| Status and confirmation date | Confirmed / [date the decision was confirmed] |
| Consequences and limitations | Does not include automatic transfer of settings to another device |

Separate reasons for storage location from reasons for loading timing, even within one feature. For example, “Load at startup because the display language must be known before constructing the screens” explains an implementation timing decision. Record the evidence confirming that reason as well.

Recording decisions, reasons, assumptions, and status is also discussed in [Tyree and Akerman's paper](https://personal.utdallas.edu/~chung/SA/zz-Impreso-architecture_decisions-tyree-05.pdf). This guide simplifies those fields for passing relevant decisions to an AI. [1]

A storage format appearing in source code does not establish the historical claim that it was selected for offline use. If an AI organizes possible reasons, mark explanations as unverified unless supported by a record from the time or confirmation from the decision maker.

## 2. Decide where to keep lasting reasons and task-specific reasons

| Content | Location | How to pass it to the AI |
|---|---|---|
| Reasons that remain useful across tasks | The relevant section of an existing design document, or a separate decision such as `docs/decisions/settings-storage.md` | Specify the relevant file and heading in the request |
| Entry point to reasons from project information | `PROJECT_CONTEXT.md` copied from the [project information template](../../../templates/PROJECT_CONTEXT.en.md) | Include references and reading conditions, not duplicate reason text |
| Current task's reasoning or pointers to applicable decisions | `CONTEXT_PACK.md` copied from the [task memo template](../../../templates/CONTEXT_PACK.md), or the current request | Provide a short reason, status, and evidence location |

Use the existing design section if it already explains the reason. There is no need for another decision document. Duplicated reasons can diverge when updated. If a task-specific decision becomes lasting guidance, confirm it as the requester, move it into the design document, and retain a reference in the task memo.

For a new record, save the following in a file such as `docs/decisions/settings-storage.md`. Field names and paths are examples.

```text
# Language setting storage
Status: [confirmed / proposed / unverified / current applicability needs checking]
Confirmation date: [date]
Decision confirmation record or person: [relevant Issue passage, etc.]

Purpose:
Chosen specification or implementation:
Conditions to preserve:
Reasons for the decision:
Evidence for the reasons: [material path and heading, decision record]
Consequences and limitations:
Conditions for reconsidering this decision:
```

## 3. Explicitly ask the AI to read the applicable reasons

Saving a document does not mean the AI read it. For an AI with file access, specify the path and heading. In a chat without file access, attach or paste the relevant section. Provide the decision, reasons, status, and necessary evidence passages rather than entire previous conversations or change histories.

```text
Goal: Save the language selected in settings and restore it at the next startup.
Read: docs/decisions/settings-storage.md, “Language setting storage.”
Applicable decision: Device storage that does not depend on a connection or account.

Read the chosen specification, reasons, status, and evidence before making changes.
Check current behavior against the relevant code and tests.
If reasons are missing, ask instead of inferring historical intent from code.
Do not treat proposed or unverified reasons as settled conditions.
If the rationale's assumptions conflict with current specifications, report the
conflicting passages and required clarification before proceeding with changes
that depend on that decision.
Briefly report decision references, conditions preserved, checks performed,
and anything unverified at completion.
```

For repeated use, put “When changing settings storage, read the relevant section of `docs/decisions/settings-storage.md`” in an instruction file the AI actually reads. For an AI supporting `AGENTS.md`, use the file applicable to the work location. If instructions do not load automatically, specify the reference in each request.

## 4. Have the AI check status and current applicability

- **Confirmed**: A decision record or confirming person is identifiable. Have the AI check whether its assumptions still match current specifications.
- **Proposed**: An option awaiting adoption. Do not have the AI implement it as an already adopted condition.
- **Unverified**: An explanation without supporting records. Keep it as a question for the requester rather than letting the AI fill it in as fact.
- **Possibly outdated**: A previously confirmed decision whose environment or requirements changed. Retain its date and mark “confirmed at the time; current applicability needs checking.”

When a reason is unknown, also have the AI explain which current decision needs it. Do not keep searching for reasons irrelevant to this task. When changing an existing decision, confirm the new reasons, evidence, and status, and make the new record reachable from the old decision.

## Why it can reduce reading in conversation

Providing the relevant decision location and reasons can reduce broad reading of conversations and history to infer design intent. Keeping details in one place also reduces comparison of duplicate explanations in project information and task memos.

Creating and maintaining records takes work. Supplying many unrelated decisions for a small change increases reading. Check whether repeated investigation and questions about reasons decreased; do not claim a reduction in information processed without measurement.

## Helper tools

- [context-pack-builder](https://github.com/tomiya7688/ai-context-reducer/blob/main/tools/common/medium/context-pack-builder/README.md) — Generates a task memo from the goal, conditions, and Git state. It can provide a starting memo to pass with the request. It does not establish historical decision reasons automatically; verify and add reason and evidence references.

## About this method

Explicitly recording a chosen design, its reasons, assumptions, and status is discussed as **architecture decisions** in Tyree and Akerman's paper. [1] This guide adds a procedure for directing an AI to those records. The paper does not evaluate this request example or a reduction in information processed in AI conversations.

## References

1. Jeff Tyree, Art Akerman. 2005. [Architecture Decisions: Demystifying Architecture](https://personal.utdallas.edu/~chung/SA/zz-Impreso-architecture_decisions-tyree-05.pdf). *IEEE Software*, 22(2):19–27. DOI: [10.1109/MS.2005.27](https://doi.org/10.1109/MS.2005.27).
