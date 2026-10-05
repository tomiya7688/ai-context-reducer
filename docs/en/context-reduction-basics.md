# Context Reduction Basics

> Japanese Source of Truth: [コンテキスト削減の基本](../jp/コンテキスト削減の基本.md)

Here, **context** means the instructions, code, documents, search results, and check results an AI receives to complete a task. Reducing context means keeping the evidence needed for the task while leaving out information the task does not use.

Leaving out needed evidence can cause mistakes. The goal is not to make every prompt short, but to decide what to search, select, and verify in the original sources. Unrelated source files and full logs still count as input, leaving less context available for the requirements and errors that matter.

## Example: improve an error message for a configuration file

Suppose you want the application to explain why it could not load a configuration file. If you give the AI the whole project, it has to search through screens, configuration loading, logging, tests, and many other files to find the change.

The requester first searches for candidate files or functions and finds the configuration loader and a related test. Give the AI those two locations and the change requirements instead of the full candidate list. Ask it to check the original source and test, and expand the scope only if another affected area appears.

```text
change request
  -> find the related implementation and tests
  -> read the relevant source code
  -> make and verify the change
```

This lets work begin without loading the entire project first. A list or pointer helps locate what to read; implementation decisions and verification still rely on the original source and tests.

## How to give the information to an AI and check its work

Put recurring instructions in the instruction file or settings that the AI tool actually reads. Whether a tool loads a file automatically depends on its configuration, so check that setting. For a one-time task, name the method guide and target locations directly in the request.

```text
Fix the configuration error message.
First find candidate locations for the configuration loader and its related test, and report the paths and why they are relevant.
Read the selected original code and test, make the change, and run the related test.
Expand the scope if you find another affected area.
At the end, report the files read, checks run, results, and anything not verified.
```

Compare the reported files and checks with the visible work log and diff. If the environment does not show read activity, the AI's report alone cannot prove how much it actually read. In that case, check that it followed the candidate-to-source process and did not skip required tests. If the environment measures tokens, compare similar tasks before and after adopting the method.

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

## Optional tools and terminology

Choose optional search, indexing, task-note, and validation tools from the [method and tool map](tool-method-map.md). Start with existing search and short instructions; add a tool only if repeated work remains. This approach may be called **context engineering** or **context routing**, but this repository explains the concrete steps for what to read and provide.
