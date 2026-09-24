# Task Routing / Compact Workflow

> Japanese Source of Truth: [作業別の案内表](../jp/作業別の案内表.md)

This document organizes context-reduction techniques that proved useful in practice without depending on a particular project or AI.

## 1. Task Capsule

Instead of feeding the entire current Issue / Task to the AI, generate a short working Context Pack.

Include at least:

- Issue / Task ID
- title
- priority
- labels / task type
- compact summary
- relevant documents
- validation rule
- references to Sources of Truth

Use this Task Capsule as the entry point for the current task.

Do not turn the Task Capsule into a long-lived specification. Return to the original Issue, design document, source, or other authoritative material when needed.

## 2. Priority-first task selection

When multiple unfinished tasks exist, there is no need to make the AI read all of them before selecting one.

If the Issue tracker already has priority metadata, narrow the next task mechanically before passing it to the AI.

Example:

```text
P0 -> P1 -> P2 -> P3 -> unlabeled
```

The project can define ordering within the same priority.

Priority selection is simple work that can be handled outside AI context, so reuse tools or existing Issue metadata when practical.

## 3. Metadata-driven document routing

Use Issue labels, task type, target module, and similar metadata as routes to the required design documents.

Example:

```text
spec:architecture -> docs/architecture.md
spec:runtime      -> docs/runtime.md
spec:protocol     -> docs/protocol.md
spec:data         -> docs/data-format.md
```

Do not make the AI search all of `docs/` for related documents by default. Narrow candidates using metadata first.

Only search for directly related material when no routing rule applies.

The mapping may live in `AI_CONTEXT.md`, a configuration file, a helper tool, or another location appropriate to the project.

## 4. Compact issue summary

When an Issue body or request is long, create a short summary at task start.

The summary is not a replacement for the original source.

- keep a URL / Issue ID or other reference to the original
- do not blindly copy code blocks and decoration
- prioritize purpose, constraints, and completion conditions
- return to the original when the summary is insufficient for a decision

A strict fixed length is unnecessary, but avoid simply reproducing the entire Issue inside the Context Pack.

## 5. Compact change inspection

For normal change inspection, do not begin with the full diff. First inspect:

```text
changed file names
    +
diff stat / shortstat
    +
commit summary
    +
validation result
```

Read the full diff or affected files only when a problem appears or implementation review requires it.

This is especially useful for PR creation, progress checks, AI handoffs, and other cases where a change overview is enough.

## 6. Validation before handoff / PR

Run standard build / test / lint checks before generating a large description of the change.

Normally record only results in the Context Pack or PR summary.

Example:

```text
Validation
- build: passed
- tests: passed
```

Add only the necessary log range when something fails.

This avoids passing large success logs into AI context.

## 7. State chaining

Keeping the Issue ID or task ID in the Task Capsule allows later steps to reuse it.

Example:

```text
Issue
  -> Task Capsule
  -> branch / work
  -> compact change summary
  -> PR
```

Reusing the identifier reduces the need to rediscover what the work was about at every stage.

Do not make the Task Capsule itself the Source of Truth; keep references to the Issue and formal documents.

## 8. Standardization level

### Standard recommendation

- make Current Task Context the primary entry point
- route to required documents from task metadata
- inspect a compact change summary before the full diff
- keep only result summaries for successful build/tests
- preserve a path from the Task Capsule back to original sources

### Optional implementations

- automatic Issue priority selection
- automatic Issue-body compaction
- automatic label -> document mapping
- automatic PR summary generation
- branch / PR automation

These may be useful, but GitHub, a particular OS, or a particular AI is not part of the standard requirement.

## 9. Importing ideas from other projects

When bringing a technique from another project into this repository, do not necessarily append it directly to this document.

First check whether it:

- is reusable across multiple projects
- actually reduces context
- preserves correctness
- has low adoption cost
- can be added without breaking existing specifications

Promote only sufficiently general methods into standard recommendations.
