# Use External Tools to Reduce Investigation

> Japanese source of truth: [外部ツールの使い方](../jp/外部ツールの使い方.md)

External tools are existing programs that handle recurring work such as searching or inspecting code structure. If a suitable tool is already available, consider using it before building a simpler version of the same feature. The AI can read only the relevant results instead of the full search output, reducing unrelated material in its context.

## Example: Investigating CSV date handling

For a small change, searching for `date` or a function name may be enough to find the CSV conversion code. If a search tool is already available, there is no need to build another search program.

In a large repository, a recurring task such as “find every use of this function and its tests” may benefit from an existing symbol index or dependency analyzer. Use its results to select relevant files and tests, then verify those sources directly. The AI does not need to read a huge search result or the full index; it can move from candidate discovery to the actual task sooner.

## Choose a tool

First decide what you need to find accurately and quickly. Examples by purpose:

| Need | Examples | How to use the result |
| --- | --- | --- |
| Find text or a setting | Full-text search such as `rg` | Read matching lines and nearby context |
| Find files by name or path | File search such as `fd` | Select paths that match the task |
| Find functions, types, or syntax patterns | `ast-grep`, Universal Ctags | Open candidate definitions and usages |
| Find dependencies between files or features | Existing structure index or project dependency data | Check consumers and related tests |
| Summarize lines, languages, or Git history size | Tools such as `scc` or `git-sizer` | Inspect relevant findings rather than every detail |

These names are examples. Prefer a search, index, analyzer, or build tool that the project already uses if it meets the need. Do not install a tool just to discover tools; weigh its adoption, updates, and CI maintenance against the benefit.

## Reuse an existing tool

Check that the tool handles the relevant language or file format accurately, is maintained, and can run in the project environment. If the project already manages builds or dependencies, avoid duplicating the same analysis elsewhere. A mature index or analyzer may find consumers that a simple custom script would miss.

A tool helps find candidates, but check that its results match the current source and tests. If its index is stale, its scan was cut short, or it does not support the target language, do not conclude from its output alone that there is no other impact. Supplement the search or inspect a broader area.

## When not to add one

Do not add an external tool when ordinary search finds the target in a small repository, the task is one-off and setup is substantial, or adoption would require a new runtime or ongoing maintenance. Use a command-line or IDE feature already available if it is sufficient.

Do not install missing tools automatically. If a change to the environment or CI is needed, the people responsible should first check usage conditions, installation, and licensing. Before recommending a specific product for the project, also check the [External Tool Reference Policy](external-tool-reference-policy.md).

## Keep results small and useful

When output is large, show only the matches, summaries, or warnings needed for the current question. Make clear which tool ran, what it searched, and whether results were truncated. Do not stop internal analysis required for correctness just to reduce the amount of output.

Analysis results are pointers to original sources. Check the formal specification for requirements and current code or tests for behavior. If tool output conflicts with its sources, investigate the source of the mismatch instead of trusting a stale index or an incorrect candidate.

## Implementations in this repository

This repository also has helpers for searching, finding files, inspecting code structure, and summarizing repository statistics. Their supported tools, commands, configuration, and output formats belong in their individual READMEs. The method works without a particular tool, using available commands or manual search.

- [source-structure-index](../../tools/common/large/source-structure-index/README.md)
- [affected-tests (Python)](../../tools/python/medium/affected-tests/README.md)
- [affected-tests (Go)](../../tools/go/medium/affected-tests/README.md)

## Example request to the AI

> Choose an available search or analysis tool that fits the task. First report what it searched, whether results were truncated, and only relevant candidates with reasons. Open candidate source files and tests to verify them; do not paste the full output or index.

## Optional tools and terminology

See the [method-to-tool map](tool-method-map.md) and each tool README for implementations by purpose. Using a tool to find candidates and then checking original sources is called **tool-assisted search** or bounded output.
