# Assign AI roles and separate chats by task

> Japanese source: [作業ごとにAIの役割とチャットを分ける](../../jp/AI利用/作業ごとにAIの役割とチャットを分ける.md)

When you ask for comments or a review in a long implementation chat, discussions irrelevant to the new task remain in the conversation. Start by briefly stating the AI’s responsibility.

```text
You are the code reviewer.
Check the settings-save fix against its specification and diff.
Do not edit files. Report possible bugs with locations, triggering conditions, impact, and evidence.
State anything you have not inspected.
```

A role name alone does not specify what to check or return. Add the goal, target, permitted changes, review criteria, and required result. You can try this in an ordinary chat.

When conversations about other tasks grow long, open a new chat and provide only necessary information. Saying “now act as a reviewer” in the same chat does not remove earlier conversation from its input.

## Use a new chat for unrelated work

**Continuing one task** and **accumulating unrelated tasks in one chat** are different. Even if you select only a few source files per task, earlier conversations and tool results can enlarge the next model input when the application carries them forward.

Consider three **illustrative** tasks:

| Task | Everything in one chat | Separate chats |
| --- | --- | --- |
| ① Fix a settings-save bug | Adds the reproduction, failed runs, edits, and tests to the conversation | Keeps those details with the bug fix |
| ② Investigate a new data format | Earlier bug-fix discussion may still be included in later inputs | Starts with the research question, sources and constraints |
| ③ Improve public documentation | Previous implementation and research discussion may still remain | Provides the draft, target readers and writing rules |

**When the goal changes, reconsider which previous facts the new task needs.** Keep the same chat while investigating a failure whose earlier steps matter. For a separate research task, a new chat is often more appropriate. If the documentation depends on an implementation decision, hand over that decision and its source, not the entire history.

Saying “new task now” or “act as the documentation editor” in the same thread does not guarantee that earlier history is removed from the model's input. Check how the host application assembles context.

### Saved history, one-call input and cumulative usage are different

- **Visible saved history:** Messages you can scroll through. They are not necessarily all sent to the model on the next request.
- **Input for one model call:** Instructions, selected history, documents and tool results supplied on that request. Even “next” can accompany a long context.
- **Cumulative task usage:** Input and output over multiple calls. Repeatedly supplied history can be counted again in multiple requests.
- **Context window:** The amount of content a model can handle at one time. It is not the total of all requests in a task.

Applications may **summarize older exchanges, exclude earlier portions, or retrieve selected facts** rather than forwarding every visible message. Do not assume the whole displayed thread is always resent or that all past details remain available. See [What Is Context?](../llm-mechanics/what-is-context.md) for what is available in a call and [Context Amount, Computation, and Cost](../llm-mechanics/context-compute-and-cost.md) for usage accounting.

### Prompt caching does not remove old text from context

Some providers use **prompt caching** to reuse computed states for a matching prefix of instructions and earlier conversation. It can reduce processing work, latency or price under supported conditions. But **the reused content still belongs to the context the model can attend to**. Reusing computation is not the same as omitting past messages or increasing the context window.

