# Source Structure Index

> Japanese Source of Truth: [コード構造の索引](../jp/コード構造の索引.md)

This document defines a standard approach for reaching the necessary source areas through structured analysis results before reading full source files.

The important idea is not a particular implementation. Reuse structural information such as symbols / ownership / dependencies as an index so that the agent reads only the necessary original sources.

## 1. Source Structure Index

In a large codebase, use a code-structure index before making the AI read every file.

Possible index contents:

- module / file
- class
- function / method
- qualified name
- source line range
- parameters
- parent / ownership
- calls / called-by
- import / dependency
- responsibility summary

The goal is not to replace code with prose summaries. It is to create a mechanical map for reaching the necessary original source.

## 2. Separate language-specific parsers from the common IR

```text
Source Code
    ↓
Language Parser / AST Adapter
    ↓
Common Intermediate Representation
    ↓
Relationship / Flow Analysis
    ↓
Context Routing / Diagram / Evaluation
```

AI Context Reducer does not need to own parsers for every language. Analysis may come from project tools, external tools, an IDE, static analyzers, or another source.

When a semantic index already exists, prefer reusing it over reparsing source. For example, if a repository already generates SCIP, do not duplicate a SCIP protobuf parser inside Context Reducer. Use an available official CLI or existing export as a boundary adapter and convert only routing-relevant information into the common IR.

```text
existing semantic index
    ↓
small boundary adapter
    ↓
Common IR
    ↓
query / expand / affected
```

The goal is still not to pass the whole external index to the agent. Internal analysis may be broad; agent-visible results should remain bounded.

## 3. Reuse analysis results

From a common IR or structure index, derive information such as:

- call graph
- dependency graph
- class / module relationships
- responsibility table
- sequence candidates
- fan-in / fan-out
- cycle detection
- task-specific working set
- affected scope from changed files

Reuse these results as an index instead of making the AI reread the same code repeatedly.

## 4. Graph-based context expansion

```text
Target symbol
  -> direct callers / callees
  -> directly dependent modules
  -> matching tests
  -> deeper relationships only if needed
```

Prefer bounded traversal when exploration depth can be limited.

Do not confuse the internal dependency closure required for impact correctness with the agent-visible result limit. To avoid false negatives, a tool may compute all transitive dependents internally while returning only a bounded subset.

## 5. Fan-in / Fan-out

Fan-in / fan-out can support change-impact analysis, dependency candidates for a Context Pack, high-risk-change detection, and identification of central nodes.

Do not use the numbers alone to declare design quality. Treat them as supporting information for read priority.

## 6. Cycle detection

For a change involving a dependency cycle, do not judge only the target file. Treat the elements in the cycle as one working set when appropriate.

## 7. Generated diagrams are derived from the index

Prefer the underlying structural data over the diagram itself.

```text
Common IR / Structure Index
  -> compact relationships
  -> diagrams when useful
```

## 8. Prefer deterministic analysis

For ASTs, symbols, call relationships, dependencies, and other mechanically obtainable information, prefer deterministic analysis when possible.

When LLM-assisted analysis is used, distinguish it from deterministic results.

## 9. Existing tools and repository-owned implementation

Concrete external examples include:

- [SCIP](https://github.com/scip-code/scip): a language-agnostic code-intelligence index protocol / CLI. For languages with compatible indexers, definition / reference information can be reused.
- [Tree-sitter](https://github.com/tree-sitter/tree-sitter): an incremental parsing library supporting many languages, useful for lightweight syntax extraction and custom language adapters.

When an IDE / language server / build system already provides equivalent information, prefer reusing it.

### Repository-owned minimal implementation

This repository provides `tools/common/large/source-structure-index` as a lightweight common-IR / routing layer.

It does not reimplement SCIP or Tree-sitter. It normalizes symbol / dependency graph JSON from existing language-specific analyzers, `ast-grep outline`, existing SCIP indexes, and similar sources into a common IR. The full index is written to a file; the agent receives only required parts through `query` / `expand` / `affected`.

The current minimal implementation handles:

- file / module / symbol nodes
- ownership / dependency edges
- exact / partial node query
- bounded in/out/both traversal
- fan-in / fan-out
- cycle groups within the traversal scope
- reverse-dependency affected scope from changed files
- propagation of input-side truncation
- explicit external-backend-unavailable / malformed-output states

Python outputs from `python-symbols` / `python-module-graph` and Go outputs from `go-symbols` / `go-package-graph` can be used directly as inputs. Existing SCIP indexes can be read through the external boundary when the SCIP CLI is available. The CLI or indexer is not auto-installed.

Only link external tools that satisfy [External Tool Reference Policy](external-tool-reference-policy.md).

This positioning preserves the following:

- the repository-owned implementation is not a condition for the standard method
- the standard does not depend on a particular CLI or file format
- changes in external projects are not adopted automatically
- new methods are generalized separately before becoming standard
- the same standard can be satisfied by another implementation

## 10. Standard recommendations

- use a structure index before full-source reading when one is available
- separate language-specific parsers from the common IR
- prefer reusing an existing semantic index over reparsing source
- reuse the same analysis results for multiple purposes
- expand around a target symbol with bounded graph traversal
- separate internal closure required for impact correctness from agent-visible output bounds
- use fan-in / fan-out / cycles as supporting read-priority signals
- do not use generated diagrams as replacements for original sources or the IR
- prefer deterministic analysis for mechanically obtainable information
- prefer reuse of a high-quality existing code-intelligence/parser implementation over building another analyzer
