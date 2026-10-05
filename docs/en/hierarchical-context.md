# Put Instructions Near the Work They Govern

> Japanese source of truth: [場所ごとの指示](../jp/場所ごとに作業ルールを分ける.md)

In a large repository, keep rules shared by the whole project separate from procedures needed by one application. Once you know which file you will change, read the repository-wide guide and the guides that apply to the folder containing that file.

## Example: Changing a Desktop app setting

Suppose you are changing the settings screen in a project that contains both a Desktop app and a Web app. They have different build and test procedures.

```text
repo/
  AGENTS.md                     # shared rules and pointers
  apps/
    desktop/
      AGENTS.md                 # Desktop-specific build and test steps
      src/settings/              # file being changed
    web/
      AGENTS.md                 # Web-specific build and test steps
      src/
```

When changing a file under `apps/desktop/src/settings/`, read the repository-wide `AGENTS.md` and the Desktop guide at `apps/desktop/AGENTS.md`. The Web guide does not apply to this file, so there is no need to read its procedures.

For example, the repository-wide guide might say to preserve the saved data format. The Desktop guide might name the command for launching the app and the location of settings-screen tests. Keeping a Web-only build command out of the shared guide means Desktop contributors do not load a procedure unrelated to their task.

## Where instructions belong

Put conditions that apply to every part of the repository, along with guidance on finding local instructions, in the root guide. Put an app's build steps or local design constraints in that app's folder. You do not need a guide in every folder; add one only where a distinct rule is repeatedly needed.

In the example, the Desktop guide adds only Desktop-specific conditions instead of copying the full repository guide. When shared guidance changes, this avoids having to update the same text in several places.

## Start with a short AGENTS.md

If your AI tool reads `AGENTS.md`, begin with one at the repository root. Keep only rules that apply to every task and pointers to the next guide. `AGENTS.md` is not a universal file that every AI tool loads automatically. Check which file names the active tool recognizes and whether it reads files in nested folders. If the project already has a recognized guide such as `CLAUDE.md`, update it instead of adding a duplicate.

A small root file might contain:

```markdown
# AGENTS.md
- Before editing, identify the behavior, specification, and matching tests.
- For changes under `apps/desktop/`, also read that folder's AGENTS.md.
- Follow links to the original specification and command details when relevant.
```

Keep command catalogs, design explanations, and notes for every feature out of the root guide. Link to them under a clear condition, so the next file to open is still obvious.

## Use Skills for repeated task workflows

If the AI tool supports Skills, use one for a repeated workflow such as changing an API or preparing a release. Keep rules needed for every task in the root `AGENTS.md`; put in each Skill when to use it, the inspection order, checks to run, and what to report at completion. Skill formats, locations, and invocation differ by tool, so follow the active tool's conventions.

A Skill should state when to use it and what steps to follow. Use the format required by the AI tool.

```markdown
# api-change-review
Use when: changing API inputs, outputs, or compatibility
1. Find the endpoint and its consumers.
2. Check contract tests and run tests for the change.
3. Report inspected paths, results, and consumers not verified.
```

If the Skill is not selected automatically, say “Use the api-change-review Skill” in the request. If the AI tool has no Skills feature, put the same steps in a short Markdown guide and give the AI its path.

## Keep guidance small and make sure it works

- Start with one recurring task. Do not add a guide just because the format exists.
- Write each rule as **when to use it → what to open or do → how to check the result**. Replace vague rules such as “be careful” with a concrete action, or remove them.
- Put shared rules at the root, folder-specific steps in a nested guide, and task workflows in Skills. Link to detailed sources instead of copying the same explanation.
- Try one real task. Check that the AI selects the expected guide or Skill and reaches the needed code and tests. If the tool shows loaded files, inspect that record; otherwise compare the reported paths, actual diff, and check results with the instructions. A claim that a file loaded is not proof by itself.
- Update paths and commands when the code or tests move. Remove rules that are unused, duplicated, or no longer true.

## Find the guides that apply to a file

For a task, follow the folder path to the target file and check the guides along the way.

```text
repo/AGENTS.md
  └─ apps/desktop/AGENTS.md
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

You can also follow the folder path and check applicable guides manually.

## Example request to the AI

> Check the instructions in parent folders up to the target file, and list the paths that apply. Do not mix in a sibling app's instructions. Explain which rules are project-wide and which procedures apply only to this app.

## Optional tools and terminology

If useful, [scoped-guides](../../tools/common/small/scoped-guides/README.md) finds candidate guides in the target file's parent folders and lists only their paths and reasons. Layering guidance by folder is called **Hierarchical Context** or scoped instructions.
