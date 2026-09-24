# External Tools

> Japanese Source of Truth: [外部ツールの使い方](../jp/外部ツールの使い方.md)

`ai-context-reducer` does not reimplement work unnecessarily when an existing high-quality external tool can provide it.

The goal is not to increase the number of tools. The goal is to reduce how much information the AI must read. When a suitable external tool is already available, it may be preferred over a simpler repository-local analysis.

## Recommended tools

| Tool | Main use | Good fit | Role in ai-context-reducer |
|---|---|---|---|
| `ripgrep (rg)` | fast text search | almost every repo | optional backend for `text-search` |
| `fd` | fast file discovery | repositories with many files | optional backend for `path-find` |
| `ast-grep` | AST structural search / outline | medium-large, multi-language | backend for `structural-search` / Source Structure Index input |
| `Universal Ctags` | multi-language symbol index | medium-large, multi-language | existing symbol backend for `source-structure-index` |
| `SCIP` | semantic code-intelligence index | repositories already able to produce a semantic index | symbol/dependency backend for `source-structure-index` |
| `Tree-sitter` | syntax-tree generation | when building precise analysis | common parser foundation; avoid low-quality reimplementation |
| `scc` | LOC / language / complexity overview | repository analysis before adoption | optional aggregate backend for `repo-profile` / `repo-stats` |
| `git-sizer` | Git history / repository size health | very large or long-lived repositories | machine output compressed into findings by `git-history-health` |

## Choosing tools

### Almost every project

For Search-first / Read-second, begin with `text-search` and `path-find`.

```text
text-search -> reuse rg if available -> otherwise portable fallback
path-find   -> reuse fd if available -> otherwise portable fallback
```

The caller does not need to learn each external backend's output format. Both tools normalize results to the same self-describing JSON contract and use `backend` only to state which implementation actually ran.

If an external tool is simply absent, use the portable backend normally. Report fallback information only when a backend was found on PATH but failed during execution.

### Medium to large codebases

When symbol lookup is common, prefer Universal Ctags. When syntax-shaped search is needed, consider `ast-grep`.

`source-structure-index` can import existing Universal Ctags JSON Lines through `--ctags-json` or run an already-installed Universal Ctags through `--ctags-source`. Do not pass the full tag output to the AI; normalize it to file / symbol / scope ownership and reuse it through `query` / `expand`.

When a SCIP index exists, import it through `--scip` / `--scip-json` into the same common IR. Because SCIP can include cross-file dependencies, it may provide higher-precision evidence for `affected` routing than Ctags alone.

Use `ast-grep` as a high-quality backend for `structural-search`, and its outline JSON may also be used as Source Structure Index input.

Keep regex/stdlib-based tools as dependency-free fallbacks. Do not auto-install external tools.

### When building custom analysis

For accurate multi-language analysis, Tree-sitter is a candidate foundation.

Do not add large parser runtimes or many grammars merely to adopt the method in a small repository. Reuse an existing parser/indexer when available and avoid duplicating another multi-language parser inside Context Reducer.

### Repository size and language statistics

`repo-profile` uses a portable scan to collect total file count, size class, and top-level directories. When `scc` is available, it can add language LOC/complexity as supplementary information.

`repo-stats` / `acr-toolbox stats` focuses on language/line statistics. Reuse scc aggregate JSON when available and do not send per-file details into AI context. If scc is absent, use the portable Python/Go implementation.

This avoids making the agent learn scc-specific JSON or read large raw output.

### Very large repositories / long Git history

Use `repo-profile` / `repo-stats` for current source volume and language composition. Treat Git history and large objects as a separate concern through `git-history-health`.

```text
git-history-health -> git-sizer --json -> return only findings with concern >= threshold
```

`git-history-health` does not send raw git-sizer JSON to the AI. It compresses it to `metric / value / level_of_concern` plus the necessary description/object path. Saved git-sizer JSON can be normalized through `--json-input`.

If `git-sizer` is absent, do not build a low-quality Git object-graph analyzer or auto-install it. Return `external_backend_unavailable`.

For large repositories, keep "current source volume" and "Git history weight" as separate dimensions.

### Repositories with many policies

Move mechanically decidable policy into the repository's standard lint/checker and pass only success results or compact findings to the AI.

Keep semantic ownership and design-responsibility rules that are difficult to automate as targeted review.

## External tool detection

`tools/common/small/external-tool-probe/script/external_tool_probe.py` can report whether representative tools are on PATH.

```text
python tools/common/small/external-tool-probe/script/external_tool_probe.py
```

Do not install missing tools automatically. Adopt them only after considering the target environment, CI, and developer policy.

## Principles

- do not use an external tool when adopting it creates too much burden
- prefer existing repository-standard tools
- do not leak raw external-backend output to callers; normalize it to a stable compact contract
- keep external tool output bounded / compact
- treat analysis results as an index to original sources, not as the Source of Truth
- when a high-quality external index/parser can be reused, do not build another implementation of the same analyzer
