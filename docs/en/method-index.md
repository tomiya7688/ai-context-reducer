# Method Index

> Japanese Source of Truth: [手法一覧](../jp/手法一覧.md)

This page is a plain-language index of methods for reducing how much an AI needs to read.

You do not need to memorize the names. What matters is **what each method does and what it prevents the AI from having to read**.

There are only three basics:

1. Let machines inspect what can be inspected mechanically before the AI reads it
2. Put repeated work into a procedure or tool
3. Make the AI read only the necessary part

## Index

| Method | What it does | Why it reduces context |
|---|---|---|
| [Current State](context-state.md) | Keep a short document describing current capabilities, constraints, and unimplemented items | The AI does not need to reread README, Issues, and history to reconstruct current state |
| [Context Pack](context-pack.md) | Put only the current goal, required references, change targets, and completion conditions in one place | The AI does not need to rediscover required information across the repository at the start of every task |
| [Context Manifest](context-manifest.md) | Keep a small pointer-oriented candidate list of original source / tests / docs | The AI does not need to broadly reread the repository just to find candidates |
| [Context Priority](context-priority.md) | Put task relevance first and use size, churn, and similar signals only to choose routing granularity | Unrelated large files stay unread, while relevant large files can be narrowed before a full read |
| [Context Exclusion](context-exclusion.md) | Keep generated output, logs, vendor, cache, history, and similar material out by default and restore it only when a task needs it | The AI avoids large amounts of derived or auxiliary information on every task |
| [Task Routing](task-routing.md) | Define which documents, source, and tests to read for each kind of work | The AI does not need to search unrelated directories and documents one by one |
| [Exploration Control](exploration-control.md) | Define when to stop searching once necessary information is available | Prevents continued searches and rereads "just in case" |
| [Evidence Budget](evidence-budget.md) | Decide required evidence first and search only for what is missing | Prevents collecting more material after enough evidence already exists |
| [Change Routing Map](change-routing-map.md) | Map change types such as configuration or API changes to the places to inspect | Related source / tests / docs do not need to be rediscovered for every change |
| [Architecture Boundary Routing](architecture-boundary-routing.md) | Use responsibility boundaries and official communication paths already defined by the project to choose the initial read scope | Avoids broad reading of unrelated subsystems to rediscover boundaries |
| [Hierarchical Context](hierarchical-context.md) | Put rules near the directory where they apply | The AI does not need to read detailed rules for the entire repository every time |
| [Validation Routing](validation-routing.md) | Select only the tests and checks required by the change | The AI does not need to reconsider every possible test and validation procedure each time |
| [Syntax Health Validation](syntax-health-validation.md) | Use an already available parser to check syntax health first, then proceed to required tests / compiler / runtime validation | Obvious syntax errors are found cheaply without reading parse trees or large lists of successful files |
| [Change / Test Impact Routing](change-impact-routing.md) | Mechanically narrow affected tests from changed files and dependencies | The AI does not need to read large unrelated test sets |
| [Responsibility Map](responsibility-map.md) | Briefly record what each file or module owns | The AI does not need to open source just to infer responsibilities from filenames |
| [Policy Routing](policy-routing.md) | Separate mechanically checkable rules from rules requiring semantic review | The AI can inspect only necessary policy instead of reading the full policy every time |
| [Documentation Duplication Control](documentation-duplication-control.md) | Keep detailed specifications in one authoritative source and use short explanations + pointers elsewhere | Reduces repeated reading of the same explanation and update drift across documents |
| [Remote Delta First](remote-context.md) | Inspect only what changed on the remote since the previous state first | Avoids rereading the whole repository |
| [Source Structure Index](source-structure-index.md) | Mechanically index functions, types, imports, and dependencies in a searchable form | Large source files can be narrowed to necessary functions and relationships instead of read end to end |
| [Boilerplate Generation](boilerplate-generation.md) | Generate repeated license, NOTICE, header, and similar files from canonical data | The AI does not need examples and writing instructions every time or regenerate the same text |

## If you want a more concrete starting point

### I want only the information needed for the current task

- [Current State](context-state.md) — quickly understand where the project is now.
- [Context Pack](context-pack.md) — keep only information needed for the current work in one place.
- [Context Manifest](context-manifest.md) — make a bounded pointer-oriented list of candidate original sources, then choose the working set.
- [Context Exclusion](context-exclusion.md) — exclude generated / logs / vendor / cache / history by default and restore only what is needed.
- [Task Routing](task-routing.md) — decide where to look first from the work type.
- [Exploration Control](exploration-control.md) — stop searching when enough information is available.
- [Evidence Budget](evidence-budget.md) — search only for missing information.

### I want to know only where to make the change

- [Change Routing Map](change-routing-map.md) — narrow source / tests / docs from the type of change.
- [Architecture Boundary Routing](architecture-boundary-routing.md) — narrow the initial working set from responsibility boundaries already defined by the project.
- [Responsibility Map](responsibility-map.md) — see what each file owns.
- [Hierarchical Context](hierarchical-context.md) — read only instructions needed in the current directory.
- [Remote Delta First](remote-context.md) — inspect only changes made by other people or AIs first.

### I do not want the AI to read all of a large codebase

- [Context Priority](context-priority.md) — prioritize task relevance and route large files to slice / symbol-level inspection when needed.
- [Source Structure Index](source-structure-index.md) — mechanically inspect functions, types, and dependencies first, then read only necessary locations.

### I want only the necessary validation

- [Validation Routing](validation-routing.md) — select required checks from the type of change.
- [Syntax Health Validation](syntax-health-validation.md) — use a parser as cheap validation only when already available; syntax success alone does not complete the task.
- [Change / Test Impact Routing](change-impact-routing.md) — select only tests related to the change as candidates.

### I do not want the AI to repeat the same explanations or work

- [Documentation Duplication Control](documentation-duplication-control.md) — keep details in one authoritative source and use short explanations + pointers elsewhere.
- [Policy Routing](policy-routing.md) — let machines check rules that can be checked mechanically.
- [Boilerplate Generation](boilerplate-generation.md) — generate repeated text and files.

## Which methods should I use?

You do not need all of them.

Choose from the problem you actually have.

```text
I keep wondering where to look
  -> Task Routing / Change Routing Map

Architecture boundaries are clear, but the initial read scope is still broad
  -> Architecture Boundary Routing

I keep reading large source files
  -> Source Structure Index

Search continues even after enough information is available
  -> Exploration Control / Evidence Budget

I keep checking every test
  -> Validation Routing / Change-Test Impact Routing

I keep reading long rules
  -> Hierarchical Context / Policy Routing
```

If you are unsure whether to adopt something, see [Adoption Priority](adoption-priority.md).

The v1.1 tool guide will describe what each tool actually executes.
