# Method Index

> Japanese Source of Truth: [手法一覧](../jp/手法一覧.md)

This index helps project users choose a method for avoiding repeated searches. The user prepares a guide, list, or check that fits the problem, then tells the AI where it is and how to use it. An AI does not necessarily read project documents automatically. For recurring use, confirm that the guide is registered in an instruction file or setting the AI tool actually loads.

## Example: searching the repository for every settings change

Suppose each small settings change makes you search for which explanation, code, and tests to inspect.

A task routing guide can say: “For a settings change, check the settings documentation, the loading code, and the settings tests.” In the next request, tell the AI where the map is, have it select those three candidates, and ask it to check the original code and tests. This avoids giving it the whole repository just to find an entry point. Expand the scope if the map is stale or the change affects more than expected.

## Tell the AI to use the method, then check the result

For one task, say which guide to use, what it should return first, and how far it should check. For recurring work, put the guide link and its scope in project instructions that the AI actually reads. Whether folder-specific instructions load automatically depends on the AI tool's settings.

At completion, ask for the files consulted, checks run and their results, and anything not verified. Compare this report with the visible work log and diff. If read history is unavailable, a report alone cannot prove the actual context size. Check instead that the guide led to the right original sources and that necessary tests were not skipped. Compare token counts before and after only when the tool measures them.

## Methods

### Avoid rediscovering information for each task

| Method | What to do | Why it reduces reading |
|---|---|---|
| [Current State](context-state.md) | Briefly record current capabilities, constraints, and unfinished features | You do not need to compare the README, Issues, and change history every time to learn the current state |
| [Context Pack](context-pack.md) | Keep the current goal, references, change targets, and completion conditions together | You do not need to collect the task requirements from conversation and repository files each time |
| [Context Manifest](context-manifest.md) | List the locations of authoritative documentation, code, and tests | You do not need to search the whole repository by filename just to find candidates |
| [Task Routing](task-routing.md) | Name the documentation, code, and tests to inspect first for each kind of task | You do not need to rediscover the same starting points for recurring kinds of work |
| [Change Routing Map](change-routing-map.md) | Map change types such as settings or API changes to places to inspect | You can follow the likely effects from what changed |
| [Architecture Boundary Routing](architecture-boundary-routing.md) | Start from component responsibilities and communication paths already defined in the project | You do not need to read unrelated code to find the boundary of the affected feature |
| [Responsibility Map](responsibility-map.md) | Record what each file or module is responsible for | You do not need to open source files and guess their role from their names |
| [Hierarchical Context](hierarchical-context.md) | Put instructions needed in one location beside that location | You do not need to read detailed instructions for unrelated parts of the repository |
| [Remote Delta First](remote-context.md) | First inspect what changed remotely since the last known state | You can avoid rereading files that have not changed |

### Retrieve only the relevant parts of large material

| Method | What to do | Why it reduces reading |
|---|---|---|
| [Context Priority](context-priority.md) | Start with the changed behavior, its specification, and its tests; include consumers when changing an external format | You can skip unrelated features and start with the material needed to implement and check the change |
| [Context Exclusion](context-exclusion.md) | Record which generated output or caches to skip by default and when to read them | You do not need to repeat the same exclusions for every task, and relevant code and tests are easier to find |
| [Source Structure Index](source-structure-index.md) | Search functions, types, and dependencies in a form that can be queried | You can inspect relevant definitions and callers instead of reading a large source file from beginning to end |
| [Language-specific Analysis](language-tool-setup.md) | Choose the needed depth: locate code, inspect relationships, or verify a build or run | The AI receives relevant candidates and diagnostics instead of every source file and full log |

### Record decisions before implementation

| Method | What to do | Why it reduces reading |
|---|---|---|
| [Set Design and Completion Criteria First](design-and-completion-criteria.md) | Record the goal, scope, conditions to preserve, and completion criteria before implementation | Implementers do not need to reread past conversations or broad documentation to infer the design intent |

### Decide when to stop and what to verify

| Method | What to do | Why it reduces reading |
|---|---|---|
| [Exploration Control](exploration-control.md) | Decide in advance what it means to have enough information to make the decision | Once the needed evidence is checked, you can stop extra searches and rereads “just in case” |
| [Evidence Budget](evidence-budget.md) | List the evidence needed for the decision before collecting it | You do not need to keep gathering documents for a question that is already answered |
| [Validation Routing](validation-routing.md) | Choose required tests and checks based on the change | You do not need to look up validation procedures unrelated to the change |
| [Change / Test Impact Routing](change-impact-routing.md) | Find candidate tests from changed files and their dependencies | You do not need to read the full test list and consider unrelated tests |
| [Syntax Health Validation](syntax-health-validation.md) | If a parser is available, use it to check syntax before running tests | You can inspect reported errors instead of large lists of successful parse results. Passing syntax checks alone does not verify behavior |

### Consolidate repeated explanations and checks

| Method | What to do | Why it reduces reading |
|---|---|---|
| [Policy Routing](policy-routing.md) | Separate rules a machine can check from rules that need human judgment | You can inspect machine results and the relevant rules instead of reading every rule description |
| [Documentation Duplication Control](documentation-duplication-control.md) | Keep details in one authoritative document and link to it from other documents | You spend less time comparing duplicate explanations and checking whether they disagree |
| [Boilerplate Generation](boilerplate-generation.md) | Generate standard content such as license notices from canonical data | You do not need to reread examples and instructions to recreate text in the same format |

## Choose by the problem

- Unsure where to look each time: [Task Routing](task-routing.md), [Change Routing Map](change-routing-map.md)
- Unsure what should change or how to tell when it is complete: [Set Design and Completion Criteria First](design-and-completion-criteria.md)
- Unsure which parts of a large source file are relevant: [Context Priority](context-priority.md), [Source Structure Index](source-structure-index.md)
- Unsure how deeply to analyze or what check is needed: [Language-specific Analysis](language-tool-setup.md)
- Continuing to investigate after enough evidence is available: [Exploration Control](exploration-control.md), [Evidence Budget](evidence-budget.md)
- Searching for tests from scratch after each change: [Validation Routing](validation-routing.md), [Change / Test Impact Routing](change-impact-routing.md)
- Rereading long rules or duplicate explanations: [Hierarchical Context](hierarchical-context.md), [Policy Routing](policy-routing.md), [Documentation Duplication Control](documentation-duplication-control.md)

See [Adoption Priority](adoption-priority.md) to decide what to adopt first. Every method works without a dedicated tool. Only if you want to automate repeated searches or steps, choose an optional helper from the [method-to-tool map](tool-method-map.md) and check its README for instructions. These practices may be called context routing or context engineering, but first decide what the user prepares and what the AI receives.
