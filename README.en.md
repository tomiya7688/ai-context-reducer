# ai-context-reducer

English | [日本語](README.md)

## Give an AI the information it needs to do the work

For example, when fixing an error message for a settings file, giving an AI the whole project makes it search through unrelated code such as screens and logs. If you first find the settings loader and its related tests, then provide the relevant parts, you reduce search time and the amount the AI needs to read.

Instructions, explanations, source code, and test results provided to an AI for a task are called its **context** here. This repository describes ways to keep the evidence needed for a task while reducing information that is unlikely to help.

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

Start with the [Adoption Prompt](docs/en/adoption-prompt.md) to review the existing guides and work procedures. Pick one recurring problem and begin with a method that addresses it. After adoption, check whether it is easier to reach the needed code and tests, and whether any necessary checks were missed.

## Downloads

Helper tool releases are available from [GitHub Releases](https://github.com/tomiya7688/ai-context-reducer/releases). See [Releasing](docs/en/releasing.md) for supported environments, archive contents, and verification. You can also use the documentation ideas without installing any tools.

## Documentation

Japanese documents are under [`docs/jp/`](docs/jp/), with English versions under [`docs/en/`](docs/en/). This README does not repeat the details of every method; follow the [Method Index](docs/en/method-index.md) to reach each guide.

This repository is provided under the [MIT License](LICENSE). External projects and content remain subject to the licenses from their respective distributors.
