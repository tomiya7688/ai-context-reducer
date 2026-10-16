# Coding agents: types and how to choose

**Last checked: October 16, 2026.** This guide covers more than Codex, Claude Code, and Grok Build. It is not a ranking. Product capabilities, pricing, and availability change; verify current details in each linked official source.

## What is a coding agent?

A coding agent supplies task-relevant code, requirements, and tests to an AI model and uses tools for file search, edits, commands, and verification. **Allowed actions and required approvals vary by product and configuration.**

| Distinction | Role | Examples |
| --- | --- | --- |
| AI model | Generates text or code and helps decide next actions | GPT, Claude, Gemini, and Grok models |
| Coding agent | Supplies context to models and operates file, command, and test tools | Codex, Claude Code, Grok Build, Gemini CLI |
| Working environment | Determines where code is handled and commands run | Developer device, IDE, cloud virtual environment |

**Using a Grok model inside Cursor is different from using the Grok Build coding agent.** Also, using a terminal does not guarantee that model inference happens locally. Check where code is stored, what is sent to models, and where commands execute.

## Main products

The categories describe **common entry points**, not mutually exclusive capabilities. Summaries are based on official provider materials.

### Terminal-first entry points

| Product | Main workflow | Official source |
| --- | --- | --- |
| **Codex (OpenAI)** | Searches, edits and runs commands via CLI/IDE; also offers app and cloud workflows. | [Official](https://github.com/openai/codex) |
| **Claude Code (Anthropic)** | Multi-file edits and verification through terminal, IDE, desktop and web interfaces. | [Official](https://code.claude.com/docs/en/overview) |
| **Grok Build (xAI)** | Terminal and headless coding agent, distinct from the Grok model family. | [Official](https://docs.x.ai/build/overview) |
| **Gemini CLI (Google)** | Terminal agent with file, shell and search tools. | [Official](https://github.com/google-gemini/gemini-cli) |
| **OpenCode** | Open-source agent for terminal, desktop and IDE, with configurable model providers. | [Official](https://opencode.ai/docs/) |
| **Aider** | Terminal AI pair programming with Git integration. | [Official](https://github.com/Aider-AI/aider) |
| **goose** | General-purpose desktop and terminal agent that also handles coding. | [Official](https://github.com/aaif-goose/goose) |
| **Amp** | Terminal and cloud environments that can continue work across sessions. | [Official](https://ampcode.com/docs) |

### Editor-centered workflows

| Product | Main workflow | Official source |
| --- | --- | --- |
| **Cursor Agent** | Code search, editing and command execution in Cursor, plus cloud agents. | [Official](https://cursor.com/docs/agent/overview) |
| **Cline** | Open-source agent for editor and terminal coding workflows. | [Official](https://cline.bot/) |
| **Kilo Code** | IDE/CLI agent with modes for planning, investigation and implementation. | [Official](https://kilo.ai/docs/getting-started) |
| **Junie (JetBrains)** | Coding agent in JetBrains IDEs and terminal workflows. | [Official](https://junie.jetbrains.com/docs/) |
| **Kiro** | IDE/CLI workflows that can organize requirements, design and tasks. | [Official](https://kiro.dev/docs/ide/) |

### Delegated GitHub and cloud workflows

| Product | Main workflow | Official source |
| --- | --- | --- |
| **GitHub Copilot** | IDE agent mode and delegated cloud work from GitHub issues. | [Official](https://docs.github.com/en/copilot/concepts/agent-capabilities/about-agents) |
| **Jules (Google)** | Connects GitHub repositories and works on code in a cloud virtual machine. | [Official](https://jules.google/docs/) |
| **Devin (Cognition)** | Delegates code investigation, edits, commands and tests in the cloud. | [Official](https://docs.devin.ai/get-started/devin-intro) |
| **OpenHands** | Development-agent platform with browser UI, cloud services and an SDK. | [Official](https://docs.openhands.dev/overview/introduction) |
| **Replit Agent** | Browser-based environment focused on building apps and websites. | [Official](https://replit.com/products/agent) |

**Outdated product references:** The former **Roo Code** [officially announced that its products would shut down on May 15, 2026](https://github.com/RooCodeInc/Roo-Code-Docs/blob/main/docs/sunset.md). Do not treat historical comparison articles as a current adoption guide.

## Choose what fits the task

| Question | What to consider |
| --- | --- |
| Working interface | Start from a terminal or editor, or delegate a GitHub issue? |
| Work scope | A single edit or a multi-file investigation with commands and tests? |
| Permissions | Can you review file writes, shell commands, network access and external actions? |
| Model and data | Which models, credentials, endpoints and local inference options are used? |
| Evidence and verification | Can you inspect diffs, sources, actual commands, tests and unverified areas? |
| Usage costs | Check current subscriptions, request limits and token-based billing. |

Begin with a small **read-only** request to check what the agent can inspect.

```text
Find the code responsible for loading settings and its related tests.
Report candidate file paths, why you selected them, and any unexamined areas.
Do not edit files or make changes in external services yet.
```

After checking the candidates, have the agent inspect the source, requirements and tests, then perform the change and verification. Do not rely only on its claim that a test was run; inspect the diff and actual result.

## Using ObaPick methods

ObaPick does not require a specific agent. It focuses on choosing task-relevant code and documents while keeping the evidence needed for correct work.

- [Context Reduction Basics](../context-reduction-basics.md) — what to omit and preserve.
- [Context Priority](../context-priority.md) — finding relevant code and tests.
- [AI Usage FAQ](faq.md) — choosing models and editing workflows.

Whether an agent reads `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or other instruction files automatically depends on the product and configuration. **Simply adding ObaPick documents does not guarantee that an agent reads them.** Name the required documents explicitly.

## Keeping this list current

Prefer official provider sources, check discontinued products, and do not publish unsupported rankings such as "most capable" or "cheapest." For new entries, describe the work surface, allowed operations, permissions, and official link.
