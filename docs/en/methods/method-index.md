# Find a method for your problem

> Japanese source: [困りごとから手法を探す](../../jp/手法/困りごとから手法を探す.md)

When you ask an AI to investigate or change code, **choose the problem closest to yours from the list below.** Each linked guide explains what to ask the AI to do and what evidence you should check. You do not need to adopt every method.

To use a guide, tell the AI the task and the location of the page you chose. The AI may not load it automatically. If your AI cannot open project files, provide the relevant passage yourself.

For questions such as “the later parts of the AI's output are vague” or “which model should I use,” start with the [AI usage FAQ](../ai-usage/faq.md).

## You are unsure what to change or read

- [Write a README for people and AI](write-readme-for-people-and-ai.md) — organize getting-started guidance and sources to supply to the AI.

- [Inspect existing code before adding similar responsibilities](reuse-existing-code-before-adding.md) — inspect definitions, users, and tests before choosing reuse, extension, or a new component.
- [Tell the AI where to start for each kind of work](task-routing.md) — tell the AI which documents or code to read first for this kind of work.
- [Guide work by the kind of change](change-routing-map.md) — direct the AI to settings or code affected by changes to how another program uses it.
- [Find which files handle what](responsibility-map.md) — see which area is responsible for what.
- [Find functions and where they are used](source-structure-index.md) — use functions and callers to narrow what you ask the AI to read.
- [Choose a language-appropriate method when analyzing code](analysis-depth-routing.md) — choose between search, code relationships, language-specific checks, and running the app based on what you need to know.
- [Give the AI instructions for the files it will change](hierarchical-context.md) — have the AI read only the rules that apply to the target folder.
- [Get shared changes before starting work](remote-context.md) — check changed files, then apply only the updates you need.
- [Use feature areas to choose what code to read](architecture-boundary-routing.md) — use the existing code layout and data flows to direct the AI to a starting point.

## The AI is reading unrelated material

- [Assign AI roles and separate chats by task](../ai-usage/split-chats-by-task.md) — when unrelated research, implementation, and writing accumulate in one chat, explain why cache reuse does not remove history, when to split, and what evidence to hand over.

- [Summarize project capabilities and limitations](context-state.md) — give the AI a short note about which features work and what their limits are.
- [Write a short note for the current task](context-pack.md) — give the AI the goal, relevant documents, and conditions for this task.
- [Make a short list of where information lives](context-manifest.md) — give the AI a map of documents without copying all their contents.
- [Choose which files to read](context-priority.md) — direct it to files most relevant to the task.
- [Split long files and logs into parts for the AI](splitting-long-files-and-logs.md) — have the AI read content that does not fit at once in order and record ranges and evidence.
- [Give the AI only the relevant parts of a web page](retrieve-relevant-webpage-information.md) — select evidence from large amounts of text or tables by task, keep source references, and retrieve more if needed.
- [Decide what the AI usually does not need to read](context-exclusion.md) — identify logs and generated files to inspect only when needed.
- [Decide when the AI should stop investigating](exploration-control.md) — tell it when to stop once it has enough information to begin.
- [Before investigating, decide what checks can identify the cause](evidence-budget.md) — decide what to check and when to broaden the investigation.

- [Diagnose repeated context from work logs](diagnose-repeated-context-from-work-logs.md) — find information that was passed repeatedly and retries in the record, then change one thing at a time and compare quality, usage, and rework.
- [Estimate context use by task](../ai-usage/estimate-context-use-by-task.md) — separate a single input from the accumulated total, fix the measurement conditions, and record a guideline. See the [measured benchmark](../ai-usage/measured-context-reduction-benchmark.md) for a measured example.
- [Shorten investigation with external tools](shorten-investigation-with-external-tools.md) — leave searching and analysis to existing dedicated tools and give the AI only the places this task needs.
- [Use tools without extra installs](use-tools-without-extra-installs.md) — choose from environments and distributed tools you already have, instead of requiring a new runtime.

