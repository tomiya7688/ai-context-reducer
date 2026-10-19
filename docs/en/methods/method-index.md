# Find a method by the problem you have
> Japanese version: [困りごとから手法を探す](../../jp/手法/困りごとから手法を探す.md)


This page is for people asking an AI to do work. Use it to find an explanation that matches a problem you are facing. You do not need to adopt every method. Start with the closest match.

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

- [Assign AI roles and separate chats by task](../ai-usage/split-chats-by-task.md) — specify responsibilities and permitted changes, then hand over necessary sources, diffs, and check results.

- [Summarize project capabilities and limitations](context-state.md) — give the AI a short note about which features work and what their limits are.
- [Write a short note for the current task](context-pack.md) — give the AI the goal, relevant documents, and conditions for this task.
- [Make a short list of where information lives](context-manifest.md) — give the AI a map of documents without copying all their contents.
- [Choose which files to read](context-priority.md) — direct it to files most relevant to the task.
- [Split long files and logs into parts for the AI](splitting-long-files-and-logs.md) — have the AI read content that does not fit at once in order and record ranges and evidence.
- [Decide what the AI usually does not need to read](context-exclusion.md) — identify logs and generated files to inspect only when needed.
- [Decide when the AI should stop investigating](exploration-control.md) — tell it when to stop once it has enough information to begin.
- [Before investigating, decide what checks can identify the cause](evidence-budget.md) — decide what to check and when to broaden the investigation.

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

## The goal or finish line is unclear

- [Give the AI decision reasons](share-decision-reasons.md) — keep decisions and reasons in one place and provide only records relevant to the task.

- [Set the goal and finish conditions before work](design-and-completion-criteria.md) — tell the AI what to change and how to know when the work is done.

## If this is your first time here

If you are unsure how much context a task may use, see [Build estimates by task kind](../ai-usage/estimate-context-use-by-task.md) to distinguish per-call input from cumulative task usage.

Start with [Basic steps for asking AI to work on a project](guide.md). If you are unsure which methods to adopt, see [Choose only the methods you need](../adoption/adoption-priority.md).

## Keep the guidance small

Start with one short project instruction file, such as `AGENTS.md`. Add folder-specific instructions only when people keep reading rules for unrelated areas. Use reusable skills only for procedures repeated across tasks. Keep shared rules in one place, link to details, and remove outdated examples. Each AI product loads instruction files and skills differently; include their paths or invocation names in your request when needed.
