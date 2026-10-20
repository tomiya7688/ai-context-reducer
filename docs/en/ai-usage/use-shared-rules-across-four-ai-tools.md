# Share repository rules across Claude Code, Codex, ChatGPT, and Copilot

> Japanese Source of Truth: [4つのAIで共通ルールを使う](../../jp/AI利用/4つのAIで共通ルールを使う.md)

Copying the same instructions into four AI-specific files creates inconsistencies and increases context when more than one copy is loaded.

**Keep the canonical rules in the root [AGENTS.md](../../../AGENTS.md).** Tool-specific files only provide the entry points. The common rules cover scope, Japanese/English documentation, verification, permissions, and reporting.

Before any substantive investigation or edits, follow the [shared task workflow](ai-task-workflow.md). In a new task with local Git, first check worktree safety, then **successfully run `git pull --ff-only origin main` on main**. In API-only environments such as some ChatGPT setups, verify the latest remote commit and do not claim to have executed git pull.

## How each environment accesses the rules

| Environment | Repository entry point | What to verify |
| --- | --- | --- |
| **Codex** | Root `AGENTS.md` | Confirm the instructions are loaded from the relevant directory. Configuration and working directory affect the scope. |
| **Claude Code** | `@AGENTS.md` in `CLAUDE.md` | The import loads the common file. Newer Claude Code versions can also use AGENTS.md directly; the import serves older versions or different settings. |
| **GitHub Copilot** | `.github/copilot-instructions.md`, and `AGENTS.md` in supported features | Support differs between IDE, cloud agent, and review. Keep only a short reference in the Copilot-specific file to avoid duplicating the rules. |
| **ChatGPT** | Explicitly retrieve `AGENTS.md` through a permitted GitHub connection, or attach it | Do not assume that ordinary chats or Projects automatically load repository instruction files. Explicitly request the file and verify access. |

Adding these files does **not** guarantee that every product or feature will load them. Consult the official sources below for differences across versions and settings.

## Using ChatGPT

In ChatGPT Project settings, you can place a project instruction such as:

```text
When working on repository tomiya7688/ai-context-reducer,
retrieve and read AGENTS.md from the repository root before editing.
Do not claim to have read a file that was not available.
If access is unavailable, explain the limitation and ask for the required text.
First follow the shared task workflow. If Git commands are unavailable,
check the latest remote SHA and task base; never claim to have pulled.
Check original sources and completion criteria for the current task separately.
```

This is a setup example, not a setting changed by the repository. If GitHub access is unavailable, attach the rules or supply the text in an accessible way. Avoid bringing unrelated conversations into a new task; see [Separate AI roles and chats by task](split-chats-by-task.md).

## Updating the rules

1. Decide whether a rule applies to all four environments. Place shared rules in `AGENTS.md` only; keep tool-specific operations in the appropriate adapter.
2. Do not copy common paragraphs into `CLAUDE.md`, `.github/copilot-instructions.md`, or ChatGPT Project settings.
3. Put lengthy, task-specific guidance in the [Method Index](../method-index.md) or the owning implementation guide rather than an always-loaded file.
4. Verify actual loading in each environment using a small read-only task that asks for the instruction file consulted and the scope of the check. Loading a file and consistently following every rule are separate outcomes.

## Troubleshooting

- **Claude Code:** Check the memory files with `/context`. The `@AGENTS.md` import is different from merely telling Claude to open a file. Newer Claude Code reads AGENTS.md directly when applicable, but project CLAUDE.md and settings affect precedence. See [official documentation][claude].
- **Codex:** Check AGENTS.md discovery from the working directory and confirm the applicable scope.
- **Copilot:** Check instruction support for your particular IDE and feature. The wrapper is intentionally short, even when AGENTS.md is also loaded.
- **ChatGPT:** A GitHub connection alone does not prove that this particular file was retrieved for the current task. If it is inaccessible, supply the text explicitly.

Instruction files are **not access-control mechanisms**. They do not grant permissions or replace approval settings. Prefer small task-specific references to repeatedly pasting long instructions or unrelated work histories.

## Sources

Official documentation checked October 20, 2026; behavior may change with versions and settings.

- [Claude Code: How Claude remembers your project][claude] — AGENTS.md, CLAUDE.md, imports, and precedence.
- [OpenAI Codex: Codex prompting guide][codex] — AGENTS.md discovery and instruction loading.
- [GitHub Copilot: Custom-instruction support][copilot] — feature-specific instruction support.
- [ChatGPT Projects][chatgpt] — project instructions and source files.
- [Connecting GitHub to ChatGPT][github] — searching and retrieving repository information.

[claude]: https://code.claude.com/docs/en/memory
[codex]: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
[copilot]: https://docs.github.com/en/copilot/reference/custom-instructions-support
[chatgpt]: https://help.openai.com/ja-jp/articles/10169521-projects-in-chatgpt
[github]: https://help.openai.com/ja-jp/articles/11145903-connecting-github-to-chatgpt
