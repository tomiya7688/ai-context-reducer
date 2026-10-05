# Create Repeated Text and Files from a Template

> Japanese source of truth: [定型文と定型ファイルを生成する](../jp/定型文と定型ファイルを生成する.md)

For text or configuration files with a mostly repeated structure, keep the shared parts in a template and fill in only the values that change for each task. This avoids having an AI recreate the whole text every time and reduces missing fields or unintended edits.

## Example: Create a release notice

Suppose every release notice includes a product name, version, date, and list of changes. If the headings and order stay the same, keep that structure in a template:

```markdown
# {{product}} {{version}}

Released: {{date}}

## Changes
{{changes}}
```

For a new notice, provide the product name, version, date, and changes for that release. There is no need to compare every old notice or recreate the same headings. A person still checks that the change list and release date are correct.

## Separate the template from its inputs

Put wording, headings, and settings that stay the same in the template. Keep task-specific values—such as a name, version, date, or target—in the inputs. Duplicating the shared part into separate files makes it easy for fixes to get out of sync, so maintain one source for the repeated content.

```text
template + current input values -> generated text or file
```

The generated text or file is the deliverable. If the shared wording needs to change, edit the template and regenerate the outputs that need updating instead of editing a generated copy. This keeps the next result in the same format.

## Create and check the result

1. Confirm that the same format is used repeatedly.
2. Separate the parts that stay the same from the values that change each time.
3. Create the text or file from the template and current inputs.
4. Check that required values are present and no replacement marker remains.
5. Have a person review the result when its correctness or approval matters.

A successful generation does not prove that the content is correct. Check that required fields are filled, the values are right, and expected sections are present. For license or contract text, a generator only reuses approved wording; it does not determine legal validity or suitability for an individual case.

For public or policy text where meaning matters, keep enough information to identify the template version and inputs used. A simple internal note may not need version tracking.

## When it helps

This works well for notices, release information, shared headers, and configuration files that reuse the same content. After checking the template once, a person can focus on the changing values and generated diff instead of writing and comparing the entire text every time.

It is not a good fit for one-off free-form writing or content whose structure changes for every task. If creating and maintaining a template takes more work than repeating the content, write it normally.

## Use a generator when needed

A small script may be enough to replace input values. If the project already uses a template manager and needs to update previously created projects when a template changes, reuse that existing system. This method does not require a particular tool.

Commands, replacement rules, and checks for this repository's simple generator are in the [template README](../../tools/common/medium/template/README.md).
