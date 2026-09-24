# Adaptive Adoption / Adoption Priority

> Japanese Source of Truth: [導入優先度](../jp/導入優先度.md)

This document provides decision criteria for Codex, Claude Code, ChatGPT, and similar AIs to observe a target project quickly and autonomously choose which `ai-context-reducer` methods to adopt.

The goal is **not to adopt everything**.

Before making adoption decisions, confirm the three principles in [Context Reduction Basics](context-reduction-basics.md).

1. Use static analysis for what can be statically analyzed
2. Bundle frequently used operations
3. Make the AI read only a subset

Treat individual methods as concrete applications of these principles. Do not treat the number or names of tools as adoption value by themselves.

> Adopt the minimal Core first. Use additional methods only when the expected benefit exceeds adoption and maintenance cost.

## 1. Adoption priority

### A — Core / almost every project

This is the minimal starting set.

- Small `AI_CONTEXT.md` or equivalent AI entry point
- Search first, read second
- Stop exploring once Goal / Required / Acceptance are known
- Explicit Source of Truth
- Separation of the current task from unrelated refactors
- targeted validation and Unverified areas
- [Context Exclusion](context-exclusion.md): normally exclude generated files / logs / vendor / caches / broad history from context, while retaining artifacts required as a Source of Truth or for validation

For some small projects, A alone is sufficient.

### B — High ROI / prioritize when conditions fit

These can often provide large reductions at relatively low cost.

| Method | Signals that favor adoption |
|---|---|
| Current State summary | Implemented features, constraints, and unfinished work have grown enough that README alone no longer describes the current state clearly |
| [Context Manifest](context-manifest.md) | There are many source / test / doc references and each task repeatedly searches broadly for candidates |
| Task Routing | There are many Issues / docs / subsystems and the material to read changes by task |
| Change Routing Map | Change categories can be mapped to source / tests / docs |
| [Architecture Boundary Routing](architecture-boundary-routing.md) | The project already has trustworthy responsibility boundaries, layers, components, or official communication paths that can narrow the initial working set |
| Responsibility Map | File / module count has grown and responsibility is hard to infer from names |
| Hierarchical Context | A monorepo / multi-app project has subsystem-specific rules and the root AI guide is growing |
| Evidence Budget | Search continues even after Required evidence is available, or tends to spread into history / broad docs "just in case" |
| Remote Delta First | Multiple AIs, chats, or developers update the same remote |
| Validation Routing | Required validation differs substantially by change |
| [Syntax Health Validation](syntax-health-validation.md) | A parser / compiler frontend is already available and a syntax check is cheaper than full build/test |
| Change / Test Impact Routing | The test suite is large or slow, source/test mapping or dependency data exists, and the full suite is run every time |
| compact policy checks | Policies are long or many rules are mechanically decidable |
| [Documentation Duplication Control](documentation-duplication-control.md) | The same rules or explanations are multiplying across README / AI guide / docs, causing drift and reread cost |

### C — Conditional / project-specific

These can have large benefits but should be adopted only in projects that need them.

| Method | Suitable projects |
|---|---|
| [Context Priority / Hotspot](context-priority.md) | There are large files or concentrated change areas and you want to choose routing granularity before reading full files |
| Source Structure Index | Very large codebases, huge files, many call/dependency relationships |
| changed-symbol routing | Tasks frequently modify only a few symbols inside large files |
| artifact-boundary validation | build / package / distribution differs from the source tree |
| headless-first validation | GUI / editor / game / interactive application |
| disposable validation workspace | export / save / conversion generates many temporary files |
| deterministic seam | many nondeterministic inputs such as random / clock / network / environment |
| structured runtime observation | runtime behavior can be checked through a few state values instead of huge logs |
| Boilerplate Generation | license / NOTICE / headers / standard text are distributed to many projects |
| Policy Routing | policies have multiple strengths such as Required / Recommended / Advisory |

### D — Optional / after confirming benefit

These are not mandatory standards.

- expensive generated indexes
- continuously maintained large call graphs
- complex summary caches
- large numbers of AI-only files
- excessive routing tables for small repositories
- automation whose adoption / maintenance cost exceeds its reduction benefit

Add them only when measurement or clear repeated cost justifies them.

## 2. Guidance by project size

Do not classify mechanically by LOC or file count alone. Judge whether the AI can reach the target area without confusion.

### Small

Characteristics:

- Major implementation is in a small number of files
- Few docs
- Source-to-test relationships are obvious
- Mostly single-developer / single-session work

Recommended:

```text
A Core
+ Validation Routing if needed
```

Context Manifest, Context Priority / Hotspot, Task Routing, and Source Structure Index are normally unnecessary. If standard compiler / tests are already cheap enough, do not add a dedicated Syntax Health step or enlarge the environment just to introduce a parser. For a small task where target source / tests / docs are obvious, pass direct pointers instead of creating a manifest. Do not add Hierarchical Context when a small root AI entry point is enough. If the test suite is small and a full run is cheap, Change / Test Impact Routing is unnecessary. Do not formalize Evidence Budget when target source / tests are already obvious.

### Medium

Characteristics:

- Multiple modules / subsystems
- Growing docs / tests / scripts
- Read locations vary by Issue or change category

Recommended:

```text
A Core
+ Responsibility Map
+ Change / Task Routing
+ Current State
+ Validation Routing
+ Evidence Budget only when exploration tends to run long
+ Change / Test Impact Routing only when the test suite is expensive
+ Hierarchical Context only when there are many subsystem-specific rules
```

### Large

Characteristics:

- The AI cannot identify the target area from the root listing alone
- Many subsystems, docs, tests, and generated artifacts
- Repeated rereading of the same files is costly

