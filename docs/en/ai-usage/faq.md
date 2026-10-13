# Frequently Asked Questions for Using AI

> Japanese Source of Truth: [AI利用でよくある質問](../../jp/AI利用/よくある質問.md)

Use this page when your question is closer to "how should I ask the AI to do this?" than to a method name. Each item gives a short answer and a reusable request first, then links to a longer guide when one already exists.

This page is not a reading list. Open only the question that matches the problem you have now.

## Later files in a multi-file code proposal become vague or compressed

### Short answer

List the target files first and require **the same output structure for every file**. If the response cannot fit in one message, tell the AI to stop at a file boundary and list the files that remain instead of compressing the later files.

### Example request

```text
The target files are:
- src/a.py
- src/b.py
- src/c.py
- tests/test_c.py

For every file, always use this order:
1. Why this file changes
2. Changes
3. Updated code
4. Checks

Do not omit sections for later files.
If one response cannot fit everything, do not compress the remaining files.
Stop at a file boundary, list the files not yet produced, and continue with the same format next time.
```

### Why it helps

The output contract stays visible even when the response is long. This does not increase the service's output limit; split long work across messages without changing the format.

### Learn more

See [Give the AI document headings and their order](../methods/write-from-document-outline.md).

## The AI keeps missing coding rules

### Short answer

Do not paste every rule into every request. Point to the rules that apply, ask the AI to read them **before editing**, then ask it to compare the final diff against those rules. Run existing automated checks for rules that machines can verify.

### Example request

```text
Before editing, read the work and coding rules that apply to these files.
Briefly list the rules that apply and the existing checks you will run.

After editing, compare the diff with those rules.
Separate items verified by automated checks from items verified by reading the code.
Do not report an unchecked rule as passed.
```

### Why it helps

The workflow ties the rule to the actual diff and check result rather than stopping at "I read the rules."

### Learn more

See [Have the AI read coding rules and check its changes](../methods/follow-coding-rules.md).

## Code comments follow neither project rules nor what readers need

### Short answer

Before asking for comments, identify the project's comment rules and **who will read the comment**. Ask for information that is not already obvious from the code: usage contracts for callers and non-obvious reasons, constraints, or invariants for maintainers.

### Example request

```text
Before changing comments, read the comment rules that apply to this file and nearby existing examples.

For public functions, prioritize the inputs, outputs, and failure conditions a caller must know.
For implementation comments, prioritize non-obvious reasons, constraints, and invariants.
Do not add comments that only restate the code unless project rules require them.

Afterward, compare each changed comment with the implementation and diff.
```

### Why it helps

The goal becomes useful information rather than a larger comment count.

### Learn more

See [Have the AI write code comments that help readers](../methods/write-useful-code-comments.md).

## I want the AI to choose among several options for the current project

### Short answer

Provide the candidates, goal, and mandatory conditions. Compare every candidate against **the same criteria** and require project evidence from specifications, code, configuration, and tests.

### Example request

```text
Recommend the option that best fits this project from A, B, and C.
The goal is ... and the mandatory conditions are ....
Do not add new candidates.

First derive criteria from the goal and mandatory conditions.
Inspect the project specifications, code, configuration, and tests needed for those criteria.
Compare all candidates using the same criteria.
Separate verified facts, inferences, and unknowns.
Do not invent scores.
I will make the final decision.
```

### Why it helps

The result is about this project rather than a generic list of pros and cons.

### Learn more

See [Compare proposed design options with project evidence](../methods/compare-design-options-with-project-evidence.md).

## How do I tell the AI who a document is for?

### Short answer

Do not stop at "for beginners." Specify **what the reader already knows** and **what the reader should be able to do after reading**. Ask the AI to check first-use terminology, subjects, actions, and results.

### Example request

```text
The reader has used Python a little but does not know this project's structure or terminology.

After reading, the reader should be able to explain which file to change and which test to run.

Explain first-use technical terms by their role.
Do not rely on "this" or "that" when the subject is unclear.
After drafting, fix only sentences that are missing a subject, target, action, or result.
```

