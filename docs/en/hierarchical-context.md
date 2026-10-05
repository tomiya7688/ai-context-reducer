# Put Instructions Near the Work They Govern

> Japanese source of truth: [場所ごとの指示](../jp/場所ごとの指示.md)

In a large repository, keep rules shared by the whole project separate from procedures needed by one application. Once you know which file you will change, read the repository-wide guide and the guides that apply to the folder containing that file.

## Example: Changing a Desktop app setting

Suppose you are changing the settings screen in a project that contains both a Desktop app and a Web app. They have different build and test procedures.

```text
repo/
  AI_CONTEXT.md                 # rules shared by the repository
  apps/
    desktop/
      AI_CONTEXT.local.md       # build and test steps for Desktop
      src/settings/              # file being changed
    web/
      AI_CONTEXT.local.md       # build and test steps for Web
      src/
```

When changing a file under `apps/desktop/src/settings/`, read the repository-wide `AI_CONTEXT.md` and the Desktop guide at `apps/desktop/AI_CONTEXT.local.md`. The Web guide does not apply to this file, so there is no need to read its procedures.

For example, the repository-wide guide might say to preserve the saved data format. The Desktop guide might name the command for launching the app and the location of settings-screen tests. Keeping a Web-only build command out of the shared guide means Desktop contributors do not load a procedure unrelated to their task.

## Where instructions belong

Put conditions that apply to every part of the repository, along with guidance on finding local instructions, in the root guide. Put an app's build steps or local design constraints in that app's folder. You do not need a guide in every folder; add one only where a distinct rule is repeatedly needed.

In the example, the Desktop guide adds only Desktop-specific conditions instead of copying the full repository guide. When shared guidance changes, this avoids having to update the same text in several places.

## Find the guides that apply to a file

For a task, follow the folder path to the target file and check the guides along the way.

```text
repo/AI_CONTEXT.md
  └─ apps/desktop/AI_CONTEXT.local.md
       └─ apps/desktop/src/settings/config.py
```

For `apps/desktop/src/settings/config.py`, the root guide and the guide in `apps/desktop/` apply. The guide in the neighboring `apps/web/` folder does not. If `apps/desktop/src/settings/` has its own guide, check it for additional rules that apply only to that folder.

If an agent cannot load folder-specific guides automatically, the root guide can tell the reader to check guides along the path to the target file. File names and automatic discovery rules vary by tool; check the project's setup instead of assuming defaults.

## When instructions conflict

The root guide describes repository-wide conditions; a guide in a lower folder adds conditions for that part of the project. For example, if the root guide says to preserve the saved data format, the Desktop guide must not silently cancel that rule. A task request states the current goal and completion criteria, but it does not silently remove long-lived rules.

Instruction precedence can vary between agents and repository policies. If two instructions conflict, do not invent an order and choose one. Check the relevant specification or authoritative source. If the conflict still cannot be resolved, make it explicit before implementation.

## When this helps

This approach helps when apps have different build or test steps, the same rules are reread for each task, or the root guide is growing too long. A contributor can read the instructions for the target folder without loading procedures for unrelated apps.

For a small repository where one short root guide leads directly to the relevant code and tests, local guides are unnecessary. Do not create empty guides for every folder or copy the same rules into multiple guides. Start with the locations that repeatedly need distinct instructions.

## Introducing folder-specific instructions

1. Identify the rules shared by the repository and put them in the root guide.
2. Put app-specific procedures and conditions in that app's folder.
3. Make it clear which guides apply to a target file.
4. Try one real task and confirm that the applicable guides explain its constraints and checks.

Helper tools can determine which guides apply to a path. For installation and command details, see the [scoped-guides README](../../tools/common/small/scoped-guides/README.md). The method itself also works by following the guides manually.

## Example request to the AI

> Check the instructions in parent folders up to the target file, and list the paths that apply. Do not mix in a sibling app's instructions. Explain which rules are project-wide and which procedures apply only to this app.

## Optional tools and terminology

Use [scoped-guides](../../tools/common/small/scoped-guides/README.md) to find applicable instructions. Layering guidance by folder is called **Hierarchical Context** or scoped instructions.
