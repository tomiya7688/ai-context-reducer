# Assign responsibilities and edit boundaries to multiple AI agents

> Japanese Source of Truth: [複数のAIに担当と編集範囲を分けて頼む](../../jp/手法/複数のAIに担当と編集範囲を分けて頼む.md)

Before asking multiple AI agents to work at the same time, decide who owns each task and which files each may change. Give each agent the sources and completion criteria for its assignment, then have a coordinator collect the changes and check the combined result. These assignments help avoid agents independently changing the same place or working without knowing about another agent's changes.

## Example: revise two separate documentation pages

Suppose you want to add usage examples to the CSV import and image export documentation. Shared terminology and the feature specifications are already settled, so neither revision needs the other's result. The paths and assignments below are fictional.

| Owner | Task and completion criteria | Files permitted for editing | Workspace and starting condition |
| --- | --- | --- | --- |
| AI-A | Write a CSV import example; check it against the specification and actual operations | `docs/csv.md` | A's dedicated folder; start after checking shared conditions |
| AI-B | Write an image export example; check it against the specification and actual operations | `docs/image-export.md` | B's dedicated folder; start after checking shared conditions |
| Coordinator | Maintain assignments, integrate both changes, update the index, and check the combined result | `docs/tasks/parallel.md`, `docs/README.md` | Integration folder; update the index after checking both results |

You can coordinate this yourself, sending the A and B assignments to separate chats. A chat without file-editing access can return a proposed change and its evidence; you apply each proposal in turn. A dedicated feature for launching multiple agents is not required.

Give A and B the shared goal, required terminology, reference revision, and each other's boundaries. They do not need each other's entire conversations or unrelated sources. When either notices an index change is needed, it reports the proposed link to the coordinator rather than editing the index.

## 1. Check whether the tasks can run independently

The coordinator writes down each task's required inputs and expected result. Ask whether it can be performed and checked independently using settled specifications before the other task is finished.

| Combination of tasks | How to divide the work |
| --- | --- |
| Inspect separate documents and return evidence-backed findings | Divide the investigation using the same criteria; leave writes to shared documents to the coordinator |
| Change files for two unrelated features | Work concurrently only when shared configuration and generated output do not overlap either, and each task can be checked separately |
| Change an implementation and review its diff | Begin review after a revision is available to inspect; the reviewer reports findings without making fixes |
| Specify an interface other code calls (API), then implement its users | Settle the specification first; do not let agents independently guess an undecided interface |
| Make a few-line fix or repeatedly discuss changes to the same function | Keep one owner rather than adding handoffs |

Different filenames do not prove independence. Check input and output rules when changes use the same configuration format, shared function, or test data. Start dependent work only after the prerequisite result is verified and available in the revision the next owner will use. Translating Japanese text after its wording is settled is another example of this ordering.

## 2. Give each edit target one owner

Save the example table and shared conditions in, for example, `docs/tasks/parallel.md`. An existing Issue or task note can serve this purpose. Choose one person or AI to maintain it, recording task ID, goal, targets, completion criteria, prerequisites, workspace, and state. Each worker returns its result; the coordinator updates the table.

Edit targets include not just prose and code, but tests, indexes, translation maps, dependency records, generated files, and result output locations. Define what this assignment needs rather than allowing every change under an assigned folder. Reading and editing are separate permissions: a worker may need to read a shared specification while returning proposed changes to its owner.

For example, if A and B both rewrite `docs/README.md` in a shared folder, one may erase the other's additions. Separate folders still leave overlapping changes or inconsistent heading and ordering decisions to resolve during integration. Separate branches alone do not finish the coordination work.

Instead, let only the coordinator edit the index, or give B the verified revision containing A's work and edit sequentially. Even different lines of one file can overlap after whole-file formatting or heading changes, so this guide avoids concurrent editing of that file.

When a task needs a wider edit boundary, pause that change and report the reason and target to the coordinator. Before transferring ownership, confirm that the previous owner has stopped editing and preserved outstanding changes; then update the table and the next assignment. A lack of response is not evidence that an agent has stopped.