### Why it helps

The AI has a concrete knowledge boundary instead of guessing how much to explain.

### Learn more

See [Make explanations understandable to their readers](../methods/make-explanations-understandable.md).

## I have a large design change and want its impact split into work items

### Short answer

Do not start implementation immediately. Provide the goal, the design change, what must not change, and the completion criteria. Ask for evidence-backed impact analysis across specifications, implementation, configuration, callers, and tests, then derive work items from that evidence.

### Example request

```text
Before implementing this design change, investigate only the impact and work breakdown.
Do not edit files yet.

Goal: ...
Design change: ...
Conditions that must not change: ...
Completion criteria: ...

Inspect related specifications, implementation, configuration, callers, and tests.
For every candidate location, report the path, relevant symbol or section, and why it is affected.

Then split the work into independently verifiable items.
For each item, list change targets, constraints, checks, and dependencies on earlier work.
Leave unverified impact explicitly unverified.
```

### Why it helps

You establish evidence and work boundaries before a large edit, and expand the scope only when the evidence reveals another dependency.

### Learn more

Use [Set design and completion criteria first](../design-and-completion-criteria.md), [Context Priority](../context-priority.md), and [Choose validation scope from the change's impact](../change-impact-routing.md).

## The AI keeps adding classes, variables, functions, or logic with overlapping responsibilities

### Short answer

Before creating anything, search for existing elements with the **same responsibility**, not only similar names. Inspect definitions, callers, tests, and nearby design explanations, then compare reuse, extension, and new creation.

### Example request

```text
Before implementing, search for existing classes, functions, or state that have the same responsibility as this feature.

Do not stop at name matches. Inspect definitions, callers, related tests, and nearby design documentation.
For each candidate, decide with evidence whether to:
- reuse it as-is,
- extend it,
- or create a new element.

If a new element is needed, explain what the existing elements cannot satisfy and define the new responsibility before coding.
Do not merge different responsibilities merely because their names are similar.
```

### Why it helps

The AI checks whether project structure can be reused before adding another parallel implementation, while still avoiding false merges based only on naming.

### Learn more

Use [Source Structure Index](../source-structure-index.md) for definitions and callers, and [Have the AI read coding rules and check its changes](../methods/follow-coding-rules.md) for project reuse rules.

## I pointed out one problem and want the AI to find the same kind elsewhere

### Short answer

Do not ask it to "fix everything similar" from one example. Give the example, why it is wrong, the search scope, and exclusions. Have the AI restate a reusable check first, then return candidates without editing.

### Example request

```text
Find other occurrences of the same problem as this example.

Example: ...
Why it is a problem: ...
Search scope: ...
Exclusions: ...

First restate the example as a short check criterion.
If the criterion is ambiguous, ask before searching.

Then list candidates with file, line or section, and reason,
separating "clear match," "needs review," and "out of scope."
Do not edit until the candidates are reviewed.
Report what scope was searched and what remains unchecked.
```

### Why it helps

It reduces over-generalization from one example and separates mechanical candidate search from the judgment that two cases are actually the same problem.

### Learn more

For code, [Source Structure Index](../source-structure-index.md) can help find candidates. For documents and configuration, inspect each candidate in its original context instead of deciding from a text match alone.

## Which model or editing mode should I use for a task?

### Short answer

Choose **model capability, latency, and cost** separately from **what the AI tool can read, edit, and execute**. A strong model inside a targeted editor action and the same model inside a workspace agent have different work surfaces.

### Keep two axes separate

| Axis | Check |
| --- | --- |
| Model | required reasoning/code ability, latency, usage cost, local hardware requirements, and whether data leaves the device |
| Work surface | selection-only versus workspace search, multi-file editing, terminal/test execution, and change isolation/review |

Do not assume "local model = cheap" or "cloud model = powerful." Local use has hardware, electricity, setup, and maintenance costs, while cloud providers offer different capability and price tiers. Check current provider information at the time you choose.

### Practical task boundaries

- **Short question or one visible edit:** a selection- or active-editor-centered tool is convenient.
- **A change whose callers or tests must be found:** use a surface that can search the workspace.
- **Multi-file editing plus commands and tests:** use an agent that can read/write the project and run tools.
- **Code that must not leave the device:** consider a model that actually runs locally; confirm execution location rather than inferring it from a product name.

### Current examples checked on October 13, 2026

- [Ollama](https://ollama.com/) can run local models, but it also offers [cloud models](https://ollama.com/blog/cloud-models). Do not equate the product name itself with local inference; check whether the selected model runs on the machine or in the cloud.
- [VS Code Inline Chat](https://code.visualstudio.com/docs/chat/inline-chat) is designed for quick, targeted edits around the active editor or selection. Its official documentation also notes that other workspace files may be used as context, so "it can only read the open file" is not a safe assumption.
- [VS Code Agent](https://code.visualstudio.com/docs/agents/overview) can handle multi-file work, find relevant code, edit files, and run commands or tests. A user still needs to review the diff and verification results.

### Example request

```text
Help me choose an AI setup for this task.

Task: ...
Code scope: ...
Workspace search required: yes / no
File editing required: yes / no
Commands or tests required: yes / no
Restrictions on external data transfer: ...
Priority for latency and cost: ...

Compare "model capability, latency, and cost" separately from
"what the tool can read, edit, and execute."
If you name currently available models or prices, verify them against current provider information.
```

### Why it helps

It avoids treating model intelligence and tool permissions as the same capability, and makes it easier to give the AI only the scope the task needs.

### Learn more

See [Why can LLMs write code?](../llm-mechanics/why-llms-can-write-code.md).

## I want fewer image-generation retries

### Short answer

Before generation, organize only the **conditions that must be preserved**: purpose, subject and action, composition, background, medium/style, light and color, aspect ratio, required text, and elements that must stay. More adjectives are not automatically better; prioritize details that change the result.

With a reference image, separate what should remain from what should change. If a result is close, use an editing feature that can target the changed region or attribute. If the main subject or composition is far off, revise the core conditions and regenerate.

### Example request

```text
Purpose: store image for a mobile game
Subject: one small red robot running to the right
Composition: robot slightly left of center, with space in the direction of motion
Background: futuristic city at night
Medium/style: 2D animation
Color/light: blue city light while keeping the red robot easy to see
Aspect ratio: 16:9
Text in image: none

Must preserve:
- exactly one robot
- full body inside the frame
- facing and moving right

If I provide a reference:
- preserve: robot shape and color palette
- change: background and running pose
```

For a close result, a targeted edit can be:

```text
Keep the robot shape, colors, and composition.
Change only the background to a rainy city at night.
Do not add people or another robot.
```

### Why it helps

Providing the central conditions up front can reduce retries caused by missing requirements, but it does not guarantee a one-shot result. Models, resolutions, reference-image behavior, editing features, credits, and pricing vary by service, so this guide does not claim a fixed cost reduction.

### Current official references checked on October 13, 2026

- The [Gemini API image generation guide](https://ai.google.dev/gemini-api/docs/image-generation) documents text-to-image generation and text-plus-image editing that can add, remove, or modify elements and alter style or color grading. It also includes an example that turns a rough sketch into a finished image.
- [Midjourney Prompt Basics](https://docs.midjourney.com/hc/en-us/articles/32023408776205-Prompt-Basics) describes useful dimensions such as subject, medium, environment, lighting, color, mood, and composition. It also notes that short, clear prompts can work better than long instruction lists.
- [Midjourney Image Prompts](https://docs.midjourney.com/hc/en-us/articles/32040250122381-Image-Prompts) describes reference images influencing content, composition, and color. An Image Prompt is not itself an instruction to edit an existing image, so use the service's editing tools when direct modification is the goal.

## How this FAQ relates to context reduction

The FAQ is an entry point so you do not have to read every method guide for every problem. Reuse the short request that matches the current issue, then open a longer guide only when you need its details.

Reusable requests can reduce repeated clarification when requirements are often omitted, but do not remove the specifications, source code, tests, or image constraints actually needed for the task.
