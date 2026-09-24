# Adoption Prompt

> Japanese Source of Truth: [導入依頼文](../jp/導入依頼文.md)

This document is an entry point for asking Codex, Claude Code, ChatGPT, or a similar agent to adopt `ai-context-reducer` while keeping the initial context small.

For detailed adoption criteria, see [Adaptive Adoption](adoption-priority.md).

## Recommended prompt

```text
Adopt the following ai-context-reducer approach in this project:
https://github.com/tomiya7688/ai-context-reducer

Do not install everything by default.
First read only the ai-context-reducer README, docs/en/adoption-priority.md, and templates/AI_CONTEXT.md as entry points, then begin with a shallow inspection of the target project.

Briefly classify the target project by size, documentation volume, issue volume, concurrent AI/remote editing, GUI/interactive behavior, nondeterminism, generated artifacts, policy volume, and similar signals. Then choose only the methods with high expected value.

Required core:
- a small AI entry point / AI_CONTEXT
- Search first, read second
- stop exploration when Goal / Required / Acceptance are known
- identify the Source of Truth
- do not mix unrelated refactors into the current task
- targeted validation and explicit Unverified areas

Add other methods only when the conditions in adoption-priority.md apply.
Do not unconditionally read the whole repository, all documentation, or all Issues.
Preserve and reuse existing AGENTS.md / CLAUDE.md / README / docs structures when appropriate.

After adoption, report only:
- Adopted
- Skipped
- Why
```

## Expected adoption flow for an AI

```text
1. Read only the three ai-context-reducer entry files
2. Shallow-inspect the target repository
3. Classify project signals
4. Adopt A Core
5. Add only high-value B / C methods
6. Verify that the AI entry point leads to source / tests / source of truth
7. Report Adopted / Skipped / Why
```

Initial inspection of the target repository should begin with the root structure, README, existing AI instructions, documentation names/headings, tests, and build/package metadata.

## For a small project

For a small repository, it is acceptable to stop after adding an `AI_CONTEXT.md` equivalent and the core rules.

Do not add Task Routing, Source Structure Index, Responsibility Map, or dedicated tools merely because they are part of the standard set.

## For a large project

If reaching the target area repeatedly requires broad exploration, add Responsibility Map, Task / Change Routing, Current State, Source Structure Index, split Context Pack, and similar methods incrementally.

If multiple AIs, chats, or developers update the same remote, prioritize Remote Delta First regardless of repository size.

## Do not

- read the entire target repository before adoption
- read every file in ai-context-reducer
- copy an entire design document into `AI_CONTEXT.md`
- create a large number of AI-only documents
- force large-repository mechanisms onto a small repository
- reorganize the existing documentation structure without a reason
- add automation whose benefit cannot be explained

## Success criteria

After adoption, the AI should be able to determine quickly:

- what the current task is trying to achieve
- where to read first
- what normally should not be read
- where the Source of Truth is
- which source / tests form the current working set
- when to stop exploration
- what must be validated to finish

The goal is to reach this state with the smallest useful setup for the target project.
