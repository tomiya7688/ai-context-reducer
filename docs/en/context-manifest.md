# Context Manifest

> Japanese Source of Truth: [参照先の目録](../jp/参照先の目録.md)

This method keeps a small pointer-based inventory before collecting full candidate information for an AI, then uses that inventory to choose the current task's working set.

A Context Manifest is neither a specification nor a collection of summaries. It is a routing index for reaching the necessary original sources with little context.

## 1. What is a Context Manifest?

A Context Manifest lists source / tests / docs / tasks / policies that may become relevant to current or future work, focusing on pointers rather than content.

A minimal entry can contain:

~~~text
pointer
role / reason
scope
optional priority or status
~~~

Example:

~~~text
docs/storage.md        specification      save format
src/storage/           implementation     persistence
tests/test_storage.py  validation         persistence
issue #123             current task       save migration
~~~

Do not copy file contents or long summaries into the manifest.

## 2. Purpose

In a large repository, an AI may otherwise read README files, documentation listings, source trees, test trees, and Issues broadly just to discover what exists.

A Context Manifest replaces that exploration with a short list of pointers.

~~~text
Task
  -> Context Manifest
  -> relevant pointers only
  -> selected working set
  -> original source / tests / docs
~~~

The manifest is not intended to contain enough information to complete implementation decisions by itself. Its role ends at deciding **what should be read**.

## 3. Keep it pointer-first

Store only the minimum information needed to select a working set.

Recommended:

- path / URL / Issue ID or another pointer
- role of the information
- applicable scope
- short task-relevance or priority hint
- routing-relevant state such as generated / stale / unavailable

Normally do not include:

- source contents
- test contents
- document contents
- long summaries
- detailed design explanation
- full diff / full log
- copies of constraints already owned by an original source

When a decision requires the content, follow the pointer back to the original source.

## 4. Do not replace the Source of Truth

A Context Manifest is derived information.

~~~text
Source of Truth
  -> source / tests / formal docs / Issue / policy

Context Manifest
  -> pointer / routing hint
~~~

When the manifest conflicts with the original source, the original source wins.

Do not store long-lived specification changes, design decisions, or unfinished requirements only in the manifest. Update the authoritative source and regenerate or minimally update the manifest.

## 5. Relationship with AI_CONTEXT / Current State / Context Pack

Separate responsibilities so similar documents do not duplicate the same information.

### AI_CONTEXT

AI_CONTEXT contains relatively stable **entry points, read order, important constraints, and routing policy** for the repository.

~~~text
AI_CONTEXT
  -> where to start / stable routing rules
~~~

Do not fill it with large candidate-file lists for every task.

### Current State

[Current State](context-state.md) briefly describes **what is currently true**: major available capabilities, constraints, and unimplemented items.

~~~text
Current State
  -> what is currently true
~~~

It is not a file inventory or a task working-set list.

### Context Manifest

A Context Manifest uses pointers to show **what original sources can be selected**.

~~~text
Context Manifest
  -> what can be selected
~~~

It comes before working-set selection and does not duplicate the content.

### Context Pack

[Context Pack](context-pack.md) is the temporary packet containing **the information and completion conditions actually selected for the current task**.

~~~text
Context Pack
  -> what this task actually needs
~~~

The relationship is:

~~~text
AI_CONTEXT
  -> stable entry / routing

Current State
  -> current capability / constraints

Context Manifest (optional)
  -> bounded candidate pointers

Context Pack
  -> selected task working set

Original sources
  -> final evidence / implementation truth
~~~

Do not maintain the same content in both the Manifest and Context Pack. The Manifest contains candidates; the Context Pack contains what this task actually selected.

## 6. Bounded context

A repository-wide giant file list defeats the purpose of a manifest.

Keep the agent-visible manifest bounded.

- filter by task relevance first
- return only entries needed for the relevant role / scope
- cap returned entries
- make truncation explicit
- expand only when more candidates are needed

A tool may scan the whole repository internally. The important constraint is on agent-visible output.

~~~text
internal scan may be broad
agent-visible manifest should be bounded
~~~

Do not treat size or file type alone as proof that something must be read. Prioritize relevance to the current task.

## 7. Working-set selection

Even when a manifest is used, the final working set is chosen from the task.

~~~text
Goal / Required / Acceptance
  -> manifest candidates
  -> target source
  -> matching tests
  -> direct dependencies
  -> detailed docs only if needed
~~~

A manifest entry is not by itself a reason to read the file.

When many candidates remain, narrow them further with Task Routing / Change Routing / Responsibility Map / Source Structure Index or similar methods.

## 8. Updates and staleness

A manifest can become older than its original sources.

- regenerate it when needed if generation is available
- keep manual manifests small
- update pointers when source moves or responsibilities change
- stop using an entry for routing once it is known to be stale
- do not keep appending new summaries to an old manifest

Do not use a manifest as long-term history storage.

## 9. When not to create one

A Context Manifest is often unnecessary when:

- target source / tests / docs are already explicit in the request
- the repository is small and candidate discovery is trivial
- the change is local to only a few files
- the task is one-off and has little reuse value
- manifest creation costs more than passing direct pointers
- AI_CONTEXT / Responsibility Map / Change Routing Map already narrows the target sufficiently

For example, "fix this function in this file and update its test" does not need a repository-wide manifest.

Use the method when:

~~~text
expected repeated routing saving
    > manifest creation + maintenance cost
~~~

## 10. Representation

The format is not fixed.

- Markdown
- JSON
- line-oriented text
- database / IDE index
- generated temporary artifact
- existing repository metadata

Any representation is valid if it remains pointer-first, bounded, original-source-first, and task-relevance-first.

## 11. Optional implementation

This repository includes `tools/common/large/context-manifest`.

It scans repository files and turns them into bounded JSON containing file path / size / coarse priority.

The tool's priority rules and JSON schema are not the Context Manifest method itself.

- a manual pointer list is valid
- a project-specific index is valid
- P0..P4 are routing hints, not absolute importance
- when task relevance is known, task-specific routing takes priority
- tool output does not replace original sources

## 12. Standard recommendations

- treat a Context Manifest as a pointer inventory to original sources
- do not duplicate full content or long summaries
- keep only the minimum metadata required for working-set selection
- keep agent-visible output bounded
- do not replace the Source of Truth
- separate its role from AI_CONTEXT / Current State / Context Pack
- do not read something merely because it appears in the manifest
- do not keep using stale manifests
- skip dedicated manifests for small repositories or obvious tasks
- do not make a particular tool or JSON format part of the method
