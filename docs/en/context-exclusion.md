# Decide What Not to Read by Default

> Japanese Source of Truth: [ふだん読まないファイルを決める](../jp/通常は読まないものを決める.md)

For everyday changes, keep generated output, logs, copies of external libraries, and temporary files out of the AI's initial reading when they are unlikely to help with the task. This keeps implementation details and tests from being buried under unrelated material and reduces what must be read each time. This only sets the AI's normal reading scope; it does not delete files or change Git ignore settings.

## Example: fixing a calculation bug

For an incorrect result, start with the calculation code, its relevant tests, and the specification. Unless they matter to the task, do not read an executable from an old build, unrelated logs, copied external libraries, or temporary caches. The AI can focus on the implementation and tests instead of searching through a large amount of unrelated material.

When diagnosing a failed build, read the relevant error lines. When checking a release package, inspect the package itself. A generated file should be read when it becomes the task's target or necessary verification evidence; include only what is needed.

## Read these only when needed

Generated output is produced from other code or documents. Usually, begin with the source or code that creates it, but inspect the output when the result itself is under review. Read logs around the relevant failure or behavior. Inspect copied external libraries when changing them, investigating a security issue, or checking a license. Read a temporary cache when investigating a problem with clearing or rebuilding it.

## Take care when excluding files

Names such as `build`, `generated`, and `vendor` are not enough to decide that files can be skipped. A project may treat generated code as official input or need test data and release files to verify a task. Check whether a file is needed as an original source or verification material for the current task. If uncertain, leave it available as a candidate.

Telling the AI not to read a file by default is different from deleting it or changing `.gitignore`. Do not change files or repository settings based only on this guide. In a small project, a short note in the AI guide such as "Normally skip build output and caches" is enough.
