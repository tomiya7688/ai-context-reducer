# Context Exclusion / Ignore Candidates

> Japanese Source of Truth: [通常は読まないものを決める](../jp/通常は読まないものを決める.md)

This document defines Context Exclusion: keeping generated output, logs, vendor content, caches, history, and similar material that is normally unnecessary for the current task out of the AI's normal context so it can focus on authoritative sources.

The important distinction is that **normally excluding something from context is different from deleting it from the repository or adding it to ignore configuration**.

> Find exclusion candidates first, then confirm Source of Truth status, task relevance, and validation use before excluding them from normal context.

## 1. Purpose

Repositories often contain areas that are not the work target but can consume large amounts of context.

Typical examples:

- build / dist / generated output
- logs / traces / reports
- dependency / vendor directories
- cache / temporary directories
- runtime saves / backups
- broad Git history
- generated documentation / indexes
- editor / IDE generated state

There is no need to read these unconditionally for every task.

~~~text
repository
  -> normal context candidates
  -> default-excluded candidates
  -> task-specific promotion when required
~~~

The goal is not to make information invisible. It is to keep the normal working set small.

## 2. Do not exclude a Source of Truth

Do not exclude important original sources based only on a path name or file type.

Depending on the project, the following may be an official Source of Truth or an artifact required by Acceptance:

- checked-in generated source
- lockfile
- schema snapshot
- migration file
- golden test data
- fixture
- vendored code containing project-specific patches
- a project where binary / asset files are official input
- a generated API definition that is a distribution contract

Therefore decide in this order:

~~~text
candidate signal
  -> Source of Truth?
  -> current task target?
  -> required validation evidence?
  -> safe to exclude from normal context?
~~~

If any answer is yes, do not discard it through mechanical default exclusion.

## 3. Use three states

Context Exclusion is safer when modeled with three states rather than simple include / ignore.

### Normal context

Candidates normally read for the current task:

- target source
- matching tests
- authoritative docs / contract
- direct dependencies
- current task / required constraints

### Default-excluded context

Candidates normally not read:

- build outputs
- cache
- dependency mirror
- large logs
- runtime backup
- unrelated history
- generated reports

They can be restored later when needed.

### Validation-only / task-promoted

Items normally excluded but temporarily needed by Acceptance for a particular task.

Examples:

- package archive
- installer
- generated config
- export result
- compiled binary
- generated manifest
- transformed dataset

~~~text
default excluded
  -> Acceptance requires artifact evidence
  -> promote for validation only
  -> inspect bounded evidence
  -> return to default-excluded after task
~~~

This distinction allows release / packaging tasks to validate generated artifacts correctly without reading them every time.

## 4. Separate candidates from confirmed exclusions

Detecting an ignore candidate does not make it a confirmed exclusion.

~~~text
candidate
  -> review
  -> confirmed context exclusion
  -> optional repository ignore change as separate action
~~~

At minimum, review:

1. Is it a Source of Truth?
2. Is it a direct target of the current task?
3. Is it required as Acceptance / validation evidence?
4. Is it an important project-specific artifact?
5. Is its source and regeneration method known?
6. Is context exclusion sufficient, or is actual ignore configuration also needed?

Candidate detection is a conservative hint, not an apply decision.

## 5. Separate from repository ignore configuration

Context Exclusion decides what the AI normally does not read.

Changing `.gitignore`, `.ignore`, `.dockerignore`, IDE settings, build settings, or similar configuration is separate.

~~~text
context exclusion
  -> normally remove from AI working set

repository ignore configuration
  -> changes version-control / tool behavior
~~~

The latter is a write action that affects repository behavior.

Do not apply it automatically without an explicit task and review.

In particular, do not mechanically add already tracked files, release-required files, or generated-but-checked-in files to ignore configuration.

## 6. generated / logs / vendor / caches / history

### Generated output

Generated output is normally derived rather than authoritative, so it is a default-excluded candidate.

