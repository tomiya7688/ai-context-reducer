# Ask AI to improve the project guide
> Japanese version: [AIに作業ルールを整えてもらう](../../jp/導入/AIに作業ルールを整えてもらう.md)


Send the text below to an AI to improve only the guidance your project needs. Start from a problem that keeps happening; do not ask the AI to read every document first.

## Text to send to the AI

```text
Improve the project guidance so an AI can find the information it needs.

Put project-wide instructions in `AGENTS.md` at the repository root. Put project features and limits in a root `PROJECT_CONTEXT.md`, and link to it from `AGENTS.md` with a note about which tasks need it. If a recurring guide or map belongs under `docs/`, link to it from `AGENTS.md` too. Keep conditions for a single task in that task request instead of making them permanent rules.

Start with the README, existing AI instructions, document headings, and how tests are run. Do not read every file or the full project history at the start.

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

## Why set a scope first

Giving the AI a starting point and a way to check the change avoids sending search results and explanations for unrelated parts of the project. Tell the AI to search further if needed, so starting small does not mean skipping necessary checks.

## Related pages

- Choose which methods are useful: [Choose only the methods you need](adoption-priority.md)
- Follow the basic approach: [Basic steps for asking AI to work on a project](../methods/guide.md)
- Project rules for the AI: [AGENTS.md template](../../../templates/AGENTS.md)
- Project features and limits: [project context template](../../../templates/PROJECT_CONTEXT.md)

## Terms

“Context” means the instructions, code, documents, and check results given to an AI for one task. Context reduction keeps the information needed for the task and leaves out unrelated material.