The [OpenAI prompt caching documentation](https://developers.openai.com/api/docs/guides/prompt-caching) describes reusing matching prompt prefixes. Summarization or truncation may change a prefix and reduce cache reuse. Use provider usage fields to check cache reuse, and **do not add cached tokens a second time to the total input**.

A fresh chat can keep irrelevant earlier work out of the next task's context. It can also require duplicated shared instructions and sources or lose cache reuse. **Splitting does not guarantee lower total tokens or lower bills.**

### Handoff for a fresh chat

Instead of pasting a whole conversation, provide the smallest reliable handoff:

~~~text
Goal: Reflect the existing settings-save behavior in user documentation
Decision and reason: What changed and where the supporting decision is recorded
Constraints: Preserve the existing settings-file format
Original sources: Specification, code and exact revision or diff
Checks: Commands run, target revision, results and evidence locations
Open questions: Unresolved issues and unverified areas
Allowed work: Edit documentation only; do not edit program code
~~~

This is a template, **not evidence of completed work**. Verify the revision and sources before reusing conclusions. Some applications automatically attach project instructions, memory, or documents to a new chat; check what the model actually receives.

### Do not split tasks too finely

A bug investigation and its reproduction tests may belong together because their sequence matters. Starting an independent agent and writing a handoff for every tiny question can increase repeated input and coordination work.

When measuring whether chat splitting helps, use **equivalent completion criteria** and count all inputs, outputs, handoffs, retries, and separate chats. Savings achieved by omitting required specifications or tests are not a successful comparison. For measurement methods see [Build context-use estimates by task kind](estimate-context-use-by-task.md).

## Decide how much separation is useful

| Situation | Approach to try | Example criterion |
| --- | --- | --- |
| One question or short change | State the goal and response format in the same chat | Do not create three chats just to rename one function |
| Same purpose, different inspection criteria | Specify the role and criteria in the same chat | Check the changed diff against comment rules |
| Moving from implementation to review, with little need for earlier trial and error | Give a new chat the specification, diff, and check results | Exclude long rejected-option discussions; verify format compatibility |
| Repeating the same responsibility across tasks | Save a short reusable role instruction | Reuse review criteria; replace the target revision and diff each time |

If you are still narrowing a bug’s cause and the relationship with recent checks matters, you can continue in the same chat. When separating, carry forward necessary facts, including failing conditions and counterexamples.

Some environments automatically include shared memory, project instructions, or attachments in new chats. Check what carries over and whether required instructions and sources are actually accessible.

## Steps to use the method

### 1. Keep the task and shared conditions in one place

For a settings value that disappears after restarting, save the goal, preserved behavior, completion criteria, and references in, for example, `docs/tasks/settings-save/task.md`. An existing Issue can serve the same purpose. You can also use the [task-memo template](../../../templates/CONTEXT_PACK.md).

```markdown
# Settings-save fix
- Goal: Preserve saved values after restarting
- Preserve: Existing settings-file format
- Initial targets: Save and startup-loading code, with related tests
- Completion: Verify saving and reloading with the reproduction and related tests
- References: Issue reproduction, format specification, relevant code and tests
```

This is a fictional example. Replace references with actual paths, headings, and Issue numbers. Do not invent unresolved targets or conditions. Link to specifications and code where facts can be checked instead of copying entire specifications or long histories.

### 2. Give each chat its responsibility and scope

The following sequence handles implementation, comments, and review for one fix. You need not use all three chats; small comment changes can stay with implementation.

**Implementation chat**

```text
You are responsible for implementing the settings-save fix.
Read docs/tasks/settings-save/task.md and inspect the implementation and tests.
You may change save/loading code and related tests. Preserve the public file format.
If other changes are necessary, first report their targets and reasons.
Check the specified completion criteria. Return changes, checks and results, and unverified areas.
Write the handoff to docs/tasks/settings-save/handoff.md.
```

**Comment chat, after implementation finishes**

```text
You are responsible for reviewing code comments.
Read task.md and handoff.md, then inspect the changes at the recorded revision.
Limit edits to comments on declarations changed in this task.
The readers are developers maintaining this code.
Read the project’s comment rules and inspect the implementation and its users.
Explain necessary reasons, usage conditions, and constraints not apparent from code alone.
Edit comments only. Report behavior fixes without making them.
Append changed locations, evidence, checks and results, and unverified areas to handoff.md.
```

Both `task.md` and `handoff.md` above are in `docs/tasks/settings-save/`. See [writing useful comments](../methods/write-useful-code-comments.md) for detailed criteria.

**A new review chat, afterward**

```text
You are the code reviewer. Do not edit files.
Read docs/tasks/settings-save/task.md and handoff.md.
Confirm the target revision and comparison base for the diff.
Using the specification, diff, related code, and tests, check format compatibility,
state after save failures, loading after restart, and consistency between comments and code.
Read necessary original sources rather than relying on the implementer’s “verified” conclusion.
Report findings with severity, location, triggering conditions, impact, evidence, and a proposed fix.
State inspected scope, checks and results, and unverified areas.
If you find no issues, limit that conclusion to the inspected scope.
```

Role instructions do not enforce file permissions. If the environment supports a read-only setting, you can use it for review. Checks may generate or modify files, so agree on permitted operations as well.

### 3. Give the next chat a short handoff and necessary original sources

Have the AI record the following in `docs/tasks/settings-save/handoff.md`. This is a blank template, not a completed verification report.

With Git, a commit records a set of changes; its ID identifies a revision. Provide changes not yet recorded in Git separately as an uncommitted diff.

```markdown
# Settings-save handoff
- Goal and conditions: task.md
- Target revision: commit ID, or a file containing the uncommitted diff
- Comparison base: commit ID or equivalent
- Decisions and reasons used for this task: decision and evidence location
- Changes: paths, function names, and what changed
- Checks: target revision, commands or operations, results, and log locations
- Unresolved or unverified: what is unknown and what to check next
- Next task and permitted changes:
```

Update the target revision when comments or code change. A check that passed on an earlier revision is not a check of the latest revision. Include uncommitted changes in the handoff when they are in scope.

Provide the new chat with the task memo, handoff, target diff, and specifications or code needed for inspection. Give file paths to an AI that can read them; otherwise attach or paste the content. Supply necessary text when links are inaccessible too. Use a short entry point instead of the whole conversation, adding missing facts as needed.

For recurring roles, save instructions in, for example, `docs/ai/roles.md`. In an entry instruction the AI reads, say: “For review requests, read the review section of docs/ai/roles.md.” Confirm that the entry instruction actually loads; otherwise provide its path or text in the request. Keep task-specific revisions and history out of permanent role settings.

### 4. Compare the results and handoff yourself

- Compare actual diffs with the permitted change scope.
- Check review findings against the code revision, specification, and check results cited.
- Leave unavailable checks and unread sources explicitly unverified.
- After fixing findings, request the necessary checks for the changed revision.

Separate chats may repeat the same model error or accept an incorrect handoff. Agreement between chats is not completion evidence by itself. Use diffs and check results corresponding to the completion criteria.

## What decreases and what increases

Excluding implementation trial and error can remove conversation irrelevant to review from that review’s input. A short handoff can also avoid repeated explanations of conditions. Adding a role name alone does not reduce input.

However, repeated specification reads and handoff preparation or checking can increase total usage. Separation does not guarantee against forgotten information or missed issues. When usage is measurable, follow [task-level usage recording](estimate-context-use-by-task.md) and compare input, output, and retries across all chats while checking that required verification is preserved.

## Research on assigning roles

[Zheng et al. (2024)](https://aclanthology.org/2024.findings-emnlp.888/) evaluated personas including 162 roles on 2,410 factual questions selected from the MMLU knowledge-question evaluation dataset. Adding roles did not improve overall accuracy compared with the no-role condition. [1]

[Luz de Araujo et al. (2025)](https://aclanthology.org/2025.emnlp-main.1364/) evaluated nine models on 27 tasks. Expert roles commonly produced improvement or no significant difference, while irrelevant persona details also affected performance. [2]

These studies did not validate this guide’s chat separation or request examples. Effects vary by task and model. Rather than assuming an “expert” label improves quality, specify targets, criteria, and evidence, then inspect the results.

## Supporting tools and features

- **New-chat creation:** Starts a separate conversation per task. You can begin by manually supplying the necessary handoff. Check memory and attachment carryover settings.
- **Saved role instructions:** Reuses responsibilities and inspection criteria. Supply current targets and revisions with each request; do not turn role settings into a long work history.
- **Delegation to another AI agent:** Supported environments can run investigation or review in another conversation and return the result. Check supplied sources, editing permissions, and who integrates the output. Launching and transferring results differs from manually opening separate chats.

## About the methods

Assigning a responsibility at the start and specifying the goal, target, and expected result is **role prompting**. Assigning a character or persona is discussed as **persona prompting** in the references.

Assigning responsibilities to multiple AIs and exchanging their results is **multi-agent collaboration**. The [ChatDev paper](https://aclanthology.org/2024.acl-long.810/) describes connecting design, implementation, testing, and other phases through conversations between agents with roles. [3] Adopting such a system or running agents concurrently is not required to separate chats manually.

## References

1. Mingqian Zheng et al. (2024). [When “A Helpful Assistant” Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models](https://aclanthology.org/2024.findings-emnlp.888/). Findings of EMNLP 2024, pp. 15126–15154.
2. Pedro Henrique Luz de Araujo et al. (2025). [Principled Personas: Defining and Measuring the Intended Effects of Persona Prompting on Task Performance](https://aclanthology.org/2025.emnlp-main.1364/). EMNLP 2025, pp. 26857–26886.
3. Chen Qian et al. (2024). [ChatDev: Communicative Agents for Software Development](https://aclanthology.org/2024.acl-long.810/). ACL 2024, pp. 15174–15186.