## You repeat the same steps or checks

- [Assign responsibilities and edit boundaries to multiple AI agents](assign-agent-edit-ownership.md) — separate edit ownership and have the coordinator integrate and check the combined result.

- [Advance one listed task per signal](run-one-task-per-signal.md) — provide the list, priorities, scope, and stop conditions, then request one ready task with “next.”

- [Find the same problem from one example](find-same-problems-from-one-example.md) — derive criteria from an example, exclusions, and scope, then confirm other candidates before fixing them.
- [Have the AI write code comments that help readers](write-useful-code-comments.md) — provide comment rules and readers, then check usage conditions and reasons against the diff and evidence.
- [Have the AI read coding rules and check its changes](follow-coding-rules.md) — provide naming and reuse rules, then check compliance using existing checks and the changed diff.
- [Check a change in a way that matches what changed](validation-routing.md) — select tests and other checks that fit the change.
- [Decide which tests to run based on change impact](change-impact-routing.md) — identify which tests are related and should be run.
- [Start by checking code syntax](syntax-health-validation.md) — use a quick syntax check to catch obvious errors.
- [Check only the rules that apply to this task](policy-routing.md) — separate rules a tool can check from rules a person must judge.
- [Avoid repeating the same explanation](documentation-duplication-control.md) — keep detailed explanations in one place and link to them.
- [Create repeated documents and settings from a template](boilerplate-generation.md) — create standard text or files automatically.

## You keep asking follow-up questions about AI explanations

- [Give the AI document headings and their order](write-from-document-outline.md) — save a short outline, then provide section requirements and factual sources to the AI.
- [Make explanations understandable to their readers](make-explanations-understandable.md) — specify the reader and have the AI revise only unclear objects, actors, or actions. Use the [follow-up question comparison](make-explanations-understandable.md#compare-follow-up-questions-before-and-after) to check whether the revision does more than lengthen the text.

- [Compare design options with project evidence](compare-design-options-with-project-evidence.md) — compare candidates by the same criteria and recommend one from evidence in specifications, code, settings, and tests.

## The goal or finish line is unclear

- [Give the AI decision reasons](share-decision-reasons.md) — keep decisions and reasons in one place and provide only records relevant to the task.

- [Set the goal and finish conditions before work](design-and-completion-criteria.md) — tell the AI what to change and how to know when the work is done.

## If you are new to this project

If you are asking an AI to change code for the first time, read [Basic steps for an AI development task](guide.md). To decide what information to give the AI, read [Three ways to limit what the AI reads](context-reduction-basics.md). To choose which method to adopt, see [Choose only the methods you need](../adoption/adoption-priority.md).

To understand the model first, see [What Is an LLM?](../llm-mechanics/what-is-an-llm.md). To choose a coding agent, see [Coding agents](../ai-usage/coding-agent-overview.md). To record usage by task, see [Estimate context use by task](../ai-usage/estimate-context-use-by-task.md).

## Ask the AI to apply a method

Tell the AI what you want to accomplish and which guide to use. If it can open the page, ask it to read the relevant part. Otherwise, paste that passage into your request.

**Example message for you to send to the AI:**

```text
Task: [What needs to be done]
Use the method explained in [the guide you selected].
First list the candidate code, requirements and tests, and why they are relevant.
Verify the original sources before making changes.
Report the diff, actual checks and results, and anything not checked.
```

When the work finishes, **inspect the actual changes and check results yourself.** The AI saying “verified” does not prove it opened the right sources or ran the tests. If your service provides usage measurements, compare equivalent tasks without omitting necessary evidence.

You can start without installing extra tools. For optional tools that you or an agent can run, see the [method-to-tool map](tool-method-map.md).

## Avoid unnecessary permanent instructions

If you repeatedly give the AI the same rules, you can record shared rules and document locations in a file the AI actually reads. Keep folder-specific instructions limited to work in those folders. AI products differ in when and how they load instruction files, so verify your tool's settings and provide an explicit path if needed.
