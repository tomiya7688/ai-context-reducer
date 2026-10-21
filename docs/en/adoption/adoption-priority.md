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

## When it is worth adding a method

Add a method when the effort it repeatedly saves outweighs the cost of introducing and maintaining it. Judge by whether the amount read and the time spent searching actually went down while accuracy and needed checks were kept.

For example, if you spend 12 minutes finding the target for the same kind of task and do it 8 times a month, that is about 96 minutes of searching. If writing an entry guide takes 30 minutes, updating it takes 10 minutes a month, and each search then takes 3 minutes, the monthly work is about 34 minutes, so the method pays off even after maintenance. For a one-time task where the search takes 12 minutes, there is no need to spend 30 minutes building a dedicated index. These numbers only show how to calculate; they are not a pass mark. Estimate from the searches and time you actually repeated recently and the effort of keeping the method up to date.

Size is not the only factor. If several people or AIs update the same repository, consider a step to check what changed since your last check, plus a short shared note of each task's goal and scope.

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

See [Find a method by the problem you have](../methods/method-index.md) for the methods, and the [method and helper tool map](../methods/tool-method-map.md) for the matching helper tools. This procedure is called **Method Adoption / method selection**.

## How to judge the benefit

For repeated questions about explanations, use the [before-and-after question comparison](../methods/make-explanations-understandable.md#compare-follow-up-questions-before-and-after). Record candidate questions separately from actual repeated explanations; fewer questions do not count as improvement if operations or conditions are incorrect.

Count how often the problem occurs and how long the search or check takes. Compare the time saved, unrelated material no longer sent to the AI, and any checks that might be missed. If the benefit is unclear, start with one short guide instead of a large system.
