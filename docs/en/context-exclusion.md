# Decide Which Files to Skip by Default

> Japanese Source of Truth: [ふだん読まないファイルを決める](../jp/ふだん読まないファイルを決める.md)

This method keeps files unrelated to a task out of the places an AI checks first. For example, leaving out build output that can be recreated from source and old logs helps the AI find the code and tests it needs. Pair every exclusion with a reason and a note about when the files should be read.

## Decide what to leave out

Do not decide by file or folder name alone. Check:

1. Will this file help make or verify a decision for the current task?
2. If not, can the same information be found in source code, configuration, or another location?

For a routine feature change, you might leave out files under `build/` or `dist/` that can be regenerated from source, recreatable caches, and old logs unrelated to the task. Copies of external libraries can also be left out of the initial candidates when the task does not involve changing or investigating them.

Tests, configuration, specifications, input data, and dependency lists may be needed depending on the task. Do not exclude them permanently just because a name contains `generated`, `vendor`, or `lock`. If you do not know how a file is used, leave it available until you can decide whether it is needed.

## Tell the AI what to skip

Write the decision in an instruction file the active AI tool actually reads. If the project already has an `AGENTS.md`, `CLAUDE.md`, `AI_CONTEXT.md`, or similar guide, confirm the tool reads it before adding the rule; do not create a duplicate. Put exclusions that apply to every task in the root guide. If an exclusion belongs only to a repeated workflow, use that workflow’s Skill when supported. File names, locations, and automatic loading vary by tool; see [Hierarchical Context](hierarchical-context.md) for how to check them.

For example, state the normal scope, the paths to skip, and the exceptions:

```text
For routine code investigation, leave build/, dist/, and .cache/ out of the initial file search.
If the task changes or investigates these outputs, or checks a build or release package, read only the files needed for that task.
```

This saves you from repeating the same exclusion in every task. However, a note in a guide does not restrict file access. If the AI must be unable to read those paths, configure file exclusions or access controls in the AI tool or editor, if it provides them. Check whether a setting only hides paths from search and indexing or also blocks direct file access; the behavior depends on the tool.

An exclusion passed to a search command affects only that command's results. `.gitignore` tells Git which files not to track; it does not prevent an AI or search tool from reading them. You do not need to delete files or change Git settings for this method.

## When an excluded file becomes relevant

When investigating a failed build, read the log lines related to that failure. When checking a release package, inspect the package contents. Fixing a generated-file problem may require checking both the source that creates the file and the generated result.

If an excluded path becomes part of the task, temporarily remove it from the guide or tool exclusion, or explicitly ask the AI to read the needed files. Restore the normal exclusion after the check. The rule sets initial search candidates; it is not a reason to ignore evidence needed for the task.

For a small project, one short paragraph in the AI guide is enough. Add file exclusions in the AI tool only when there are many paths and you keep having to specify them by hand.

## Example request to the AI

> Check which exclusion rules and exceptions apply to this task. Name the skipped paths and why, and make sure required logs, generated artifacts, or tests are not excluded. Distinguish hiding search results from blocking direct file access.

## Optional tools and terminology

[ignore-candidates](../../tools/common/medium/ignore-candidates/README.md) only suggests paths to review. The policy for excluding initial reading candidates is called **Context Exclusion** or ignore rules.
