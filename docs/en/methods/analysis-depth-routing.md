# Choose a language-appropriate method when analyzing code

> Japanese version: [コードを解析するときは、言語に合った方法を選ぶ](../../jp/手法/コードを解析するときは、言語に合った方法を選ぶ.md)

When asking AI to inspect code, choose the depth based on what you need to know, not only on the language. Start with a simple check, then move to a deeper one if it cannot answer the question or establish correctness.

## Choose based on what you need to know

| What you need to know | Start with | If that is not enough |
| --- | --- | --- |
| Where a file or operation is located | Search for its file or operation name | Search for related terms and callers |
| Where the changed operation is used | Inspect links between functions or files | Open the actual code and callers to verify |
| Whether the code is valid for its language and settings | Use a syntax check for that language | Build or check types using the project settings |
| Whether it behaves as expected when run | Run related tests | Run the app if tests cannot reproduce the behavior |

For example, search is enough when you only need to locate an operation. Checking types or project settings requires a method that understands the language or project. To verify behavior that users can observe, go beyond reading code and run tests or the app.

## Match the available environment

Prefer search, editors, compilers, and tests that are already available. A compiler turns a program into a form that can be run and reports problems with its syntax or types. If the needed tool is unavailable, inspect what search can establish and state that a build or run could not be checked. Before adding a large development environment just for one task, compare the required check with the installation and maintenance cost.

Before passing results to the AI, keep only what is needed. Provide relevant problem locations, test results, and unchecked conditions instead of a complete list of successful files or a long log.

Lightweight analysis may work without a runtime or compiler, but it only suggests where to look. It does not confirm behavior, types, or build correctness. A deeper analysis is not always better: stop when you have the evidence you need, and do not hand the AI the full output. In a small project where the target and tests are already known, skip the dedicated analysis and read the source.

## Example instruction for the AI

```text
Start with the simplest method that can answer what this task needs to know.
If you only need to locate code, search. If you need to know how an operation is connected, check its callers.
Use an available language-specific check for syntax or types, and related tests or execution to verify behavior.
If a suitable check is unavailable, do not assume it passed; report what you learned and what remains unchecked.
Limit the results to the parts relevant to the change.
```

## Why this reduces context

When search can answer the question, do not give the AI a project-wide analysis or long build output. If search cannot establish correctness, ask it to inspect code connections, run language-specific checks, or execute the relevant tests in order. This keeps results focused without skipping necessary checks.

## Optional helper tools

- [language-setup](../../../tools/common/small/language-setup/README.md) checks the project's languages and the runtimes you can use, and suggests what to run.
- [language-run](../../../tools/common/small/language-run/README.md) runs the matching lightweight analysis and saves the result to a file. Give the AI only the candidates the current question needs, not the whole result.

## Terms

- **Syntax check**: A check for obvious mistakes in how a program is written. It does not establish runtime behavior.
- **Type check**: A check that values such as numbers and text are used consistently as they pass between operations.
- **Compiler**: A tool that transforms a program into a runnable form and reports syntax or type problems.
- **lightweight search / dependency analysis / language-specific analysis**: Finding locations by name, analyzing references and dependencies between files, and inspecting code with a language's own tools such as its compiler.
