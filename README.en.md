# ai-context-reducer

[日本語](README.md) | English

This project helps people using AI choose the code and documents to provide for a task. It includes three kinds of resources:

- **Method guides** — ways to decide what the AI should read and how far it should investigate, with example requests.
- **Templates** — documents for writing project rules, project information, and notes for the current task.
- **Helper tools** — programs that help with file searches, task note generation, rule checks, and test selection.

You can start by giving example requests or completed templates to the AI you already use. Helper tools are also available when you want to spend less effort investigating, checking, or creating documents. Instructions, code, documents, search results, and check results provided to an AI for a task are called its **context**.

[Latest release](https://github.com/tomiya7688/ai-context-reducer/releases/latest) · [Try a helper tool in about five minutes](docs/en/adoption/getting-started.md) · [Method Index](docs/en/methods/method-index.md)

Published v1.0.0 supports Windows, Linux, and macOS on x64 and arm64. Its overview and suggestion commands do not require installing a language runtime.

## Example: Fix a saved setting that disappears after a restart

This is an illustrative example using a fictional app. Suppose you save a setting in the app's settings screen, but it resets when the app restarts.

```text
Ask the AI to read broadly
  Give it the whole project and ask it to investigate the cause
  → It also reads screen and feature code unrelated to settings

Limit what you ask the AI to read
  Ask it to search for the setting save code, startup loading code, and related tests
  → Have it read the relevant code, setting requirements, and tests
  → If another operation turns out to be involved, have it check that part too
```

Both approaches have the same goal: fix the app so the saved setting survives a restart. After the fix, save the same setting, restart the app, and check that it is retained.

Limiting the reading scope reduces the unrelated screen and feature code you provide. Have the AI read the setting requirements and related tests, and check the behavior after the change, so the work keeps the information needed to make and verify the fix.

## New here?

Start with [Getting started](docs/en/adoption/getting-started.md) to get a first result. Continue with the following guides if you want to understand the approach or adopt it in your project. You do not need to read every document.

1. [Three ways to limit what the AI reads](docs/en/methods/context-reduction-basics.md) — how to reduce irrelevant information
2. [Find a method by the problem you have](docs/en/methods/method-index.md) — a guide from common problems to explanations
3. [Choose only the methods you need](docs/en/adoption/adoption-priority.md) — how to decide which guidance or tools to add
4. [Ask AI to improve the project guide](docs/en/adoption/adoption-prompt.md) — a request you can give an AI to improve project guidance

## Start with these habits

- Tell the AI the goal, conditions to preserve, and how to know it is done.
- Search file names or contents before opening files, and start with relevant results.
- Keep detailed explanations in one place; link to them elsewhere and say when to read them.
- Broaden the search when important information is missing or shared code changes.
- Run checks that match the change, and report anything you could not check.

This lets the AI start work before reading unrelated files or long logs. Keep the documents and tests needed to confirm correctness; removing necessary information can lead to the wrong change.

## Find a guide by problem

Use this table to find guidance for problems you encounter when asking an AI to do work.

| Problem | Guide |
| --- | --- |
| Each time I ask for work, I am unsure what information to give the AI | [Tell the AI where to start for each kind of work](docs/en/methods/task-routing.md), [Guide work by the kind of change](docs/en/methods/change-routing-map.md) |
| I cannot decide what to ask the AI to change or how to judge completion | [Set the goal and finish conditions before work](docs/en/methods/design-and-completion-criteria.md) |
| I cannot find the parts of a large codebase related to my request | [Choose which files to read](docs/en/methods/context-priority.md), [Find functions and where they are used](docs/en/methods/source-structure-index.md) |
| I am unsure which method to use to inspect code | [Choose a language-appropriate method when analyzing code](docs/en/methods/analysis-depth-routing.md) |
| The AI's investigation drags on, and I cannot tell when to stop | [Decide when the AI should stop investigating](docs/en/methods/exploration-control.md), [Before investigating, decide what checks can identify the cause](docs/en/methods/evidence-budget.md) |
| I have to find tests again and cannot decide which checks to request | [Check a change in a way that matches what changed](docs/en/methods/validation-routing.md), [Decide which tests to run based on change impact](docs/en/methods/change-impact-routing.md) |
| I keep including long rules or duplicate explanations in my requests to the AI | [Give the AI instructions for the files it will change](docs/en/methods/hierarchical-context.md), [Check only the rules that apply to this task](docs/en/methods/policy-routing.md), [Avoid repeating the same explanation](docs/en/methods/documentation-duplication-control.md) |
| I repeatedly explain project rules or facts to the AI | [Templates for AGENTS.md, project context, and task notes](templates/README.md) |

You do not need every method. Add one only when it addresses a repeated problem and saves more search or checking time than it takes to maintain.

## Downloads and helper tools

Download files for Windows, Linux, and macOS from [GitHub Releases](https://github.com/tomiya7688/ai-context-reducer/releases). For each operating system, files are available for common processors and ARM processors. The downloads include helper programs that search files and code, and find relationships between code and tests. They help locate only the relevant parts to pass to the AI, avoiding unrelated code and long search results.

The `acr-toolbox` program combines several helpers. Run it from a command prompt to show its version, inspect code, or choose the next investigation or check. The [helper tool list](tools/README.md) explains what each tool can do and how to use it. You can also keep using search and check methods you already have.

Instructions for maintainers, such as how this repository packages and releases files, are under [docs/internal/](docs/internal/README.md). Users do not need to read them.

## Documentation

Japanese guides are under [docs/jp/](docs/jp/), with English versions under [docs/en/](docs/en/). The [document map](docs/DOCUMENT_MAP.json) records which pages are translations of each other.

## License

This repository is provided under the [MIT License](LICENSE), including its documents, designs, templates, and programs. External projects follow the terms set by their respective authors.
