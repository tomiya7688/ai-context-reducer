# Documentation Duplication Control

> Japanese Source of Truth: [文書の重複を管理する](../jp/文書の重複を管理する.md)

This document defines how to prevent repeated copies of the same rules or explanations across AI-facing documents, README files, guides, summaries, and similar material from increasing context and causing update drift.

The goal is not to remove every piece of similar wording.

> **Do not maintain the same detailed information as multiple Sources of Truth. Prefer one authoritative source plus the minimum necessary pointer / summary.**

Distinguish short duplication that improves readability from dangerous duplication that creates stale copies.

## 1. Why control duplication?

Copying the same rule, specification, or explanation into multiple documents increases how much the AI reads and makes it unclear which copy to trust when they diverge.

~~~text
same rule
  -> README
  -> AI_CONTEXT
  -> setup guide
  -> architecture doc
  -> tool README
~~~

In this state, one change requires synchronizing multiple files.

The primary purpose of duplication control is **clarifying information responsibility**, even before context reduction.

## 2. Source of Truth + pointer

Whenever possible, choose one authoritative source for detailed information.

~~~text
Source of Truth
  -> full rule / contract / specification

Other documents
  -> short purpose
  -> pointer to Source of Truth
~~~

Example:

~~~text
docs/api-contract.md
  -> full API contract

README
  -> API contract overview + link

AI_CONTEXT
  -> where to read when changing the API + link
~~~

Do not reproduce the detailed contract in README or the AI entry point. Keep only a short statement of when and why to read it.

## 3. A summary / index does not replace the original source

Summaries, Context Packs, Context Manifests, method indexes, AI_CONTEXT, and similar material are entry points for reaching necessary original sources.

~~~text
summary / index / pointer
  -> locate authoritative source
  -> read original when needed
~~~

Do not add a new specification only to a summary without reflecting it in the official document or source.

When a summary conflicts with the original source, prefer the original and update or remove the summary.

## 4. Duplication with high drift risk

Avoid duplication that is especially likely to drift:

- full copies of normative rules across multiple docs
- independently maintained version / supported-platform / compatibility tables
- detailed copies of the same CLI contract in README and another guide
- architecture boundaries explained independently in multiple files
- generated output manually recopied into documentation
- current state independently updated in README / Issue / AI guide

If it is unclear which other files must change when one copy changes, reconsider the Source of Truth.

## 5. Intentional duplication

Not all duplication is bad.

Short repetition may be reasonable for readability or safety:

- a one- or two-sentence overview that prevents a new user from getting lost
- a short invariant needed at the AI entry point
- a short warning about safety / destructive operations
- minimum usage conditions required inside a standalone artifact
- table-of-contents or navigation labels
- a short explanation needed locally to avoid misuse

Intentional duplication should still:

- avoid copying details
- retain a pointer to the authoritative source
- not become an independent new specification
- not grow beyond what can be maintained

~~~text
short duplicate for readability
  + authoritative pointer
  != second Source of Truth
~~~

## 6. Tradeoff with readability

Over-aggressive deduplication can turn documentation into links only, making it difficult for humans and AIs to read.

Bad:

~~~text
See A.
See B.
See C.
~~~

This does not explain what to read or why.

A good pointer includes short context.

~~~text
When changing API compatibility, check the versioning section of docs/api-contract.md.
~~~

Do not remove so much meaning that navigation cost increases.

Decision criterion:

~~~text
duplicate detail maintenance cost
  vs
local readability / safety benefit
~~~

Keep a short explanation when it is sufficient, and move only the details to the authoritative source.

## 7. Separate document responsibilities

Define the role of each document type to avoid copying the same information.

Example:

- README: human-facing overview, adoption, entry point
- AI_CONTEXT: AI-facing routing, read order, short important constraints
- Current State: current capabilities and constraints
- detailed docs: specification / design contract
- Issue: task requirement / discussion / priority
- source / tests: implementation / executable truth
- generated artifact: derived result

When roles overlap, make the authoritative source explicit.

## 8. Procedure when finding a duplicate candidate

Do not mechanically delete similar or identical text.

~~~text
duplicate candidate
  -> identify document roles
  -> identify Source of Truth
  -> decide intentional vs drift risk
  -> replace detail with short pointer if useful
  -> verify no required meaning was lost
~~~

Check:

1. Do both copies intend the same meaning?
2. Is one a summary / example / warning?
3. Which is authoritative?
4. Must either document be readable standalone?
5. Would removal prevent users from reaching the original source?
6. Is the wording difference actually drift, or a scope difference?

## 9. Do not auto-delete

Do not delete, merge, or rewrite documentation solely from duplicate-detection output.

Similar text may have different reasons:

- different scope
- defining the same term
- intentionally repeated safety warning
- template or generated file
- required example
- standalone distribution requirement

Automation should therefore normally stop at **candidate detection and pointer suggestions**.

A human or task-owning agent applies changes only after confirming document responsibilities.

## 10. Duplication that must stay synchronized

When the same content must appear in multiple artifacts, consider generation from canonical data rather than manual synchronization.

~~~text
canonical data
  -> generated copies
~~~

Do not force automation for small documents when maintaining the generation mechanism costs more.

Generated copies are still not the Source of Truth; make the canonical input explicit.

## 11. Small repositories

A project with few docs and no duplication drift problem does not need a dedicated duplicate scan.

At minimum:

- choose the authoritative source for detailed specifications
- use short explanations + pointers elsewhere
- check the existing authoritative source before adding another copy of a rule

## 12. Helper implementation

This repository includes `tools/common/medium/doc-duplicate-hints`.

It is a **hint tool** that compactly reports identical or similar documentation candidates.

- finds duplicate candidates only
- does not decide which is correct
- does not decide intentional duplication vs drift risk
- does not automatically delete files
- does not automatically merge text
- does not automatically choose a Source of Truth

Use tool output to narrow review targets. Make the final decision after checking document roles and authoritative sources.

## 13. Recommended standard

- Do not make the same detailed rule / specification multiple Sources of Truth
- Prefer Source of Truth + short pointer
- Do not treat a summary / index as a replacement for the original source
- Allow short intentional duplication required for readability / safety
- Keep an authoritative pointer even in intentional duplication
- Do not mechanically delete similar text
- Check document responsibility and scope for each duplicate candidate
- Do not remove information required by standalone artifacts
- When synchronized duplication is necessary, generate it from canonical data when worthwhile
- Do not use `doc-duplicate-hints` as an automatic cleanup tool
