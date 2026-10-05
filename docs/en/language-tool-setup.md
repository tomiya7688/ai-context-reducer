# Choose an Analysis Method for the Language

> Japanese Source of Truth: [言語に合った解析方法を選ぶ](../jp/言語別ツールの選び方.md)

Code-analysis tools differ in what they can tell you, depending on the language and development environment. Start with tools already available to locate files and functions. Use deeper checks for dependencies or builds only when the task requires them. This helps reach relevant code without loading every file or installing development software at the outset.

## Example: changing CSV import in a large application

Suppose you are investigating a CSV import bug in an application written in Python and Go. Begin with a lightweight analysis to find the files and functions that handle CSV and their nearby names. Once you find the relevant code and tests, there is no need to read every other feature's source.

If the change may affect several features, inspect references between files or packages. If you also need to know whether the project builds or has type and dependency errors, use the compiler or development kit used by the project. Do not present something as verified when the lightweight analysis cannot establish it.

## Choose how deeply to analyze

A lightweight scan can locate files and functions, and may work without the language's runtime. It is a guide to where to read. It does not prove how the program runs or whether types and builds are correct.

Deeper analysis can inspect references between files and project settings. Checking actual build conditions or runtime behavior may require a compiler, development kit, or runtime for that language. For example, Python needs an environment to run the program, and building C# projects may require the .NET SDK. Requirements vary with the check being performed.

## Use the environment already available

First check which languages the project uses and which development tools are already available. If a required tool is missing, use the analysis and search that are available, and state which checks could not be performed. Do not automatically install a runtime or development kit solely for this investigation.

Inspect only the useful parts of analysis results. Once you find the relevant area, read its implementation and tests. Small projects with an obvious target and test do not need a separate analysis process. Reserve heavier analysis and broad indexes for large projects where you need to investigate wider impact.

For commands, output locations, and the exact behavior of each analysis stage in this repository, see the [`language-setup`](../../tools/common/small/language-setup/README.md), [`language-run`](../../tools/common/small/language-run/README.md), and [`acr-toolbox`](../../tools/common/native/acr-toolbox/README.md) guides.