If the generated artifact itself is the target of distribution, compatibility, or format Acceptance, promote it to validation-only.

### Logs / traces / reports

Do not put full success logs into normal context.

When needed for failure diagnosis or runtime Acceptance, read only the relevant range or structured observation.

### Vendor / dependency directories

These are normally copies of external dependencies and therefore default-excluded candidates.

They may become task-specific when the project directly patches vendored code, when checking license / NOTICE files, during security investigation, or similar cases.

### Cache / temporary files

Normally exclude regenerable caches that are not evidence for the task.

An exception is when cache invalidation itself is the bug being investigated.

### History

Do not include all Git history in normal context.

Retrieve it in bounded form only when the current task has a concrete question requiring Remote Delta, blame, regression investigation, design rationale, or similar evidence.

## 7. Relationship to Artifact Boundary Validation

Generated artifacts are normally exclusion candidates, but in projects where the source tree differs from the final product, the artifact itself can be validation evidence.

The relationship to artifact-boundary validation in [Validation Routing](validation-routing.md) is:

~~~text
normal implementation context
  -> source / config / tests are primary
  -> build / dist artifacts default excluded

package / release / export validation
  -> source validation
  -> artifact generation
  -> generated artifact promoted for validation
  -> artifact smoke / required-files check
  -> compact result
~~~

The important point is not to promote the artifact into the Source of Truth.

- generator / config / source remain authoritative
- generated artifact is evidence that directly checks Acceptance
- after success, do not keep the full artifact or large file set in the Context Pack
- retain only necessary results and problem locations

## 8. Disposable validation workspace

When possible, write artifacts created only for validation into a disposable workspace.

This:

- avoids leaving noise in the working tree
- keeps them out of changed files
- prevents accidental inclusion in the next task's context
- makes a reproducible initial state easier to maintain

Move only validation artifacts that require long-term retention into an explicit storage location.

## 9. Protect project-specific important artifacts

Do not confirm exclusion from generic directory names alone.

Even directories named build, dist, generated, vendor, or data may be a project-specific Source of Truth.

During adoption, use shallow inspection to check:

- README / build instructions
- release / package manifest
- tracked file status
- generator source
- fixtures / golden data referenced by tests
- project-specific AI / contributor guide

When uncertain, keep the item as a candidate rather than confirming exclusion.

## 10. Relationship to AI_CONTEXT

For a small project, a short default-exclusion list under Ignore Normally in AI_CONTEXT is enough; a dedicated ignore map is unnecessary.

Example:

~~~text
Ignore Normally
- build outputs
- cache
- generated reports
- large logs
- unrelated history
~~~

Record exceptions and task-specific promotion only when needed.

Do not turn the exclusion list itself into a huge catalog.

## 11. Helper implementation

This repository includes `tools/common/medium/ignore-candidates`.

It is a helper that **proposes paths as candidates** that may have low value in agent context.

- returns candidates only
- explicitly sets `review_required_before_ignoring`
- does not make the final Source of Truth decision
- does not modify `.gitignore` or similar files
- does not delete files
- does not automatically exclude project-specific important artifacts
- leaves the need for validation-only artifacts to the task

When project metadata or existing ignore settings are already sufficient, this tool is unnecessary.

## 12. Recommended standard

- Normally exclude generated / logs / vendor / caches / broad history from context
- Do not exclude a Source of Truth from path names alone
- Separate candidate detection from confirmed exclusion
- Separate context exclusion from repository ignore configuration changes
- Do not automatically rewrite `.gitignore` or similar files
- Temporarily restore artifacts required by task / Acceptance as validation-only
- Do not keep generated artifacts permanently in normal context after artifact validation
- Read only necessary failure ranges or structured results from logs
- Retrieve history in bounded form only for a concrete question
- In a Small repository, do not add a dedicated mechanism when a short Ignore Normally list in AI_CONTEXT is enough
- Do not treat `ignore-candidates` as an apply tool
