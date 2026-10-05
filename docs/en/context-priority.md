# Read the Files Needed for the Change First

> Japanese Source of Truth: [変更に必要なファイルから読む](../jp/読む候補の優先度を付ける.md)

Start with the files needed to implement the request and check the result. A file is relevant when it contains the behavior being changed, the rule that defines that behavior, or a test that checks it. If the change affects an external format or calling convention, include the code that uses it.

## Example: changing the date format in CSV output

If a request changes dates in CSV output from `2026/10/05` to `2026-10-05`, start with:

1. The code that turns the date into CSV text
2. The test that checks the output date format
3. The relevant part of a document or example that defines the CSV format, if one exists
4. The code that reads the CSV, if another program uses this format and will be affected by the change

You do not need to start with screen rendering, login behavior, or CSV input handling if those files are not needed to implement or check this output change. This smaller candidate list takes less time to search and gives the AI less unrelated material to read.

## Find the needed part in a large file

You do not need to read a large candidate file from beginning to end. Search for the date-writing function or terms such as `CSV` and `date`, then read that code, its callers, and the surrounding test. A small specification or direct test may be more important than a large file. Size and past change frequency alone do not determine whether to read something.

## When to widen the search

If a test fails, also inspect the failing behavior and the code that creates its input. If you find another program that consumes the CSV format, inspect that code too. If the specification and implementation disagree, find the source that determines which one is correct. Expand the candidate list only to understand a newly discovered effect or its cause.

For an obvious small change with a known target and check, there is no need to plan a separate reading order. Use this method when there are many candidate files and it is unclear which ones are needed to implement or verify the change.

## Example request to the AI

For a one-off task, attach this guide or name its path, then ask the AI to follow this order:

> Choose reading candidates from the requested behavior, its specification, and its tests. First list the paths and reasons. Include consumers if a format or API is affected. Check the selected original sources, then report files read and verification results.

## Optional tools and terminology

Use [context-budget](../../tools/common/large/context-budget/README.md) or [hotspot-report](../../tools/common/large/hotspot-report/README.md) to see candidate sizes if useful. Size does not determine relevance. This method is called **Context Priority**.
