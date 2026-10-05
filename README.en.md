# ai-context-reducer

English | [日本語](README.md)

## Give an AI the information it needs to do the work

For example, when fixing an error message for a settings file, giving an AI the whole project makes it search through unrelated code such as screens and logs. If you first find the settings loader and its related tests, then provide the relevant parts, you reduce search time and the amount the AI needs to read.

Instructions, explanations, source code, and test results provided to an AI for a task are called its **context** here. This repository describes ways to keep the evidence needed for a task while reducing information that is unlikely to help.

## Where to start

Choose the path that matches your goal. You do not need to read every document.

1. **Learn the methods**: Read [Context Reduction Basics](docs/en/context-reduction-basics.md) for the overview, then choose one relevant guide from the [Method Index](docs/en/method-index.md). For a first code change, start with [Context Priority](docs/en/context-priority.md).
2. **Apply them to your project**: Use [Adoption Priority](docs/en/adoption-priority.md) to choose a recurring problem, then use the [Adoption Prompt](docs/en/adoption-prompt.md) to review the existing guides and procedures. Link only the methods you decide to reuse from [AI_CONTEXT.md](templates/AI_CONTEXT.md), if useful.
3. **Use a helper tool**: Choose a method first, then follow the [method-to-tool map](docs/en/tool-method-map.md) to a tool guide only if automation would help. Tools are optional.

To use a method, attach its guide to the request or tell the AI its path. It may not load the guide automatically; for recurring use, register it in instructions or settings that your AI tool actually reads.

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

Japanese documents are under [`docs/jp/`](docs/jp/), with English versions under [`docs/en/`](docs/en/). This README does not repeat the details of every method; follow the [Method Index](docs/en/method-index.md) to reach each guide.

This repository is provided under the [MIT License](LICENSE). External projects and content remain subject to the licenses from their respective distributors.
