# Hierarchical Context / Scoped AI Instructions

> Japanese Source of Truth: [場所ごとの指示](../jp/場所ごとの指示.md)

In a large repository, monorepo, or multi-application project, do not put every AI-facing rule in one root document.

> Put shared rules at the root, local rules near the relevant subtree, and read only the additional instructions closest to the current work.

This is not a specification for a particular AI product or filename. It is the general principle of **progressive disclosure / nearest relevant instruction**.

## Purpose

Keep the root AI entry point small while still providing accurate access to subsystem-specific build / test / architecture / ownership information.

```text
repository-wide guide
        ↓
current task / target subtree
        ↓
nearest relevant local guide
        ↓
target source / tests / docs
```

The goal is to avoid loading rules for unrelated subsystems on every task.

## Responsibilities by scope

### Root / Repository-wide

At the root, keep only information that generally applies across the repository.

- repository purpose
- Source of Truth
- shared safety / compatibility rules
- repository-wide routing entry points
- policy for locating local guides
- minimal validation principles shared by the repository

Do not collect subsystem-specific build commands, local design rules, or individual fixtures at the root.

### Subsystem / Local

Near a subsystem, keep only information required inside that subtree.

- package / app-specific build and test commands
- local architecture constraints
- local ownership / responsibility map
- subsystem-specific Source of Truth
- handling of generated files
- local validation / smoke tests
- compatibility constraints

Do not copy the parent document. Record only the **difference**.

### Current Task

In an Issue, Context Pack, or other task artifact, keep only Goal / Required / Acceptance needed for that change. Do not copy long-lived subsystem policy into the task.

## Nearest Relevant Instruction

After the work target is known, inspect only the nearest instructions that apply to the current path / subsystem.

```text
repo/
  AI_CONTEXT.md
  apps/
    editor/
      LOCAL_GUIDE.md
      src/
    server/
      LOCAL_GUIDE.md
      src/
```

When changing `apps/editor/src/...`, read the shared root rules and the editor subtree guide. Do not read the server guide.

A local guide may be named `AGENTS.md`, `CLAUDE.md`, or any project-specific name. If the agent natively resolves hierarchical instructions, use that capability. Otherwise, follow explicit routing from the root index.

## Precedence

This standard does not define exact instruction precedence for a particular agent.

- local guides must not silently override repository-wide invariants
- local guides add conditions specific to their scope
- explicit task requirements define Acceptance for the current work
- when instructions conflict, return to the Source of Truth rather than guessing

When an agent has its own precedence rules, follow that agent's specification.

## Avoid duplication

Bad:

```text
root guide: 300 lines
editor guide: copy root 300 lines + 20 lines
server guide: copy root 300 lines + 15 lines
```

Recommended:

```text
root guide: 50 shared lines
editor guide: 20 editor-specific lines
server guide: 15 server-specific lines
```

Copying the same rule across scopes causes update drift, contradictions, and unnecessary context growth.

## Relationship with Task Routing / Policy Routing

- **Task Routing**: identifies where to read
- **Policy Routing**: identifies which policies are Required / Recommended / Advisory
- **Hierarchical Context**: decides where instructions live and which scopes need to be read

Keep these roles separate. Do not turn every local guide into another large routing table.

## Signals that it is useful

- monorepo
- multiple apps / packages / plugins
- different build / test procedures per subsystem
- different design rules per subsystem
- root AI guide is becoming large
- unrelated local rules are repeatedly loaded into AI context

## When not to adopt it

For a small repository where a short root AI entry point is enough to reach the main source / tests / docs without confusion, no hierarchical structure is needed.

Do not create local guides mechanically in every directory.

```text
expected repeated context saving
    > adoption + maintenance cost
```

Add only scopes that satisfy this condition.

## Monorepo example

```text
repo/
  AI_CONTEXT.md
  docs/
    architecture.md
  apps/
    desktop/
      AI_CONTEXT.local.md
      src/
      tests/
    web/
      AI_CONTEXT.local.md
      src/
      tests/
  packages/
    core/
      AI_CONTEXT.local.md
      src/
      tests/
```

Keep only Source of Truth, shared compatibility rules, task routing, and local-guide discovery policy at the root. Put subsystem-specific build, test, smoke, and architecture constraints in the local guide.

## Minimal adoption example

When useful, add only this kind of rule to the root AI entry point:

```text
## Local Instructions
Read a local AI guide only when one exists in the target subtree.
Do not copy parent instructions into a local guide; record only scope-specific differences.
```

If a routing map already lists local guides, use it instead of creating another duplicate list.

## External tool examples

Hierarchical-instruction features in coding agents are valid implementation examples, but pricing and usage conditions vary by product. Any concrete external product link in this document must satisfy [External Tool Reference Policy](external-tool-reference-policy.md).

The standard currently remains independent of any specific agent, so no product-specific external-tool links are included.

## Completion conditions

- the root AI guide focuses on repository-wide information
- subsystem-specific information is near the scope that needs it
- unrelated local guides do not need to be read for the current task
- parent policies are not repeatedly copied
- the Source of Truth for each local guide is clear
- the standard does not depend on a particular agent or filename

## Portable scoped guide resolver

When an agent cannot resolve hierarchical instructions automatically, a repository-local fallback can be used.

```text
acr-toolbox scoped-guides path/to/target .
python tools/common/small/scoped-guides/script/scoped_guides.py path/to/target .
```

The resolver returns only guide candidates on ancestor paths between the repository root and the target. It returns compact JSON with path / scope / reason rather than full guide contents or agent-specific precedence. Candidate filenames can be changed with `--name`.
