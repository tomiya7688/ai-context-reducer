# Create repeated documents and settings from a template

> Japanese version: [繰り返し使う文書や設定をひな型から作る](../../jp/手法/繰り返し使う文書や設定をひな型から作る.md)

For files such as license notices, notifications, and settings that stay mostly the same, keep the shared text in one template. Fill in only the values that change, such as a name or date.

## Example

```text
Template:
  {{name}} may be used under {{terms}}.

Values for this file:
  name = Example
  terms = commercial use allowed
```

After generating the file, check that the values are correct, no empty placeholders remain, and required sections are present. The generated text alone cannot prove that legal terms or project requirements are correct; check the approved wording.

## Keep the template and the input values separate

Put text, headings, and settings that never change in the template. Put values that change with each task, such as a name, version, or date, in the input. If you copy the same content into several files, a fix to the shared part is easy to miss, so keep one source for it.

Treat the generated document or file as the product to use. When the template must change, fix the template and regenerate instead of editing the product by hand. For public documents or terms where the meaning matters, keep track of which template version and input values produced the result. A simple internal note may not need that tracking.

## Tell the AI what to do

```text
Find the existing template. Use its name and only the values that change for this file.
Do not rewrite the shared text. Check that the generated document has no empty placeholders.
Report the template used, the changed values, and the check result.
If the template itself appears to need a change, check its purpose and owner before editing the generated file directly.
```

## Why this reduces context

Give the AI the template and the values to change so it can review only the generated differences instead of rereading or rewriting the same long document. Keeping shared text in one place also reduces wording drift and missing sections.

## When to use a template

Use one when files of the same form are created repeatedly, rewriting the whole text causes mistakes, or several copies must stay consistent. For a one-time document, a template and generator may add unnecessary work.

## Where to keep a template and how to point the AI to it

Save a reusable template under `templates/` with a name that describes its purpose. When asking the AI to use it, give both the template path and the path where the completed document should be saved. If several people reuse the process, link to the template from `AGENTS.md` or a guide under `docs/`. Merely placing a template in the repository does not ensure the AI will use it.

## Terms

- **Template Generation / boilerplate generation**: Keeping the shared parts in a template and filling in only the values that change to create a document or file.

## Optional helper tool

- If useful, `acr-toolbox template` replaces values such as `{{name}}` in a template and creates a file. Use it to create repeated documents or settings. It can also preview the result and check for unfilled values.

Reuse another template tool if the project already has one.
