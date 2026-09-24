# Context Priority / Hotspot

> Japanese Source of Truth: [読む候補の優先度を付ける](../jp/読む候補の優先度を付ける.md)

This document defines how to prioritize what to inspect when there are many context candidates, and how to use hotspot signals such as size / churn / concentration.

The most important rule is:

> **Do not read a file merely because it is large, frequently changed, or a hotspot. Relevance to the current task comes first.**

A hotspot is a signal for choosing a routing method or deciding whether deeper investigation is worthwhile. It is not a decision that a file must be read.

## 1. Basic priority order

Use the following order as a default:

~~~text
1. current task relevance
2. direct relationship to Required / Acceptance
3. target source / matching tests
4. direct dependency / authoritative contract
5. structure / responsibility / change-routing evidence
6. cheap signals such as size / churn / concentration
7. broad history / unrelated auxiliary information
~~~

A large file is not relevant merely because it is large.

Conversely, a small file may be high priority if it defines a public contract or directly affects Acceptance.

## 2. What is a hotspot?

A hotspot is a signal that additional routing or attention may be useful.

Examples:

- large file size
- deep directory location
- high change frequency
- changes concentrated in a particular module
- many responsibilities accumulated in one file
- high fan-in / fan-out
- high estimated cost if included in context

Use these signals to ask questions such as:

~~~text
Should this file be narrowed by symbol instead of read in full?
Would this module benefit from Change Routing / Responsibility Map?
Would Source Structure Index save context here?
Should this candidate be sliced before entering the Context Pack?
~~~

Being a hotspot is not proof that something should be read or that the design is bad.

## 3. Task relevance comes first

When the task already supplies direct relevance evidence, prefer it over cheap signals.

~~~text
Task: save format bug
  -> save implementation
  -> matching tests
  -> format contract
  -> direct consumer if needed
~~~

Even if the repository's largest file belongs to a rendering subsystem, do not add it automatically to this working set.

The same applies to high-churn modules that are unrelated to the current change.

## 4. Correct response to a large file

Finding a large file does not mean the first action should be to read it in full.

~~~text
large relevant file
  -> symbol / heading / text search
  -> target slice
  -> direct surrounding context
  -> full file only if still required
~~~

Context Priority helps choose not only **what** to read but also **the granularity** of reading.

For a large relevant file, high-precision routing such as Source Structure Index / structural search / target slice becomes more valuable.

## 5. Context Budget and working set

An estimate of context cost is not a hard cap for deleting required evidence from the working set.

Use it like this:

~~~text
required candidate
  -> estimated context cost
  -> cheap enough: read needed scope
  -> expensive: narrow by symbol / section / query
  -> still required: include enough evidence
~~~

Do not skip required source because it exceeds a budget. First ask whether the same evidence can be reached at smaller granularity.

[Evidence Budget](evidence-budget.md) manages Required evidence and exploration-stop conditions. It is different from estimating context cost.

~~~text
Evidence Budget
  -> what evidence is required

Context cost estimate
  -> how expensive a candidate is to include
~~~

## 6. Cheap signals and high-precision routing

### Cheap signals

Low-cost information includes:

- file bytes
- line count
- directory depth
- file count
- recent churn
- change concentration
- file type / path role

Use cheap signals to decide where more precise routing may be worth its cost before doing deep repository analysis.

### High-precision routing

Information that more directly represents task relevance includes:

- Task / Change Routing
- Responsibility Map
- Architecture Boundary Routing
- symbol / dependency index
- changed-symbol information
- direct import / call relation
- matching tests
- targeted search results

Prefer high-precision routing when available for deciding the current working set.

~~~text
cheap signal
  -> decide where precision is worth paying for
  -> precise routing
  -> bounded working set
~~~

Do not determine the final working set from cheap signals alone.

## 7. Churn / concentration

Churn and concentration can be useful maintenance/risk signals:

- the same area is repeatedly rediscovered
- responsibility or routing information may reduce repeated cost
- regression tests or targeted validation may have high value
- an unstable area may justify prioritizing current source / tests

But frequent historical change does not prove relevance to the current task.

If history itself is expensive to inspect, only retrieve detailed churn when the current task provides a reason.

## 8. Relationship with Context Manifest

[Context Manifest](context-manifest.md) is a bounded inventory of candidate pointers.

Context Priority decides how those candidates should be ordered or narrowed for the current task.

~~~text
Context Manifest
  -> candidate pointers

Context Priority
  -> task-relevant ordering / granularity

Context Pack
  -> actually selected working set
~~~

A manifest may contain P0..P4 or other priorities, but current task relevance must override a fixed file-type priority.

## 9. When to skip dedicated analysis

Normally skip dedicated hotspot/context-cost analysis when:

- the repository is small
- target source / tests are obvious
- files are small enough that full reads are cheap
- routing ambiguity is low
- repeated context cost is not a problem
- cheap signals would not change working-set selection

Running a repository-wide hotspot scan for every small task can cost more than it saves.

## 10. Optional implementations

This repository contains helper tools for Context Priority decisions.

### context-budget

`tools/common/large/context-budget` estimates the cost of putting candidate text into agent context.

- it is not an exact tokenizer
- it does not decide that an expensive candidate is unnecessary
- use high estimated cost as a signal to consider slice / query / symbol routing

### hotspot-report

`tools/common/large/hotspot-report` returns bounded hotspot candidates using signals such as size / depth.

- a high rank does not mean the file must be read
- it does not determine task relevance
- it does not score architecture quality
- use it as a cheap signal for where high-precision routing may be useful

Neither tool is required for the method. Existing IDE information, Git metadata, custom scripts, or a simple file listing may be sufficient.

## 11. Standard recommendations

- make task relevance the highest Context Priority
- do not turn hotspots into a "must read" ranking
- use size / churn / concentration only as supporting signals
- for a large relevant file, consider slice / symbol routing before a full read
- do not use context cost as a hard cap on necessary evidence
- use cheap signals to decide where high-precision routing is worth using
- prefer Task / Change / Responsibility / structure evidence for working-set decisions
- prefer task-specific relevance over fixed Context Manifest priorities
- skip dedicated analysis for small repositories or obvious tasks
- do not make context-budget / hotspot-report scores or ordering part of the method itself