Recommended:

```text
A Core
+ applicable B High ROI items
+ Evidence Budget (tasks with unclear exploration stop conditions)
+ Hierarchical Context (when multi-app / local rules exist)
+ Change / Test Impact Routing (when the test suite is large)
+ Context Priority / Hotspot (do not use size alone to rank what should be read)
+ Source Structure Index
+ changed-symbol routing
+ split Context Pack
```

### Multi-agent / Concurrent

Regardless of size, when multiple AIs or people touch the same remote, prioritize:

```text
Remote Delta First
+ compact change summary
+ current task / handoff reference
```

## 3. Profiles by project characteristics

### Monorepo / Multi-app

Prioritize:

- Hierarchical Context / Scoped AI Instructions
- Task / Change Routing
- Responsibility Map
- package / app-level Validation Routing
- Change / Test Impact Routing when the test suite is large
- Evidence Budget when broad inspection happens repeatedly

Do not aggregate every subsystem detail at the root. Keep only repository-wide invariants there. A local guide should contain only scope-specific differences rather than copying its parent document.

### GUI / Game / Editor

Prioritize:

- headless-first validation
- deterministic runtime
- structured observation
- visual confirmation only when required by Acceptance
- disposable validation workspace

### Compiler / Language / Static Tool

Prioritize:

- Responsibility Map
- Change Routing Map
- targeted tests
- Change / Test Impact Routing when the test suite is large
- Policy checker
- Source Structure Index only after scale makes it useful

### Data / Conversion Tool

Prioritize:

- dry-run
- reproducible transformation
- disposable workspace
- bounded output / compact diff
- explicit source of truth

### Packaged / Distributed Application

Prioritize:

- source validation
- artifact generation
- artifact smoke
- required files / initialization validation

### Random / Time-dependent / Simulation

Prioritize:

- fixed seed / fixed input
- deterministic seam so RNG / clock etc. can be injected
- bounded runtime
- structured evaluation output

### Rule-heavy Project

Prioritize:

- Policy Routing
- machine-checkable rules -> checker
- semantic / architectural rules -> targeted review
- compact exception record

## 4. AI-driven adoption procedure

Codex / Claude Code and similar tools should proceed in this order.

### Step 1: shallow inspection

Initially inspect only:

- root file / directory names
- README
- existing `AGENTS.md` / `CLAUDE.md` / AI entry point
- documentation filenames and headings
- test directory / test naming
- build / package metadata
- minimum information needed to understand Git / remote workflow

Do not read all source, all docs, or all Issues at this stage.

### Step 2: classify signals

Briefly classify:

```text
size: small / medium / large
concurrent remote edits: yes / no
many docs or issues: yes / no
routing ambiguity: low / high
explicit architecture boundary available: yes / no
exploration drift risk: low / high
multiple apps/packages: yes / no
subsystem-specific instructions: yes / no
test suite cost: low / high
test impact mapping available: yes / no
GUI / interactive: yes / no
runtime nondeterminism: yes / no
generated / packaged artifact: yes / no
rule-heavy: yes / no
```

Exact numeric classification is unnecessary.

### Step 3: choose the smallest useful set

Always start with A Core. Select B / C only when a matching signal exists.

Do not add a method merely because it "might be useful later."

Choose Hierarchical Context only when there is a clear reason to place different instructions in multiple scopes. A large number of directories alone is not sufficient.

Choose Architecture Boundary Routing only when trustworthy responsibility / boundary information already present in the target project can be reused. Do not infer architecture just to create a profile, and do not introduce it as a conformance checker for a particular architecture. Skip it for Small repositories or when Responsibility Map / Change Routing Map is already sufficient.

Do not introduce Evidence Budget when normal Goal / Required / Acceptance stop conditions are sufficient. When used, limit it to tracking missing Required / Optional evidence rather than a hard token cap.

Do not introduce Change / Test Impact Routing when the full suite is cheap enough. When it is used, preserve broader fallbacks for shared/core/public contract changes.

### Step 4: modify minimally

Keep the first adoption change small.

- Improve an existing AI entry point when one exists
- Otherwise create a small `AI_CONTEXT.md`
- Do not reorganize existing docs
- Do not duplicate detailed specifications
- Add only necessary routing maps or similar aids
- When a local guide is needed, include only scope-specific differences
- Keep an Evidence Ledger pointer-oriented and short, only for tasks that need it
- Start test impact routing from existing naming / dependency information rather than building a dedicated analyzer first

### Step 5: verify usefulness

After adoption, verify at least:

- The AI entry point reaches the current work target
- The source of truth is identifiable
- Unrelated large areas do not need to be read
- The completion / validation entry point is clear
- Added files are not themselves excessively large
- If Evidence Budget was adopted, exploration can stop once Required evidence is complete
- If a local guide was adopted, unrelated subsystem instructions do not need to be read
- If test impact routing was adopted, necessary broader fallbacks remain

## 5. Compact adoption report

After adoption, the AI reports the result rather than a long explanation.

```text
Adopted:
- Core AI index
- Change Routing Map
- Validation Routing

Skipped:
- Source Structure Index: repository is still small
- Remote Delta First: single-writer workflow
- Hierarchical Context: no subsystem-specific rules
- Evidence Budget: normal stop conditions are already sufficient
- Change / Test Impact Routing: full test suite is already cheap

Why:
- source/test routing was the main repeated lookup cost
```

**Also record skipped methods and short reasons** to prevent all-inclusive adoption.

## 6. Decision principle

Priority is:

```text
accuracy
  > speed of reaching the work target
  > amount of context reduction
  > amount of automation
```

Adopt a method only when:

```text
expected repeated context saving
    > adoption + maintenance cost
```
