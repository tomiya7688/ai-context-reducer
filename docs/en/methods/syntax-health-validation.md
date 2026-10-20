# Start by checking code syntax

> Japanese version: [まず、コードの構文チェックをする](../../jp/手法/まず、コードの構文チェックをする.md)


Check whether the code is written in a form the language can read, and fix the files with reported problems. This is a quick check before tests or a build. Correct syntax alone does not prove that the program behaves correctly.

## When to use this check

Use it when the project already has a suitable checker and it runs faster than the build or tests. It can catch simple mistakes after editing many files or generating code.

If the project has no such checker, do not install a new development environment just for this step. Run the project's usual build or tests and report which checks were unavailable.

## Tell the AI what to do

```text
If a code-structure checker is already available for the changed files, run it.
Report how many files were checked and list any problem files and lines.
Do not treat a successful structure check as proof that the program works.
Also run tests or a build that match the change. Mark checks you could not run as unverified.
```

## What the result tells you

This check mainly finds mistakes in the way code is written. Use other checks for the following:

| Question | Check |
| --- | --- |
| Are data types and calls valid? | Compiler or type checker |
| Does the result follow the requirements? | Related tests |
| Can the app run? | Launch and operation check |
| Are the packaged files correct? | Check the files produced for delivery |

Even a “no problems” result is useful only if the changed files were actually checked. Report zero files, unsupported languages, and checker failures as unavailable checks, not as success.

## Why this reduces context

When the AI receives only the names and lines with problems, it can start with relevant code. It does not need the output for every clean file or a full inventory. Keep the later tests and build; summarize their results instead of passing along every log line.

## Terms

- **Syntax Health Check**: Checking right after a change that the code follows the language's writing rules. It does not confirm that the code behaves correctly; check behavior separately.

## Optional helper tool

- If useful, `syntax-health` lists files with problems using code parsers already available. Use it to check the syntax of multiple files. It does not install a parser.

Use the project's compiler or editor if it can perform the same check.
