# Ask an AI to Improve How It Finds Project Information

> Japanese source of truth: [導入依頼文](../jp/導入依頼文.md)

Use this prompt when asking an AI to inspect a project and improve its guides so people do not repeatedly search for or reread the same information. It does not ask the AI to install every ai-context-reducer method or tool. The AI first inspects a small set of entry points, identifies real recurring effort, and adds only a guide that addresses it.

## Example: A small repository and a multi-app project

In a small project where the settings code and its tests are easy to find, a short note about where to start and which test to run may be enough. A code index or dedicated tool could take more time to maintain than the investigation it saves.

In a large project with Desktop and Web apps, people may have to rediscover the settings screen, storage code, and tests for each settings change. A table that maps change types to places to check, or separate instructions for each app, may help. Asking the AI to identify what is repeatedly being searched for first means it can add only the guide that reduces that work, without loading unrelated documents or instructions for another app.

## How to use the prompt

1. Open the target project and give the AI the prompt below.
2. The AI checks the specified entry points, the project overview, existing guides, tests, and build information.
3. It identifies information that people repeatedly have to find, then updates an existing guide or adds one small method.
4. It confirms that the guide leads to the relevant code and tests, and explains why it did not add other methods.

## Copyable prompt

```text
Improve this project so people do not have to repeat the same searches or reread the same information for each task. Adopt only the parts of the ai-context-reducer approach that this project needs.

Reference: https://github.com/tomiya7688/ai-context-reducer

Start by reading only these three references:
- the ai-context-reducer README
- docs/en/adoption-priority.md
- templates/AI_CONTEXT.md

For the target project, begin with the root structure, README, existing AI instructions, documentation headings, tests, and build or distribution configuration. Do not read every source file, document, or Issue from the beginning.

First identify what people repeatedly have to search for and which existing instructions are missing or out of date. Reuse existing AGENTS.md, CLAUDE.md, README, or docs when they can serve the purpose.

For a small project, stop after a short AI entry point and basic rules if those are sufficient. Add a table, index, or automation only when it reduces a repeated task in this project, and add methods incrementally. Do not add every method merely because it is part of the standard set.

After updating the guides, confirm that a reader can reach the relevant source code, tests, and authoritative specification from them. Check documentation links and any validation guidance you add. State uncertain information as unverified instead of presenting it as fact.

Report:
- Guides added or changed, and why
- Methods not adopted, and why
- Tests or checks performed
- Remaining unknowns
```

## Review the result

Judge the result by whether a person can follow the guide to the relevant code and tests, not by how many documents the AI read. A small project may need only one concise project-wide entry point. In a large project, tables and indexes must be updated when code or responsibilities move, or they will send people searching again.

For more detail on choosing methods, see [Adoption Priority](adoption-priority.md). Remove any prompt instructions that do not apply to the project's size or recurring problems.
