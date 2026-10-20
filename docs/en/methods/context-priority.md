# Choose which files to read
> Japanese version: [今回読むファイルを選ぶ](../../jp/手法/今回読むファイルを選ぶ.md)


If you do not know which file to change yet, you still do not need to read every file in the project. Start with the ones related to the task.

## Example: saved data will not load

To fix this problem, start by checking:

1. The code that loads the data
2. A check that saves and then reloads the data
3. A document describing the saved data
4. Other code that uses the data, if needed

The largest file in the project might display the screen. If it is unrelated to this problem, you do not need to read it.

## When you find a large file

Do not start by reading the whole file. Narrow down what you need:

1. Search for a related name or phrase.
2. Read the matching part and the text around it.
3. Read more only if that is not enough to decide what to do.

If the information you need is in a large file, do not skip it just because of its size. Find and read the relevant part.

If the selected text itself exceeds a single-read limit, see [Split long files and logs into parts for the AI](splitting-long-files-and-logs.md) for boundaries and coverage records. File selection and transferring the selected text are separate steps.

## Tell the AI what to do

```text
Start with the code, documents, and tests most closely related to this task.
For a large file, search for a relevant name or phrase and read that part with its surrounding lines.
Broaden the search only when the available information is not enough to decide.
```

## Why this reduces context

Do not direct the AI to a huge file just because it is easy to find. If useful information is inside a large file, have it search first and then read the relevant part without skipping necessary details.

## Terms

- **Context Priority**: Deciding what to read first, starting with what relates to the change.

## Optional helper tools

- [context-budget](../../../tools/common/large/context-budget/README.md) estimates the size of candidate files, which helps you estimate how much you will read.
- [hotspot-report](../../../tools/common/large/hotspot-report/README.md) finds large or deeply nested files. Both only help you choose investigation candidates; size alone does not show relevance.