For recurring use, add a reference in entry instructions the AI reads: “When working with multiple agents, read docs/tasks/parallel.md and check your task-ID row and shared conditions.” Check whether files such as `AGENTS.md` load automatically; otherwise include the table path in the request. Reading the table does not grant permission to edit it.

## 3. Separate working files and shared mutable state

With Git, record the common starting point using a commit identifier. A commit records a set of changes, and its identifier names a revision. A branch is a separate line of recorded changes from a starting revision. Give each owner a separate branch starting from that revision and a separate folder where it actually edits files.

Creating two branch names does not isolate work when agents switch branches in the same shared folder. When the environment supports separate workspaces, verify the folder and branch each agent actually uses before starting.

Without Git, you can still put the same source revision in separate folders, keeping the starting material distinct from proposed changes. For chat-only work, fix the attached material being reviewed and use separate response destinations. Separate chats do not necessarily mean separate editable files.

Separate folders do not isolate every operation. Working folders attached to the same Git repository can share configuration, for example. [5] Give test databases, output destinations, shared configuration, and writes to external services separate targets, or perform those operations sequentially. Put resources that cannot be separated under one owner.

A request saying “do not edit outside this scope” is not a technical permission boundary. Use read-only or scoped permissions where available. Adding workers does not authorize publishing, deletion, environment configuration changes, or other additional actions.

## 4. Give each owner a goal, targets, and required report

The following is a template for A. Replace bracketed values with actual ones. Specify existing checking procedures and expected results instead of asking the agent to guess commands.

```text
You own task A: add a CSV import usage example.
The assignment table and shared conditions are in docs/tasks/parallel.md.
Follow its references to the relevant specification paths and sections.
The starting revision is [commit identifier or attached-material revision].
Your workspace is [A's dedicated folder], on branch [A's branch].
You may edit only docs/csv.md, not the index or shared configuration.
AI-B owns docs/image-export.md; the coordinator owns the index and assignment table.

First verify your workspace, revision, and edit targets.
Read the specification and usage procedure, then add example input, operations,
and expected results to the page.
Check the result using [existing procedure and expected results].
If another file must change or an undecided specification needs a decision,
pause that part and report the needed change, evidence, and decision to the coordinator.
Do not change another owner's files, branch, or work state.

Return starting and result revisions, changed locations, checks and results,
evidence locations, and anything unverified or blocked.
Return the report in this conversation; do not write directly to the shared assignment table.
Do not start another task without the coordinator's request.
```

Attach the task note and necessary text when the AI cannot read files. Without editing access, change the instruction to “return a proposed change.” See [Assign AI roles and separate chats by task](../ai-usage/split-chats-by-task.md) for role and handoff details.

For each worker's report, use a template such as the following. These are blank fields, not verified results.

```markdown
- Task ID and owner:
- Starting revision, result revision, and workspace:
- Files changed and what changed:
- Result for each completion criterion:
- Checks performed: revision, commands or operations, expected and actual results, log locations
- Unverified, unresolved, or blocked items:
- Proposed changes to shared files:
- State: working / individually checked, awaiting integration / awaiting checks / stopped
```

## 5. Integrate one result at a time and verify the whole

After receiving successful reports, the coordinator collects changes and check results, then checks overall completion criteria against the combined revision.

1. **Fix the revision being received.** Record the result commit or saved diff, and prevent workers from modifying that deliverable during integration. Compare the report with the actual changed files and check for out-of-scope changes and unverified items.
2. **Integrate in a recorded order.** In the integration workspace, incorporate prerequisite changes first, one at a time. For independent A and B above, record an order such as A followed by B. The coordinator updates the shared index after both are included.
3. **Resolve overlaps and inconsistent assumptions.** Do not mechanically overwrite one side of overlapping changes. Inspect both diffs and the specification, pausing the affected integration if the conflict cannot be resolved. Check compatibility with any changes made to the integration target since work began.
4. **Check the combined revision.** For documentation, check headings, terminology, links, and consistency of examples. For code, check combined behavior as well as related tests and the project's mandatory checks. After a correction, rerun the necessary checks on that revision.
5. **Update the state.** Report overall completion criteria, checked revision, results, and unverified areas. Use “awaiting checks” when a required check remains, or “stopped” when a specification decision is pending; individual success does not establish overall completion.

