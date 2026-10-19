# Avoid repeating the same explanation

> Japanese version: [同じ説明を何度も書かない](../../jp/手法/同じ説明を何度も書かない.md)

When the same requirement is copied in full into several documents, the AI has more to read and the copies can disagree after an update. Keep the full explanation in one document. In other documents, keep a short description and a link.

## Choose the document that defines the rule

For example, if `docs/data-format.md` defines the saved-data format, the README or AI guide can say:

```text
When changing saved data, check the format and compatibility requirements.
Details: docs/data-format.md
```

The defining document is the place that formally explains the rule. If the same rule is copied elsewhere, one copy may be missed during an update.

## Point the AI to the original document

After choosing the defining document, link to it from other guides and AI instructions. For example, if `docs/data-format.md` defines the saved-data format, add a line to `AGENTS.md` telling the AI to read it when changing saved-data behavior. For a one-time task, include the original document's path directly in the request.

## Tell the AI what to do

```text
Check whether the same detailed explanation appears in several documents.
If so, choose one document for the full explanation. Keep a short description and a link in the others.
Keep short summaries, examples, and safety notes when readers need them at that point.
Do not delete text just because it looks similar. Check that the needed information remains easy to find.
```

## What to keep

- Keep a short orientation and a link to details in the README.
- Tell the AI when to read a document; do not paste its full contents into the AI guide.
- Choose one defining document for a detailed rule used in several places.
- Repeat a short warning or explanation when it helps readers understand a standalone document.
- Keep the necessary details in documents distributed for standalone use.

Do not put new requirements only in a summary or index. If it differs from the defining document, update the summary after checking the full explanation.

## Why this reduces context

Keep one detailed copy and give the AI links to it instead of repeating the same long explanation across documents. This also makes the source easier to update consistently. Short descriptions and links still lead to the information when it is needed.

## When to consolidate

Choose one defining document when several copies must be updated or have started to disagree. If the project is small and duplicate text has caused no problems, no special list or automated check is needed. Keep repeated short summaries when they help readers.

## Optional helper tool

- If useful, `doc-duplicate-hints` lists documents that may contain similar explanations. Use it to find possible duplication, then have the AI check each document's purpose and links before deciding what to keep or remove.
