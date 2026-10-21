# ObaPick

<img src="assets/obapick-mascot.png" alt="ObaPick mascot" width="128" height="128" />

**Give AI only the context it needs.**

[日本語](README.md) | English

This project helps people using AI choose the code and documents to provide for a task. It includes four kinds of resources:

- **LLM mechanics** — foundational guides explaining tokens, Transformers, generation, training, code generation, and how those mechanics connect to context design.
- **Method guides** — ways to decide what the AI should read and how far it should investigate, with example requests.
- **Templates** — documents for writing project rules, project information, and notes for the current task.
- **Helper tools** — programs that help with file searches, task note generation, rule checks, and test selection.

You can start by giving example requests or completed templates to the AI you already use. Helper tools are also available when you want to spend less effort investigating, checking, or creating documents. Instructions, code, documents, search results, and check results provided to an AI for a task are called its **context**.

[Latest release](https://github.com/tomiya7688/ai-context-reducer/releases/latest) · [AI usage FAQ](docs/en/ai-usage/faq.md) · [Coding agents guide](docs/en/ai-usage/coding-agent-overview.md) · [Try a helper tool in about five minutes](docs/en/adoption/getting-started.md) · [Method Index](docs/en/methods/method-index.md)

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

## Reproducible measured example

A fixed synthetic repository compares three tasks under two strategies: send all 15 eligible files to AI context, or run a literal search first and send only the 3 matching files. All predefined required evidence remains present in all three tasks, while the total AI-visible character count falls from 14,478 to 3,543, a **75.5% reduction**.

This is a fixed-fixture measurement, not a universal reduction rate or an actual LLM input-token measurement. The fixture, search conditions, script, and reference result are committed so the [Measured Context-Reduction Benchmark](docs/en/ai-usage/measured-context-reduction-benchmark.md) can be reproduced.

## New here?

Start with [Getting started](docs/en/adoption/getting-started.md) to get a first result. Continue with the following guides if you want to understand the approach or adopt it in your project. You do not need to read every document.

1. [Three ways to limit what the AI reads](docs/en/methods/context-reduction-basics.md) — how to reduce irrelevant information
2. [Find a method by the problem you have](docs/en/methods/method-index.md) — a guide from common problems to explanations
3. [Choose only the methods you need](docs/en/adoption/adoption-priority.md) — how to decide which guidance or tools to add
4. [Ask AI to improve the project guide](docs/en/adoption/adoption-prompt.md) — a request you can give an AI to improve project guidance

To learn how LLMs work, start with [What Is an LLM?](docs/en/llm-mechanics/what-is-an-llm.md) and follow the guides through tokens, Transformers, Attention, training, code generation, and context use. If you want to use a helper tool, choose a method first, then follow the [method-to-tool map](docs/en/methods/tool-method-map.md) to a tool guide only if automation would help. Tools are optional.

To use a method, attach its guide to the request or tell the AI its path. It may not load the guide automatically; for recurring use, register it in instructions or settings that your AI tool actually reads.

### Start from a question about context

- What is supplied, and why is it needed? [What Is Context?](docs/en/llm-mechanics/what-is-context.md)
- Why can equal call counts produce different usage and costs? [Context Amount, Computation, and Cost](docs/en/llm-mechanics/context-compute-and-cost.md)
- What are the benefits beyond savings, and the risks of removing too much? [Context Amount and Use](docs/en/llm-mechanics/context-amount-and-use.md)

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
| I have a concrete problem asking an AI for help | [AI usage FAQ](docs/en/ai-usage/faq.md), [Coding agents guide](docs/en/ai-usage/coding-agent-overview.md) |
| I want to choose among several design options for this project | [Compare design options with project evidence](docs/en/methods/compare-design-options-with-project-evidence.md) |
| I want to find why AI usage keeps growing and improve it | [Diagnose repeated context from work logs](docs/en/methods/diagnose-repeated-context-from-work-logs.md), [Estimate context use by task](docs/en/ai-usage/estimate-context-use-by-task.md) |
| I repeatedly explain project rules or facts to the AI | [Templates for AGENTS.md, project context, and task notes](templates/README.md) |

You do not need every method. Add one only when it addresses a repeated problem and saves more search or checking time than it takes to maintain.

## Downloads and helper tools

Download files for Windows, Linux, and macOS from [GitHub Releases](https://github.com/tomiya7688/ai-context-reducer/releases). For each operating system, files are available for common processors and ARM processors. The downloads include helper programs that search files and code, and find relationships between code and tests. They help locate only the relevant parts to pass to the AI, avoiding unrelated code and long search results.

The `acr-toolbox` program combines several helpers. Run it from a command prompt to show its version, inspect code, or choose the next investigation or check. The [helper tool list](tools/README.md) explains what each tool can do and how to use it. You can also keep using search and check methods you already have.

Instructions for maintainers, such as how this repository packages and releases files, are under [docs/internal/](docs/internal/README.md). Users do not need to read them.

## Documentation

Japanese guides are under [docs/jp/](docs/jp/), with English versions under [docs/en/](docs/en/). LLM foundations are under [docs/en/llm-mechanics/](docs/en/llm-mechanics/), while practical workflows are in the [Method Index](docs/en/methods/method-index.md) and the method guides. The [document map](docs/DOCUMENT_MAP.json) records which pages are translations of each other.

## License

This repository is provided under the [MIT License](LICENSE), including its documents, designs, templates, and programs. The mascot image ([assets/obapick-mascot.png](assets/obapick-mascot.png)) is separately subject to the [Tomiya Character License v1.0.1](https://github.com/tomiya7688/Tomiya_character_license/blob/main/LICENSE). See [mascot asset terms](assets/README.md). External projects and content remain subject to the licenses from their respective distributors.
