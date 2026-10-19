# Choose only the methods you need
> Japanese version: [必要な方法だけ選ぶ](../../jp/導入/必要な方法だけ選ぶ.md)


You do not need to add every guide or tool to a project. Start with a few basic habits. When the same problem keeps happening, add one method that addresses it.

Choose based on problems that actually occur, not on project size.

## Start with these basics

- Give the AI a short first-read guide, such as a root `AGENTS.md` or equivalent, that links to details.
- Use a reusable skill only for a procedure repeated across tasks; keep one-off steps in the task request.
- Search by file name or contents before opening files.
- Set the task goal and decide how to tell when it is done.
- Point to the document that defines the requirements; check actual behavior in code or tests.
- Keep unrelated changes out of the task.
- Run relevant tests and report anything you could not check.
- Inspect logs and generated files only when needed.

For a small project, these basics may be enough.

## Add a method when the same problem keeps happening

| Problem | Method to add |
| --- | --- |
| You keep looking up what works and what is limited | [Summarize project capabilities and limitations](../methods/context-state.md) |
| You keep searching for the documents or code needed for each task | [Tell the AI where to start for each kind of work](../methods/task-routing.md) |
| There are many possible documents and files to search | [Make a short list of where information lives](../methods/context-manifest.md) |
| File names do not show what each area handles | [Find which files handle what](../methods/responsibility-map.md) |
| I keep giving the AI instructions for unrelated apps | [Give the AI instructions for the files it will change](../methods/hierarchical-context.md) |
| I keep asking the AI to read files unrelated to the task | [Choose which files to read](../methods/context-priority.md) |
| I cannot tell the AI when to stop searching | [Decide when the AI should stop investigating](../methods/exploration-control.md) |
| It is unclear what must be checked to identify the cause | [Before investigating, decide what checks can identify the cause](../methods/evidence-budget.md) |
| Several people work at once and local files may be out of date | [Get shared changes before starting work](../methods/remote-context.md) |
| Different changes need different checks | [Check a change in a way that matches what changed](../methods/validation-routing.md) |
| There are too many tests to know which relate to a change | [Decide which tests to run based on change impact](../methods/change-impact-routing.md) |
| The same explanations appear in several documents | [Avoid repeating the same explanation](../methods/documentation-duplication-control.md) |
| Repeatedly asking about the same content because AI explanations are unclear | [Make explanations understandable to their readers](../methods/make-explanations-understandable.md) |

## Methods for particular kinds of projects

| Project characteristic | Useful method |
| --- | --- |
| Large codebase or long files | [Find functions and where they are used](../methods/source-structure-index.md), [Choose which files to read](../methods/context-priority.md) |
| Screen-based app or game that must be run to check | First do the checks that do not need the screen, then visually check only what matters |
| Saving, conversion, or packaging creates extra files | Try it in a temporary folder and check the files that will actually be delivered or saved |
| Results depend on time, random values, or network access | Fix the time or inputs so the same conditions can be checked again |

## Why start with problems that keep happening

Adding only guidance that addresses a real problem keeps the AI from reading extra instructions and lists on every task. For example, if all tests in a small project finish in seconds, running them all may be simpler than maintaining a test-selection map. If there are many tests and each run produces long logs, a map that points to tests related to the change can help.

## Wait for evidence before adding these

- A large code index that takes substantial work to update
- A complex system that summarizes information in many stages
- Large numbers of AI-specific instruction files
- Large indexes or automation for a small project

Do not add a method if setting it up and maintaining it costs more than the repeated work it saves.

## When asking AI to help adopt a method

1. Check the README and existing guides; do not make the AI read every project file first.
2. Identify one problem that actually keeps happening.
3. Choose the smallest method that addresses that problem.
4. Before adding a new document, see if a short addition to an existing guide will work.
5. Give the AI the new guide and ask it to find the relevant code and checks; confirm it can follow them.
6. Briefly report what was added and what was skipped, with reasons.

Choose methods that solve real problems, not ones that only seem useful for a possible future need.

## How to judge the benefit

For repeated questions about explanations, use the [before-and-after question comparison](../methods/make-explanations-understandable.md#compare-follow-up-questions-before-and-after). Record candidate questions separately from actual repeated explanations; fewer questions do not count as improvement if operations or conditions are incorrect.

Count how often the problem occurs and how long the search or check takes. Compare the time saved, unrelated material no longer sent to the AI, and any checks that might be missed. If the benefit is unclear, start with one short guide instead of a large system.
