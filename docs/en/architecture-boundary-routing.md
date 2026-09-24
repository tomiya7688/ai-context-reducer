# Architecture Boundary Routing

> Japanese Source of Truth: [既存の設計境界で読む範囲を絞る](../jp/既存の設計境界で読む範囲を絞る.md)

This method reuses responsibility boundaries, layers, components, and formal communication paths that already exist in the target project as routing information for narrowing the AI's initial reading scope.

The important point is that it does **not** infer a new architecture or judge whether the project conforms to a particular architecture. Use it only when existing design information is trustworthy.

## 1. Purpose

In a large project, even when one changed file is known, broad exploration may still be required to decide how much surrounding code must be read.

When responsibilities and boundaries are already explicit in the architecture, begin with the relevant responsibility and necessary boundaries instead of expanding immediately to the whole repository.

~~~text
Task / changed path
  -> project-owned architecture boundary
  -> first working set
  -> target source / matching tests
  -> direct collaborators
  -> broader expansion only if needed
~~~

The goal is to reduce the initial exploration scope without sacrificing correctness.

## 2. Existing information that can be reused

A dedicated profile is not required. You can reuse information the project already has, such as:

- architecture / design documents
- module / package ownership
- Responsibility Map
- layer / component definitions
- API / message / event boundaries
- directory ownership rules
- dependency direction
- project-specific routing metadata

These do not replace the original sources.

If you create a short routing table or profile, keep pointers to the formal architecture/specification and prefer the original source whenever there is a conflict.

## 3. When it is useful

This method is useful when several of the following apply:

- there are multiple modules / subsystems and it is difficult to decide the initial reading scope
- responsibilities or layers are already defined
- formal communication paths or contracts between components are explicit
- the same architecture information is repeatedly reconstructed from source exploration
- boundaries can exclude unrelated subsystems from the first working set

Do not adopt it merely because an architecture exists. Use it when:

~~~text
expected repeated context saving
    > routing metadata maintenance cost
~~~

## 4. Choose the first working set

### Change inside one responsibility

If the change stays within one responsibility, start with that responsibility and its direct collaborators.

~~~text
target
  -> owning responsibility
  -> direct collaborators
  -> matching tests
~~~

Add other components only when there is evidence of contract change or impact.

### Change to a boundary itself

When changing an API, message, event, serialization format, or other boundary contract, one side is not enough.

~~~text
boundary change
  -> sender / caller side
  -> contract
  -> receiver / callee side
  -> matching validation
~~~

### Unclassified work

Do not force a path or task into an architectural category when the existing information does not classify it.

~~~text
unclassified
  -> generic Task / Change Routing
  -> Responsibility Map
  -> search / Source Structure Index
  -> source details
~~~

Guessing that something "probably belongs to this layer" can create false negatives, so send unclassified work to a fallback path.

## 5. Do not turn it into an architecture checker

Architecture Boundary Routing does not standardize layered architecture, Clean Architecture, MVC, frontend/backend separation, or any other structure.

It is also not intended to decide:

- whether a design is good
- whether it conforms to the "correct" architecture
- whether layer violations exist
- whether a module should be split
- which architecture should be adopted

It uses project-owned boundaries only as **exploration input**.

If architecture-rule compliance needs validation, handle that separately through an existing linter, checker, or targeted review.

## 6. Relationship with other methods

### Responsibility Map

[Responsibility Map](responsibility-map.md) briefly answers which file or module owns which responsibility.

Architecture Boundary Routing uses boundaries and formal relationships between those responsibilities to decide how far the first working set should extend.

~~~text
Responsibility Map
  -> who owns what

Architecture Boundary Routing
  -> which boundary limits the first working set
~~~

If a Responsibility Map alone is enough to reach the target, do not add separate architecture routing.

### Change Routing Map

[Change Routing Map](change-routing-map.md) routes a change category directly to source / tests / docs.

Architecture Boundary Routing can use existing architecture boundaries as an input to that routing.

~~~text
change type
  -> Change Routing Map
  -> architecture boundary if relevant
  -> target source / tests
~~~

If the change category already determines the target, there is no need to read additional architecture information.

### Source Structure Index

[Source Structure Index](source-structure-index.md) is an index that uses mechanical structure such as symbols, imports, and dependencies to reach original sources.

Architecture Boundary Routing normally narrows the coarse scope before using that index.

~~~text
project-owned boundary
  -> candidate scope
  -> Source Structure Index
  -> target symbol / direct dependency
~~~

If architecture information is missing or ambiguous, start with Source Structure Index or normal search instead.

## 7. Fallback

Do not use Architecture Boundary Routing when:

- architecture information does not exist
- the profile or map is stale and does not match current source
- the task cannot be classified into existing boundaries
- the boundary does not materially shrink the working set
- the project is small and target source / tests are already obvious

Example fallback:

~~~text
Task Routing
  -> Change Routing Map
  -> Responsibility Map
  -> search / Source Structure Index
  -> targeted source / tests
~~~

The absence of a dedicated profile is not a defect. Do not infer an architecture merely to create one.

## 8. Skip it for small repositories

A dedicated architecture-routing layer is normally unnecessary when:

- the main implementation consists of only a few files
- source / test relationships are obvious
- subsystem boundaries are not an exploration cost
- Responsibility Map or Change Routing Map is sufficient

In a small project, maintaining routing documents or metadata may cost more context than the method saves.

## 9. Maintenance

Avoid drift from the original architecture information.

- keep the formal architecture/specification as the Source of Truth
- store only the minimum boundary information needed for routing
- update routing metadata in the same change set as architecture changes
- stop using a profile once it is known to be stale
- do not fill unknown classifications by guessing

A summary or profile must not become a duplicated specification.

## 10. Optional implementation

This repository includes `tools/common/medium/architecture-boundary-router`, which converts a project-provided routing profile into path classification and compact routing hints.

The tool is not required for the method.

- use it only when a profile already exists
- fall back to generic routing when no profile exists
- do not use it as a checker for a specific architecture
- do not let the profile replace the original architecture/specification

A different map format, build metadata, IDE information, or project-specific script is equally valid if it provides the same routing.

## 11. Standard recommendations

- reuse only responsibility and boundary information the project already owns
- do not standardize a specific architecture
- use it only to narrow the first working set
- inspect both sides when changing a boundary contract
- do not narrow unclassified work by guesswork; return to generic routing
- avoid duplicating the roles of Responsibility Map / Change Routing Map / Source Structure Index
- do not add dedicated routing for small repositories
- prefer the original architecture/specification over routing metadata
- do not make a tool or profile format part of the method definition
