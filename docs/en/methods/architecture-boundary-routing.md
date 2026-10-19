# Use feature areas to choose what code to read

> Japanese version: [機能ごとのコードの分け方から読む場所を決める](../../jp/手法/機能ごとのコードの分け方から読む場所を決める.md)

If the project already keeps code for different features, such as screens and data storage, in separate places, use that layout to tell the AI where to start reading. Do not invent a new design or guess which code belongs to each feature.

## Example

If you change only the text on a settings screen, start with the screen code and its tests. If screen code and storage are separate areas, include storage only when the change also affects how settings are saved.

If you change the data passed from the screen to storage, check both sides and the rules for that data. A change at the boundary can affect both the sender and receiver.

## Tell the AI what to do

```text
Use existing design notes or folder guides to identify which feature contains the code I changed.
Start with that feature's code and related tests.
If you change how one feature passes data to another, check the sender, receiver, and the rules for that data.
If the feature layout is undocumented, unclear, or out of date, do not guess. Search normally for related code.
```

## When to use it and when to broaden the search

This approach helps when:

- The project has several areas and it is hard to know where to start.
- Documents already show which code belongs to each feature and how data moves between them.
- That information can exclude unrelated areas from the initial search.

Search more broadly when the feature layout is unclear, the guide may be stale, or the change crosses several features. Small projects with obvious code locations do not need a special feature map.

## Where to save the map and how to point the AI to it

For a feature map used repeatedly, save it as `docs/feature-ownership.md`, for example, and link to it from the root `AGENTS.md`. In the task request, tell the AI to start with the row for the changed feature and check both sides only when the change crosses a boundary. Reuse an existing map instead of creating a duplicate.

## Why this reduces context

Tell the AI to start from the existing feature layout instead of reading the whole project to infer what each part does. Ask it to broaden the search when the change affects several features or the guide cannot answer the question, so important connections are not skipped.

## Optional helper tools

- If useful, the [Function and file relationship tool](../../../tools/common/large/source-structure-index/README.md) lists relationships between functions and files. Use the list as a starting point and have the AI check the code and tests too.
- If useful, [`architecture-boundary-router`](../../../tools/common/medium/architecture-boundary-router/README.md) uses existing feature areas and data flows to list boundaries and starting files related to a change. Use it when you are unsure where to start investigating. Have the AI check its suggestions against the design notes, code, and tests.

A document or ordinary search can serve the same purpose, so these tools are optional.
