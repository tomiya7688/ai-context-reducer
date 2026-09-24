# External Tool Reference Policy

> Japanese Source of Truth: [外部ツール掲載基準](../jp/外部ツール掲載基準.md)

When this repository names an external tool as a concrete example, the tool should normally satisfy all of the following:

- free to use
- usable commercially
- does not require credit in normal output, UI, or README usage
- portable or easy to adopt

Do not list tools whose conditions are unclear.

"Credit not required" here means that ordinary use does not require displaying the tool name or attribution in generated output, UI, README, or similar surfaces.

A separate case is software under MIT / BSD / Apache-2.0 or similar licenses where redistribution of the tool itself requires retaining license notices. Evaluate development-only use separately from bundling the tool in a distribution.

For adoption, prefer standalone binaries, package-manager installation, or repository-local wrappers that are straightforward to use.

## Current examples

When concrete examples are useful, prefer free, commercially usable, easy-to-adopt open-source tools such as:

- [Nx](https://github.com/nrwl/nx): affected project / test routing
- [Pants](https://github.com/pantsbuild/pants): changed target / dependency-based validation routing
- [SCIP](https://github.com/scip-code/scip): code-intelligence index
- [Tree-sitter](https://github.com/tree-sitter/tree-sitter): portable syntax parsing
- [ast-grep](https://github.com/ast-grep/ast-grep): structural search / lint / rewrite
- [Copier](https://github.com/copier-org/copier): versioned project templates
- [Cookiecutter](https://github.com/cookiecutter/cookiecutter): lightweight project templates

Individual method documents should mention only examples directly relevant to that method.

## Examples to omit

Even a strong tool should be left out of concrete example links when:

- free use is not assured
- commercial-use conditions vary by use case
- explicit credit is required during use
- adoption requires a persistent service contract or heavy server setup while an equivalent lightweight option exists
- license or usage conditions cannot be verified

Before adding an external tool, prioritize official information when checking free use, commercial use, attribution requirements, and installation. If conditions later change, remove or replace the reference.

The standard principles themselves must not depend on external tools.

## External / fallback / unsupported matrix

External tools are not mandatory dependencies. Keep only lightweight subsets as portable repository-local fallbacks and delegate advanced features to higher-quality external tools.

| Capability | External example | Repository-local fallback | Intentionally unsupported / delegated |
|---|---|---|---|
| fast text search | ripgrep | `acr-toolbox search` | full ripgrep-compatible CLI / all optimizations |
| file discovery | fd | `acr-toolbox find` | full fd-compatible filters / UX |
| syntax / structural search | ast-grep | `structural-search` (Python AST fallback) | multi-language AST rule engine / rewrite engine |
| affected test routing | Nx / Pants | `affected-tests`, `structure-index affected` | full build-graph / coverage engine |
| scoped AI instructions | agent-native scoped instructions | `scoped-guides` | reproduction of agent-specific precedence |
| policy checking | ast-grep / Semgrep etc. | `policy-check` | AST / dataflow / taint / semantic rule engine |
| canonical templates | Copier / Cookiecutter | `template` | Jinja2 compatibility / Copier update algorithm |
| source / semantic index | SCIP / Universal Ctags | `structure-index` adapters + portable language analyzers | full SCIP compiler/indexer reimplementation |
| syntax health | Tree-sitter | existing Tree-sitter integration where available | automatic grammar/runtime installation |
| Git repository health | git-sizer | `git-history-health` adapter/fallback routing | full Git object analyzer reimplementation |

### Decision rule

```text
external backend already available and higher quality
  -> reuse it

not installed / portable environment
  -> use repository-local fallback

task requires unsupported semantic/deep feature
  -> explicitly escalate to external backend

backend unavailable
  -> do not auto-install; keep the result unavailable / approximate / unverified
```

This table is not a promise to replace external tools. It defines the responsibility boundary of this repository. Do not add new tools that duplicate an existing fallback, and do not pursue full compatibility by default.
