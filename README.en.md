# ObaPick

<img src="assets/obapick-mascot.png" alt="ObaPick mascot" width="128" height="128" />

**Give AI only the context it needs.**

English | [日本語](README.md)

This project helps people using AI choose the code and documents to provide for a task. It includes four kinds of resources:

- **LLM mechanics** — foundational guides explaining tokens, Transformers, generation, training, code generation, and how those mechanics connect to context design.
- **Method guides** — ways to decide what the AI should read and how far it should investigate, with example requests.
- **Templates** — documents for writing project rules, project information, and notes for the current task.
- **Helper tools** — programs that help with file searches, task note generation, rule checks, and test selection.

You can start by giving example requests or completed templates to the AI you already use. Helper tools are also available when you want to spend less effort investigating, checking, or creating documents. Instructions, code, documents, search results, and check results provided to an AI for a task are called its **context**.

[Latest release](https://github.com/tomiya7688/ai-context-reducer/releases/latest) · [AI usage FAQ](docs/en/ai-usage/faq.md) · [Coding agents guide](docs/en/ai-usage/coding-agent-overview.md) · [Shared rules for four AI tools](docs/en/ai-usage/use-shared-rules-across-four-ai-tools.md) · [AI task workflow](docs/en/ai-usage/ai-task-workflow.md) · [Try a helper tool in about five minutes](docs/en/adoption/getting-started.md) · [Method Index](docs/en/method-index.md)

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

This is a fixed-fixture measurement, not a universal reduction rate or an actual LLM input-token measurement. The fixture, search conditions, script, and reference result are committed so the [Measured Context-Reduction Benchmark](docs/en/measured-context-reduction-benchmark.md) can be reproduced.

## Where to start

Choose the path that matches your goal. You do not need to read every document.

1. **Learn how LLMs work**: Start with [What Is an LLM?](docs/en/llm-mechanics/what-is-an-llm.md), then follow the guides through tokens, Transformers, Attention, training, code generation, and context use.
2. **Learn the methods**: Read [Context Reduction Basics](docs/en/context-reduction-basics.md) for the overview, then choose one relevant guide from the [Method Index](docs/en/method-index.md). For a first code change, start with [Context Priority](docs/en/context-priority.md).
3. **Apply them to your project**: Use [Adoption Priority](docs/en/adoption-priority.md) to choose a recurring problem, then use the [Adoption Prompt](docs/en/adoption-prompt.md) to review the existing guides and procedures. Use the [AI_CONTEXT.md template](templates/AI_CONTEXT.md) to draft a short entry, then put it in an instruction file the active AI tool actually reads (such as `AGENTS.md` if supported).
4. **Use a helper tool**: Choose a method first, then follow the [method-to-tool map](docs/en/tool-method-map.md) to a tool guide only if automation would help. Tools are optional.

To use a method, attach its guide to the request or tell the AI its path. It may not load the guide automatically; for recurring use, register it in instructions or settings that your AI tool actually reads.

### Start from a question about context

- What is supplied, and why is it needed? [What Is Context?](docs/en/llm-mechanics/what-is-context.md)
- Why can equal call counts produce different usage and costs? [Context Amount, Computation, and Cost](docs/en/llm-mechanics/context-compute-and-cost.md)
- What are the benefits beyond savings, and the risks of removing too much? [Context Amount and Use](docs/en/llm-mechanics/context-amount-and-use.md)

## Three ways to narrow the information

### 1. Use a program to find mechanical facts first

Search or analysis can find file names, function names, and references to other files, then narrow the candidates related to a change. This avoids asking the AI to read large amounts of code just to build a list and helps it reach the implementation it needs sooner. After narrowing the candidates, read the original code to understand its design and behavior.

### 2. Package steps that are repeated

If the same steps are repeated to find the changed code and its tests, put them in a short guide or helper tool. The next task does not need to reinvent the search process. Do not build a system for one-time work or when maintaining it would take more effort than it saves.

### 3. Read only the relevant parts

After locating the change, read the parts of the implementation, explanation, and tests needed for the task. This avoids reading everything, while keeping the evidence needed for decisions and verification. Return to the original material when checking the result.

See [Context Reduction Basics](docs/en/context-reduction-basics.md) for a detailed explanation of these three methods.

## What this repository contains

The main content is documentation and templates for guiding work and narrowing the information to read. It also has tools that help with tasks such as searching, creating indexes, and selecting checks. No tool is necessary for every project.

- Start from a concrete problem asking an AI for help: [AI usage FAQ](docs/en/ai-usage/faq.md)
- Learn the model mechanics behind context design: [What Is an LLM?](docs/en/llm-mechanics/what-is-an-llm.md)
- See the fixed-fixture context measurement: [Measured benchmark](docs/en/measured-context-reduction-benchmark.md)
- Find a method from the problem you have: [Method Index](docs/en/method-index.md)
- Decide what to adopt in a project: [Adoption Priority](docs/en/adoption-priority.md)
- Ask an AI to inspect an existing project: [Adoption Prompt](docs/en/adoption-prompt.md)
- Template for a short AI entry guide: [AI_CONTEXT.md](templates/AI_CONTEXT.md)
- Helper tool documentation: [tools/README.md](tools/README.md)

## Try it in an existing project

Start with [Adoption Priority](docs/en/adoption-priority.md) to pick one recurring problem, then use the [Adoption Prompt](docs/en/adoption-prompt.md) to review the existing guides and work procedures. After adoption, check whether it is easier to reach the needed code and tests, and whether any necessary checks were missed.

## Tell the AI to use a method

For one task, attach the selected method guide or name its path in the request, then adapt its example to your task. For recurring work, put a link and its scope in project instructions the AI actually reads. Which files load automatically depends on the AI tool, so check its settings.

For example, to narrow the files and tests for a settings change, ask:

```text
The goal is to show why loading a setting failed.
First list candidate locations for the settings loader and its related test, with paths and reasons.
Check the selected original code and test, then make the needed change and run the test.
At the end, report files read, checks run and results, and anything not verified.
```

The benefit is that unrelated files are not sent to the AI, reducing that input. Compare reported files, commands, and results with the diff or visible work log. If the environment has no read history or token measurement, do not claim a measured reduction; check that investigation was narrowed without omitting the required code or tests.

## Downloads

Helper tool releases are available from [GitHub Releases](https://github.com/tomiya7688/ai-context-reducer/releases). See [Releasing](docs/en/releasing.md) for supported environments, archive contents, and verification. You can also use the documentation ideas without installing any tools.

## Documentation

Japanese documents are under [`docs/jp/`](docs/jp/), with English versions under [`docs/en/`](docs/en/). LLM foundations are separated under [`docs/en/llm-mechanics/`](docs/en/llm-mechanics/), while practical workflows remain in the [Method Index](docs/en/method-index.md) and method guides.

The documentation and code in this repository are provided under the [MIT License](LICENSE). The mascot image ([assets/obapick-mascot.png](assets/obapick-mascot.png)) is separately subject to the [Tomiya Character License v1.0.1](https://github.com/tomiya7688/Tomiya_character_license/blob/main/LICENSE). See [mascot asset terms](assets/README.md). External projects and content remain subject to the licenses from their respective distributors.
