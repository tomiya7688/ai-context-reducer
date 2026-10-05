# Context Reduction Basics

> Japanese Source of Truth: [コンテキスト削減の基本](../jp/コンテキスト削減の基本.md)

When you ask an AI to do work, you provide instructions and may also provide source code, design notes, or test results. The information the AI reads for that task is its **context**.

Context reduction means keeping the information needed for the task while leaving out material that is unlikely to help. In a large project, finding the relevant files can take time. Sending the whole project for every task also buries useful details among unrelated material and makes the AI spend more effort deciding what to read.

## Example: improve an error message for a configuration file

Suppose you want the application to explain why it could not load a configuration file. If you give the AI the whole project, it has to search through screens, configuration loading, logging, tests, and many other files to find the change.

First make a list of files or functions, and use it to narrow the search to the configuration loader and the tests that cover it. Give the AI pointers to those locations and the relevant sections. During the change, have it check the original source and tests.

```text
change request
  -> find the related implementation and tests
  -> read the relevant source code
  -> make and verify the change
```

This lets work begin without loading the entire project first. A list or pointer helps locate what to read; implementation decisions and verification still rely on the original source and tests.

## Three ways to choose the information

### 1. Find mechanical facts before asking the AI to read

File names, function names, imports, and syntax errors can be collected in a consistent way by programs. Use those results to narrow the candidates before asking the AI to build such lists by reading large amounts of source code.

For example, finding tests related to changed files first can avoid reading every unrelated test. Mechanical analysis narrows the candidates; the AI still reads the implementation to understand the change and make design decisions.

### 2. Package steps that are repeated

If the same work follows the same order—find changed code, find related tests, choose the required checks—put the steps in a short guide or script. The AI can use the results and move on without rethinking the sequence each time.

There is no need to automate a one-time task or add a system whose setup and upkeep cost more than the repeated work it saves. Package a routine when the recurring effort is greater than the cost of maintaining it.

### 3. Read only the relevant parts

After locating the target, read the implementation, instructions, documentation, and tests that matter to the current decision. When using a short list or summary, keep a clear pointer to the file or record it came from.

Do not make a change based on a list or summary alone. Return to the original material to verify the relevant details. Leaving out necessary evidence reduces the amount of context but weakens the decision.

## When to use it, and when not to

Lists and short procedures help when work requires finding a target across many files or repeating the same checks. For a small change with an obvious target, read the relevant files directly instead of adding a formal list or dedicated system.

## Keep the work accurate

Correctly checking the necessary information matters more than minimizing what the AI reads. If the search stopped early or some files could not be read, state which parts were covered. Do not present a limited scan as though the entire project had been checked.

The [method index](method-index.md) describes the available methods and when they apply. Each method document explains its own adoption steps and suitable use cases.
