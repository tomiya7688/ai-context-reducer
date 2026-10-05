# Read What Relates to the Change First

> Japanese Source of Truth: [今回の変更に関係するものから読む](../jp/読む候補の優先度を付ける.md)

When there are many possible files to inspect, choose the reading order by how closely each one relates to the task, not by its size or how often it changes. Starting with the relevant implementation, tests, and specification helps you avoid unrelated large files and history and reach the needed information sooner.

## Example: changing the CSV date format

Suppose CSV output dates must change from `2026/10/05` to `2026-10-05`. Start with the code that writes the date and the test that checks its format. Check the format specification if one exists. Even if the application's largest file is a screen that changes frequently, do not add it to the reading list when it has no connection to CSV output.

The date-writing code may be inside a large file, but you do not need to read the whole file first. Find the date-handling function, its callers, and related tests. Read the surrounding parts needed to decide, and widen the search only when information is missing.

## Choose what to read first

Use the task's goal and completion conditions to identify the implementation and tests that directly relate to the change. If the change affects a format or calling convention used by other components, include that agreement and its consumers. File size and past change frequency do not determine whether a file is relevant.

Size can help decide **how much** of a relevant file to read, not whether to read it at all. In a large relevant file, use headings, function names, or search terms to find the necessary section. A small file that defines the current requirement or contains the direct test may deserve attention first.

## When to expand the search

Read more files when you discover an effect on another feature, a conflict between the specification and code, or an unexpected test failure. Inspect what is needed to understand the cause. High change frequency or large size alone is not a reason to read history or broad documentation.

Small tasks with an obvious target and verification method do not need a separate ranking or analysis. Prioritization is useful when there are many candidates and it is unclear which ones matter to the current decision.
