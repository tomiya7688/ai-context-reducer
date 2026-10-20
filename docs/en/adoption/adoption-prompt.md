# Ask AI to improve the project guide
> Japanese version: [AIに作業ルールを整えてもらう](../../jp/導入/AIに作業ルールを整えてもらう.md)


Send the text below to an AI to improve only the guidance your project needs. Start from a problem that keeps happening; do not ask the AI to read every document first.

## Text to send to the AI

```text
Improve the project guidance so an AI can find the information it needs.

Put project-wide instructions in `AGENTS.md` at the repository root. Put project features and limits in a root `PROJECT_CONTEXT.md`, and link to it from `AGENTS.md` with a note about which tasks need it. If a recurring guide or map belongs under `docs/`, link to it from `AGENTS.md` too. Keep conditions for a single task in that task request instead of making them permanent rules.

Start with the README, existing AI instructions, document headings, and how tests are run. Do not read every file or the full project history at the start.

Check which instruction file name your AI reads and whether it supports Skills, which register recurring procedures separately. If a recognized `AGENTS.md`, `CLAUDE.md`, README, or `docs/` page already exists, fix and reuse it instead of creating a new one. If Skills are not available, write a short guide document and give its path in the request. Do not add every method just because it is a standard.

Briefly find:
- Files or explanations that people repeatedly search for
- Situations where the AI repeatedly reads unrelated files or long logs
- Whether different changes need different checks
- Whether existing guidance or tools already solve the problem

Choose one problem that actually keeps happening. Make the smallest useful change. Before creating a document, check whether a short addition to an existing guide is enough.

Be concrete: say which documents the AI should read and when, when it should broaden its search, and what counts as done. Use real file and test names, or clearly label an example as fictional.

After the change, check that the new guidance leads to the required documents and checks. Run relevant documentation checks or tests. Mark anything you could not check as unverified.

Briefly report what changed, which repeated problem you chose, why this change helps, and what you checked. Do not add a system that has no clear benefit; explain why you skipped it.
```

## What the AI should look for

For a small project, the README, existing guidance, test instructions, and current problem may be enough. Add a large list or a dedicated automated process only when the same search or check is repeated often.

Examples:

- If people repeatedly find the same code and tests, add a short guide for each kind of work.
- If long logs are passed to the AI each time, ask it to report only relevant lines.
- If all tests finish quickly and the right tests are obvious, run the existing tests without creating a map.

## Example: a small repository and several apps

If the project has few files and the settings code and its test are easy to find, a short note on which file to read first and which test to run is enough. Adding an index or a dedicated tool can cost more to set up and update than it saves in investigation time.

In a larger project with desktop and web apps, you may be looking up the screen, storage code, and tests again for every settings change. A table that picks where to look from the kind of change, or per-app work rules, may help. Have the AI first find what is repeatedly searched again, and choose only the mechanism that reduces that repetition.

## Why set a scope first

Giving the AI a starting point and a way to check the change avoids sending search results and explanations for unrelated parts of the project. Tell the AI to search further if needed, so starting small does not mean skipping necessary checks.

## What to check after adoption

Check not whether the AI read many documents, but whether the guide takes it to the code and tests relevant to this task. A small project may need only a short top-level entry. In a larger project, a table or index you add goes stale when code or responsibilities change, so keep it in a form you can update. Remove instructions from the text you send if they do not fit the project's size or problems.

## Related pages

- Choose which methods are useful: [Choose only the methods you need](adoption-priority.md)
- Follow the basic approach: [Basic steps for asking AI to work on a project](../methods/guide.md)
- Project rules for the AI: [AGENTS.md template](../../../templates/AGENTS.md)
- Project features and limits: [project context template](../../../templates/PROJECT_CONTEXT.md)

## Terms

Setting up an existing guide as the AI's entry point is sometimes called **Context Engineering / context setup**. When you need a helper tool, choose one from the [method and helper tool map](../methods/tool-method-map.md).

“Context” means the instructions, code, documents, and check results given to an AI for one task. Context reduction keeps the information needed for the task and leaves out unrelated material.
