# ai-context-reducer

English | [日本語](README.md)

A repository of principles and methods for helping AI systems such as Codex and Claude Code reach the design and implementation information they need without reading more context than necessary.

The main focus is the methods and documentation. Portable helper tools are also provided so repeated work and mechanically decidable processing can happen outside the AI context. Major Common capabilities are available through the single `acr-toolbox` binary.

## Three principles to understand first

Context reduction is based on three ideas:

1. Use static analysis for what can be analyzed statically
2. Bundle frequently repeated operations
3. Make the AI read only the necessary subset

Most individual methods and tools are one of these ideas or a combination of them. See [Context Reduction Basics](docs/en/context-reduction-basics.md) for details.

## Goal

> Instead of making the AI read a large amount of information to find what it needs, select and route the necessary information before giving it to the AI.

Once enough information is available, stop exploring.

> When Goal / Required / Acceptance / working set are sufficient, stop additional exploration.

Priority:

```text
accuracy
  > speed of reaching the work target
  > amount of context reduction
  > amount of automation
```

Treat summaries as indexes rather than replacements for original sources, and preserve a path back to source / tests / docs / diff when needed.

## Releases and downloads

Download published archives from [GitHub Releases](https://github.com/tomiya7688/ai-context-reducer/releases).

The current v1.0.x portable distribution provides archives for:

- Windows x64 / arm64
- Linux x64 / arm64
- macOS x64 / arm64

Each normal archive contains:

- `acr-toolbox`
- `go-symbols`
- `go-import-map`
- `go-package-graph`
- `affected-tests`
- `README.md`
- `TOOLS_README.md`
- `LICENSE`
- `RELEASE_MANIFEST.json`

A common `SHA256SUMS` file is published alongside the six archives.

Before distribution, GitHub Actions builds the actual native binaries for all six targets, runs E2E with those binaries, creates the archives, extracts them again, and verifies their contents. Source-side unit tests alone do not satisfy the Release gate.

```text
acr-toolbox version
acr-toolbox analyze <project-root>
acr-toolbox select <project-root>
```

`acr-toolbox version` returns the release version, commit, OS, and architecture as JSON.

Starting with v1.1.0, the lightweight normal bundle remains available and a separate GUI Hub Full Bundle is added as a superset. The Full Bundle keeps the normal CLI contract and does not require users to install a Go toolchain. See [Full Bundle Distribution Design](docs/en/full-bundle-layout.md) and [Releasing v1.x](docs/en/releasing.md).

## Ask Codex / Claude Code to adopt it

The initial entry points are:

1. this `README.en.md`
2. [Context Reduction Basics](docs/en/context-reduction-basics.md)
3. [Adoption Priority](docs/en/adoption-priority.md)
4. [`templates/AI_CONTEXT.md`](templates/AI_CONTEXT.md)

Then shallow-inspect the target repository and adopt **only the methods with meaningful expected benefit**, rather than everything.

A ready-to-use request is available in [Adoption Prompt](docs/en/adoption-prompt.md).

## Minimal Core

Keep the Core useful for almost every project small:

- a small `AI_CONTEXT.md` or equivalent AI entry point
- Search first, read second
- stop exploring once Goal / Required / Acceptance are known
- explicit Source of Truth
- do not mix unrelated refactors into the current task
- targeted validation
- explicitly record unverified areas as `Unverified`
- normally exclude logs / generated artifacts / history from context

For a small repository, it is fine to stop here.

## Add methods according to expected benefit

Choose additional methods from the characteristics of the target project.

| Situation | Methods to prioritize |
|---|---|
| many docs / Issues / subsystems | Task Routing / Change Routing Map |
| file / module responsibilities are unclear | Responsibility Map |
| the existing architecture defines responsibility boundaries, layers, or official communication paths | Architecture Boundary Routing |
| monorepo / multi-app with many local rules | Hierarchical Context / Scoped AI Instructions |
| exploration continues after Required evidence is available | Evidence Budget / bounded evidence collection |
| README alone no longer describes current capabilities and constraints | Current State summary |
| multiple AIs, chats, or people update the remote | Remote Delta First |
| huge codebase / expensive call or dependency exploration | Source Structure Index / changed-symbol routing |
| large test suite is fully run for every change | Change / Test Impact Routing |
| GUI / game / editor | headless-first + visual confirmation when needed |
| random / time-dependent / simulation | deterministic seam / fixed input / bounded runtime |
| package / distribution differs from source | artifact-boundary validation |
| save / conversion / export creates temporary files | disposable validation workspace |
| many coding rules | Policy Routing + compact policy checks |
| repeated license / NOTICE / header text | Boilerplate Generation |

See [Adoption Priority](docs/en/adoption-priority.md) for detailed adoption signals and project-size guidance.

## Standard flow

```text
AI_CONTEXT / existing agent guide
        ↓
shallow inspection
        ↓
classify project signals
        ↓
current task: Goal / Required / Acceptance
        ↓
Search / Index / Routing
        ↓
stop exploration when sufficient
        ↓
target source / symbols / matching tests
        ↓
implementation
        ↓
smallest sufficient validation
        ↓
compact result + Unverified areas
```

When remote conflicts are possible, insert a compact remote delta before implementation.

## Documentation

Japanese documentation under [`docs/jp/`](docs/jp/) is the Source of Truth. English translations are under [`docs/en/`](docs/en/). Japanese/English document pairs are managed by [`docs/DOCUMENT_MAP.json`](docs/DOCUMENT_MAP.json).

You do not need to read all documentation when adopting the project.

- **Method Index**: [`docs/en/method-index.md`](docs/en/method-index.md) — one-line descriptions of each method and links to the detailed documents
- Basic principles: [`docs/en/context-reduction-basics.md`](docs/en/context-reduction-basics.md)
- Adoption decisions: [`docs/en/adoption-priority.md`](docs/en/adoption-priority.md)
- Adoption prompt: [`docs/en/adoption-prompt.md`](docs/en/adoption-prompt.md)
- Basic guide: [`docs/en/guide.md`](docs/en/guide.md)
- External tool reference policy: [`docs/en/external-tool-reference-policy.md`](docs/en/external-tool-reference-policy.md)
- Release / completion gate: [`docs/en/releasing.md`](docs/en/releasing.md)
- AI entry-point template: [`templates/AI_CONTEXT.md`](templates/AI_CONTEXT.md)
- Task template: [`templates/CONTEXT_PACK.md`](templates/CONTEXT_PACK.md)

Detailed links for individual methods are kept in the [Method Index](docs/en/method-index.md) rather than duplicated here.

## Relationship to external projects

AI Context Reducer may learn useful ideas from external repositories and existing projects, but its standard does not depend on a particular reference project.

- generalize and adopt only useful methods
- do not make an external repository a mandatory dependency
- do not standardize a particular CLI, file format, or directory layout
- keep it possible to satisfy the same principle with another implementation

When linking to a concrete external tool, the general rule is to include only tools that are **free to use / commercially usable / do not require visible credit during normal use / are portable or easy to adopt**. See [External Tool Reference Policy](docs/en/external-tool-reference-policy.md).

## Do not over-adopt

This project's own practices must not cause context bloat.

```text
expected repeated context saving
    > adoption + maintenance cost
```

Do not add a mechanism that fails this condition.

The standard is adaptive: use a small mechanism for a small repository, and add routing / indexes only when a larger repository needs them.

## License

Everything in this repository, including documentation, design, templates, scripts, utilities, and tools, is provided under the [MIT License](LICENSE).

External projects and content linked or referenced from this repository remain subject to the licenses specified by their respective distributors.