For a separate reviewer, provide the fixed integration diff, specification, and checking results. Ask for findings, not edits. Send fixes back to the editing owner and review the revised result again. Run checks that modify files in a separate checking workspace.

Distinguish “working,” “individually checked, awaiting integration,” and “combined result checked” in the assignment table. Do not delete failing checks or replace another worker's results without review. Proposing, integrating, and publishing changes remain separate operations under the existing permissions and procedures.

## What can decrease, and what can increase

Narrow assignments can avoid giving each AI the entire discussion and source material for other tasks. Independent investigations may also reduce elapsed waiting time when performed concurrently. However, repeated reading of shared sources, task division, reporting, integration, and rechecking consume input and output too.

This method is not always faster, cheaper, or more accurate. Keep small or strongly dependent work sequential. When comparing approaches, record usage across all workers and the coordinator, elapsed time, rework, and remaining defects under the same completion criteria. See [Build context-use estimates by task kind](../ai-usage/estimate-context-use-by-task.md).

For sequential work, use [Advance one listed task per signal](run-one-task-per-signal.md). This guide instead covers edit ownership and integration when tasks run concurrently.

## Supporting tools and features

- **[OpenAI Multi-agent](https://developers.openai.com/api/docs/guides/agents-api/multi-agent):** Delegates independent work to other agents and combines results. It can help divide investigations. Agents sharing environment files still need coordinated edit targets. [1]
- **[GitHub Copilot Fleet mode](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/fleet-mode):** A coordinator dispatches tasks and collects states and results. It can help divide investigations or documentation updates; the coordinator checks the integrated result. [3]
- **[GitHub Copilot app workspace selection](https://docs.github.com/en/copilot/how-tos/github-copilot-app/agent-sessions):** Offers separate working trees or execution environments for sessions. It can separate edit locations. Verify actual folders and permissions before starting. [4]
- **[Git worktree](https://git-scm.com/docs/git-worktree):** Creates multiple working folders attached to one repository, with different branches checked out. It can separate edit locations. Some settings remain shared; external services and output destinations are not automatically isolated. [5]

## About the method

Assigning separate responsibilities to multiple AIs and combining their results is **multi-agent collaboration**.

A coordinator assigning work and managing progress and integration is sometimes called an **orchestrator** in product documentation. Along with the role name, specify assignments, task scope, and how results are received.

## References

The following official sources were checked on October 17, 2026. They cover independent delegation, shared edit targets, and combined verification. [1][3] They also recommend comparing overall quality, time, and usage because multiple agents can increase consumption. [2] This guide's assignment table and requests are operational examples, not measurements of their effectiveness.

1. OpenAI. [Multi-agent](https://developers.openai.com/api/docs/guides/agents-api/multi-agent) — independent delegation and handling short or dependent steps.
2. OpenAI. [API deployment checklist](https://developers.openai.com/api/docs/guides/deployment-checklist#use-multi-agent-for-parallel-work) — avoiding shared mutable targets and checking usage, quality, and latency.
3. GitHub. [Fleet mode](https://docs.github.com/en/copilot/how-tos/copilot-sdk/features/fleet-mode) — ownership, dependencies, reporting, and combined verification.
4. GitHub. [Working with agent sessions in the GitHub Copilot app](https://docs.github.com/en/copilot/how-tos/github-copilot-app/agent-sessions) — choosing working trees and execution environments.
5. Git. [git-worktree](https://git-scm.com/docs/git-worktree) — multiple working folders and shared elements such as configuration.
