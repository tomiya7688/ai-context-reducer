# Source Structure Index

> Japanese Source of Truth: [コード構造の索引](../jp/コード構造の索引.md)

A source structure index is a searchable list of where functions and types are defined, and how they call or depend on one another. Narrow candidates with the index before reading a large source file from beginning to end. The index is a way to find what to read, not a replacement for the original source.

## Example: change how configuration is loaded

Suppose you need to change how a configuration file is loaded. Search the index for the loading function, then follow its callers and the modules that use it. Related tests can also become candidates. First point the AI to the function and its direct relationships; read additional dependencies or tests when needed. This reduces the amount of unrelated screens and libraries read up front.

```text
behavior to change
  -> find related functions and types
  -> check callers and related tests
  -> read the necessary original code
  -> expand the investigation if the effects are broader
```

## What to put in the index

The index may record:

- file, module, type, and function names
- the file and line where each is defined
- functions it calls and functions that call it
- imports and dependencies between modules
- the responsibility of each file or module

If an IDE, language tool, or static analyzer already provides this information, reuse it. [Tree-sitter](https://github.com/tree-sitter/tree-sitter), which can inspect code syntax, and [SCIP](https://github.com/scip-code/scip), which shares indexes of definitions and references, are examples. You do not need to add a new environment just to introduce an analyzer.

## How to use the index

1. From the request, identify a name to search for or a changed file.
2. Use the index to find candidate definitions, callers, dependencies, and related tests.
3. Open the original files and confirm the actual behavior and relationships.
4. If the change affects shared code or a public specification, broaden the investigation and validation.

Even when the index returns many results, you do not need to send them all to the AI. Start with results directly related to the task. Once the needed references are clear, read the original documentation and source.

## When it helps, and its limits

An index helps when people repeatedly search large files for the same functions, or trace callers, dependencies, and tests after each change. For a small change where the relevant names and files are already known, normal search is enough. Do not add an index when generating and updating it takes more time than it saves.

An index only shows relationships the analyzer can detect. It may omit dynamic calls or generated code, and it may be out of date. Check the original code before changing it, and run the broader checks needed for changes to shared code or public specifications. Do not decide impact or safety from index results alone.

This repository's [source-structure-index](../../tools/common/large/source-structure-index/README.md) indexes where functions and types are defined, their callers and dependencies, then returns candidates related to a name or changed file. See its README for details. The same method can use a different index or search tool.

## Example request to the AI

> Query the index for the target function or type, its callers, and related tests. Return only candidates relevant to this change, with paths and reasons. Open the selected original code and tests, and report possible relationships the index cannot detect and anything not verified.

## Optional tools and terminology

Use [source-structure-index](../../tools/common/large/source-structure-index/README.md) or an existing language analyzer. Terms: **Source Structure Index** / symbol index.
