# Give the AI document headings and their order

> Japanese source: [AIに文章の見出しと順番を渡して書かせる](../../jp/手法/AIに文章の見出しと順番を渡して書かせる.md)

When you ask an AI to write several operation guides, one may omit preparation and another may omit how to check success. Providing the order “purpose, preparation, actions, check the result,” together with what belongs under each heading, makes it easier to draft each guide consistently.

## When to use it and how to decide

- Use it for repeated documents of the same kind, such as feature operation guides or change proposals that need the same information every time.
- If headings alone do not prevent omissions, specify what satisfies each section. For an operation guide, this includes the actor, screen, button names, and state after the action.
- For a short, one-off answer, listing the required items in the request is simpler. If documents need substantially different structures, decide a suitable outline for each purpose rather than packing everything into one template.

For inserting names or dates into fixed wording, you can use [generation from a fixed template](https://github.com/tomiya7688/ai-context-reducer/blob/main/docs/en/boilerplate-generation.md). Choose according to the following distinction.

| Desired output | What to provide | How the body is produced |
| --- | --- | --- |
| Change dates or product names in a fixed announcement | Fixed text and replacement values | A dedicated program inserts values |
| Write operation guides for different features with the same structure | Headings, section requirements, and factual sources | The AI reads the sources and writes the body |

## Steps to use it

### 1. Save a short outline in a file

Copy [DOCUMENT_OUTLINE.en.md](../../../templates/DOCUMENT_OUTLINE.en.md) into your project, for example as `templates/operation-guide-outline.md`. A [Japanese version](../../../templates/DOCUMENT_OUTLINE.md) is also available.

For an operation guide, start with this outline. Bracketed text instructs the AI what to write; it is replaced by actual content in the finished body.

```markdown
# [Operation name]

## Purpose
[State who this guide is for and what they will be able to do.]

## Preparation
[Name the required screens, files, and settings. If no preparation is needed and this is confirmed, state that explicitly.]

## Actions
[Describe the actor, screen, buttons, or input values in order.]

## Check the result
[State which screen or value shows that the operation succeeded.]
```

All four section headings are required in this example. “No preparation needed” differs from “we do not know whether preparation is needed.” Tell the AI not to leave an unknown section blank or remove its heading.

### 2. Specify the outline, sources, and output destination

Include the current reader, feature, and sources that establish the facts. Replace these example paths with real files.

```text
Write a guide for saving settings.
The reader is using this app for the first time.
Outline: templates/operation-guide-outline.md
Factual source: the “Save and load” section of docs/specs/settings.md
Output: docs/users/save-settings.md

First read the outline and the specified source.
Keep the heading names and order. Replace bracketed instructions with content supported by the source.
For actions, state who uses which screen and presses what.
For checking the result, state what demonstrates success.
If facts are missing and you cannot finish, ask about the missing items first.
When I request only a draft, mark each unresolved item as “Needs confirmation: the fact to check.”
Do not invent operations or values.
If you think headings need to be added or removed, explain why before changing the body.
Before saving, check required headings and their order, section content, and additions outside the outline.
After checking, save the complete body to the specified destination.
Report a draft with unresolved items as unfinished.
```

In a chat that cannot read files, attach or paste the outline and necessary sources. Replace “save to the destination” with “output the complete body.” Giving a path alone does not pass the file contents to such a chat.

For repeated use in the same project, put a short instruction in, for example, `AGENTS.md`. If your environment does not read it automatically, explicitly ask the AI to read that file too.

```text
When creating or updating operation guides, read templates/operation-guide-outline.md
and follow its headings and section requirements. The current request specifies the reader and factual sources.
```

### 3. Have the AI check whether the requirements are met

Ask the AI to check these four points. Also check yourself that the operations and results agree with the sources.

| Check | Passing example | Example needing correction |
| --- | --- | --- |
| Required headings and order | Purpose → Preparation → Actions → Check the result are present | “Check the result” is missing |
| Section content | Actions name the screen and button; the result names a value to check | “Operate appropriately” without steps |
| Unknown facts | The source was checked or a question resolved the gap | A possibly nonexistent button was invented |
| Additions outside the outline | Only agreed sections are present | An unrequested long overview or appendix was added |

A document with “Needs confirmation” items is a draft. Do not treat it as finished until you provide missing facts or identify a source to resolve them. A complete structure does not guarantee factual accuracy or readability. You can also check explanation gaps using [Make explanations understandable](make-explanations-understandable.md).

### 4. Keep the outline small

Limit headings to what readers need to understand the purpose, perform the operation, and judge the result. An announcement that only changes a date does not need “Actions” and “Check the result” sections.

Decide before drafting to remove headings that serve no purpose for this use. Keep required sections whose sources are missing. If a heading is consistently unused, consider revising the template or separating it by purpose. Put feature names, readers, and source locations in the current request. Refer to separate instructions for detailed shared rules to keep the outline and `AGENTS.md` from growing.

## Why this can reduce context use, and its limits

Reusing a short outline can reduce conversations repeatedly explaining missing headings or changed order. Providing the current structure and necessary facts can also reduce the need to give the AI many past documents from which to infer the structure.

The outline itself consumes input. A long template or many examples may increase usage. Keep the sources needed to check facts, and judge the effect by the reduction in structure instructions and correction exchanges. This repository has not measured the savings.

## Supporting tools

- **An editor’s heading outline:** Displays headings in document order. You can use it to check missing required headings and unexpected additions.
- **Git diff:** Displays changes between versions. You can use it to find removed template headings or unrequested added explanations.

## About this method

Providing an output structure and places to fill, then asking the AI to generate content in that shape, is called the **Template Pattern**, described in [White et al.’s paper](https://arxiv.org/abs/2302.11382). The paper notes that extra text may still appear before or after the specified structure, and that restricting structure may exclude useful explanations.

The storage locations, handling of missing facts, and completion checks here are practical project examples. They do not mean the paper demonstrated reduced context use.

## References

- Jules White et al. (2023). [A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT](https://arxiv.org/abs/2302.11382). arXiv:2302.11382. DOI: 10.48550/arXiv.2302.11382. Section III-J, “The Template Pattern”.
