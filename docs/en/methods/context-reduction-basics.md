# Three ways to limit what the AI reads
> Japanese version: [AIに読む情報を絞る3つの方法](../../jp/手法/AIに読む情報を絞る3つの方法.md)


Imagine asking an AI to fix a problem saving settings. If it reads every file in the project, unrelated screens and documents get in the way of finding the code that matters.

Choose the information the AI needs for the task. There are three ways to do this:

1. **Use tools to find facts before asking the AI to inspect them.**
2. **Write down repeated steps and reuse them.**
3. **Have the AI read only the relevant parts.**

## 1. Find facts with tools first

For a settings-saving problem, use search or development tools to find where the saving code lives, what calls it, and which tests cover it. Give the AI only the results needed for this task.

This saves the AI from reading every file and guessing names or connections. The results do not replace the code or tests: have the AI check those too before deciding how to make a change.

Checking code structure without running the program is a way to find where to look. It does not prove that the program works or builds correctly.

## 2. Write down steps you repeat

If you search, inspect related files, and choose tests in the same order each time, record those steps or make a small helper tool. Give the steps to the AI so you do not have to explain the process from scratch each time.

Do not add a process or tool if it creates more setup and upkeep than it saves. Use it when the same work happens often and recording it reduces effort.

## 3. Have the AI read only relevant parts

For a settings-saving change, start with the saving code and its tests. Look at unrelated screens or old records only if the task raises a reason to.

Use a short list or summary to find the files you need. When making a decision, check the actual documentation, code, and tests. Do not rely on a list or summary alone.

## How to give it to the AI and check

Put rules you reuse in the instruction files or settings that your AI actually reads. Whether it reads them automatically depends on the AI, so check its settings. For a one-time task, name the method page and the target directly in the request.

Compare the files and checks the AI reports with the activity record and the diff. If your environment does not show what was read, the report alone does not show that the amount read went down. In that case, confirm that you reached the needed sources from the candidates and did not skip needed tests. If your environment can count tokens, you can compare before and after on the same kind of task.

## When to use it and when to skip it

For a one-off fix where the file to change and its test are clear from the request, read them directly; you do not need an index or a dedicated guide. If you keep searching several features for the same kind of request, look at what you searched again recently and put it in a short list or procedure. The test is whether the searching and rereading you save outweighs the effort of writing and updating the list. See [Choose only the methods you need](../adoption/adoption-priority.md) for examples.

## When choosing a method or tool

Check whether it reduces any of these:

- facts the AI used to guess from code
- steps the AI had to repeat
- files or documents the AI did not need to read

If it does not reduce any of them, reconsider whether it will save effort. For a small project, search and a short guide may be enough.

## Keep the work accurate

The goal is not to make the AI read as little as possible. Give it the information needed to do the work correctly, and leave out what is unrelated. Do not remove evidence needed to make a sound decision.

## Tell the AI what to do

```text
Confirm the task goal and how to tell when it is done. Start with related code, documents, and tests.
Search further only when a question needed for the change is unanswered.
Report what you checked and what you could not check.
```

This gives the AI the work goal before it searches. It can skip unrelated files while keeping the evidence needed for a correct change.

How an LLM handles input as tokens, and why information in a long input is not always used equally well, is explained in [How much context is used and how](../llm-mechanics/context-amount-and-use.md). Choose helper tools from the [method and helper tool map](tool-method-map.md). Try existing search and short instructions first, and adopt a tool only if the repeated effort remains. This approach is sometimes called "context engineering" or "context routing."

## Terms

- **Context**: the instructions, code, documents, search results, and check results given to an AI so it can answer.
- **Static analysis**: checking source code without running the program. It can help locate code and connections, but does not prove that the program works or builds correctly.
