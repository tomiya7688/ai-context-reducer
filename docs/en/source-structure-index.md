# Source Structure Index

> Japanese Source of Truth: [コード構造の索引](../jp/コード構造の索引.md)

When locating processing to change in a large program, you can use a searchable list of function and type definitions and their users. Have the AI narrow candidates with the list, then inspect their code and tests to limit unrelated files read up front.

The list is a guide to sources. Have the AI check that it matches current code before deciding how to change behavior or what to verify.

## Example: change what happens when a settings file is missing

Suppose a fictional settings app should use defaults when its settings file is missing. The following paths and function name are illustrative.

```text
Settings-loading function: load_settings
Definition file: src/settings.py
Candidate user: app.py
Candidate related tests: tests/test_settings.py
```

First have the AI inspect the definition in `src/settings.py`, its use in `app.py`, and expectations in `tests/test_settings.py`. Add settings screens or unrelated libraries only when evidence establishes a necessary relationship.

For example, although the list points to `app.py`, the current use might have moved to `src/startup.py`. Do not choose a change location from a reported line number or function name alone; use the following comparison procedure.

## When to use it

An index helps when you repeatedly locate the same functions in large files or rediscover callers, dependencies, and tests after each change. Ordinary search is sufficient for a small task whose change location and checking procedure are already known.

Reuse definition and reference results available in your existing development environment. Do not introduce a new index if recreating it costs more effort than it saves.

## Information the list may contain, and its limits

For example, a list may contain the following. Availability depends on the analysis method.

- File, type, and function names and definition locations
- Functions called by a function, or places that call it
- Imports between files or modules
- Leads for locating related tests

Lists can retain old locations or omit relationships. Selecting functions by names in configuration or generating code at runtime can create relationships analysis cannot detect. **Absence from the list is not evidence of no relationship.**

## Compare the list with current code

Have the AI follow this order. You can use the same steps when investigating yourself.

1. **Open definitions.** Open the actual function or type at the reported path and inspect its current name and processing. If lines have shifted, search for the current definition. When names are shared, distinguish candidates using their file, containing type, inputs, and return values.
2. **Open users.** Check which definition is actually imported, what is passed, and how return values or errors are handled. A matching name does not establish that the same function is used.
3. **Open related tests.** Inspect inputs and expected results and establish that the tests cover the target behavior. Similar filenames alone do not establish relevance.
4. **Add missing relationships.** When you find callees, shared processing, configuration, or other users, add the necessary definitions and related tests to the investigation. Record omitted relationships with paths and evidence. If the index can be updated, recreate it from its underlying information or current code.

For the settings example, compare:

| Location to open | What to check | When another relationship appears |
| --- | --- | --- |
| `src/settings.py` | Whether a missing file produces an exception or defaults | Follow the definition if loading delegates to another function |
| `app.py` | Whether it uses the intended `load_settings`, and how it handles exceptions or defaults | Inspect the new location if use has moved; include other affected users |
| `tests/test_settings.py` | Inputs and expectations with a present or missing file | Report a verification gap if no test covers a necessary condition |

Reading tests establishes their written expectations. Current success requires execution results. Leave unresolved definitions or users unverified too; do not have the AI infer cause, impact, or safety from the list alone.

Expand scope for concrete gaps: behavior delegated elsewhere, changed expectations of another user, or missing tests for a required condition. Have the AI find sources that address that gap instead of adding unrelated files to compensate.

## Where to provide the guide and an example request

For a one-time task, attach relevant list entries and the change goal, then request the comparison steps above. For an AI that can open files, specify the index location and code paths. For a chat that cannot, attach or paste necessary candidate code and tests too. Paths alone do not supply contents.

For recurring use, put the index location and update procedure in existing development guidance. An example new guide location is `docs/how-to-find-code.md`; link it from instructions the AI reads with the condition “when locating definitions or users.” Check whether files such as `AGENTS.md` load automatically in your environment.

```text
I am considering changing settings loading to use defaults when the settings file is missing.
From the attached list, find candidate definitions, users, and related tests for load_settings.
Open actual definitions and users and check inputs, return values, and error handling.
Open related tests and inspect the target conditions and expected results.

If you find unlisted callees or users, add their code and related tests to the investigation.
Report stale paths, missing relationships, and unresolved locations with evidence.
First propose change candidates and necessary checks; do not infer cause or impact from the list alone.
Separate sources read, checks executed and their results, and unverified points.
```

## Why this can reduce reading

Following candidates can avoid having the AI open every file to infer definitions and relationships. Comparing candidates with code and tests can help avoid edits based on stale guidance or another function with the same name, and subsequent reinvestigation.

Creating, updating, and checking an index also costs effort. Preserve necessary code and tests and add sources when evidence establishes a relationship. A short list alone does not prove lower usage; compare read records or measured input usage when available.

## Supporting tools

- [source-structure-index](../../tools/common/large/source-structure-index/README.md): Combines existing analysis results and returns candidate definitions, references, and dependencies by name or changed file. It can extract relevant surrounding information. Relationships depend on the underlying analysis; complete caller information is not always available.
- [Tree-sitter](https://github.com/tree-sitter/tree-sitter): Inspects code syntax and can provide material for locating definitions.
- [SCIP](https://github.com/scip-code/scip): A format and tooling for sharing indexes of definitions and references. It can support reuse of existing analysis results.

## About this method

A searchable list of code definitions and reference relationships that directs readers to original code is called a **Source Structure Index**, or symbol index.
