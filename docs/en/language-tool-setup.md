# Choose an Analysis Method for the Language

> Japanese Source of Truth: [言語に合った解析方法を選ぶ](../jp/言語に合った解析方法を選ぶ.md)

Choose analysis depth based on the question. An analyzer may inspect a wide area, but if you give the AI only the needed locations or diagnostics, it does not need to read every source file or full log. Context is reduced by using results to find candidates and passing only the relevant originals, not simply by running an analyzer.

## Example: changing CSV import in a large application

Suppose you are changing CSV import in an application written in Python and Go. If you do not know where to start, first locate candidate files and functions. Add relationship analysis or build checks only when you need to know the impact or whether the project builds.

## Choose the depth based on what you need to know

| What you need to know | Analysis or check | What to give the AI, and why it reduces reading |
| --- | --- | --- |
| Candidate files or functions | Lightweight file and symbol search | Give the candidate locations so the AI does not have to search every file. Check the implementation and tests in their original files. |
| Callers or affected areas | Cross-file references or dependency analysis | Give related locations and test candidates so the AI does not have to read all source files to find relationships. Read the selected originals; candidates alone do not prove behavior. |
| Types, build, or runtime result | The project's compiler, development kit, or runtime | Give pass/fail and relevant diagnostics so the AI can investigate without receiving the full log. |

A lightweight scan may work without a runtime, but it only points to locations; it cannot confirm behavior, types, or a successful build. Running Python or building C# may require a Python environment or the .NET SDK. Deeper analysis is not always better. Stop when you have the needed evidence, and do not pass every result to the AI.

## Use the environment already available

First check which languages and development tools are already available. If the environment is insufficient, use the available searches and analyses, and state which checks could not be performed. Do not automatically install a runtime or development kit solely for this investigation. If a small project has an obvious target and test, inspect the originals directly. Passing every result or the full log does not reduce what the AI reads.

For commands, output locations, and the exact behavior of each analysis stage in this repository, see the [`language-setup`](../../tools/common/small/language-setup/README.md), [`language-run`](../../tools/common/small/language-run/README.md), and [`acr-toolbox`](../../tools/common/native/acr-toolbox/README.md) guides.

## Example request to the AI

> Choose the analysis depth that answers this task and return only relevant candidates. Verify selected code and tests in their original files; do not pass every result or the full log. State which checks could not be run.

## Optional tools and terminology

Use [language-setup](../../tools/common/small/language-setup/README.md) to check available analysis and [language-run](../../tools/common/small/language-run/README.md) when a deeper check is needed. Terms: **lightweight search / dependency analysis / language-specific analysis**.
