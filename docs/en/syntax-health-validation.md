# Use Syntax Checks as an Initial Check

> Japanese Source of Truth: [構文チェックを最初の確認に使う](../jp/構文チェックを最初の確認に使う.md)

A syntax check verifies that code follows the writing rules of its programming language. Run it after a change to catch simple mistakes, such as a missing bracket or punctuation mark. You only need to inspect the reported problems, so the AI does not need to read a list of every healthy file or the full parser output.

## Example: Changing a condition

Suppose a discount condition changes from `price > limit` to `price >= limit`. A syntax check can confirm that the edited expression is written correctly. It cannot determine whether the new condition matches the requirement at the boundary value or whether it affects other behavior.

First use the syntax check to catch writing mistakes. Then check the requirement with a test that includes the boundary value or another suitable verification. Passing the syntax check alone does not prove the change is correct.

## Checking syntax and checking behavior

A parser reads source code according to the language's grammar and reports writing errors, such as a missing closing bracket or an expression in the wrong place.

Correct syntax does not prove that a called function exists, types match, calculations meet the requirement, or the program behaves as expected at runtime. Use the checks appropriate to the change, such as a compiler, type checker, tests, or a runtime check.

## How to use the result

Run the syntax check on changed code. If it reports a problem, inspect and fix the reported file and nearby lines. If it reports none, record that result and continue with the tests, compilation, or other checks the change requires. If the checker is unavailable or does not support the target language or version, do not treat that as a pass. State the limitation and use an existing verification method. There is no need to install a checker solely for this step.

For a small change where the normal compiler or tests run quickly, use those directly instead of adding a separate syntax-only step. A syntax check is an early signal, not a completion decision.

## Example request to the AI

> Run a syntax check only on changed files and report problem lines and errors. Do not treat a pass as behavior verification; also run tests or a build that checks the completion criteria. Show the commands and results.

## Optional tools and terminology

Use [syntax-health](../../tools/common/small/syntax-health/README.md) when a compatible parser is already available. This check is called a **Syntax Health Check** or syntax check.
