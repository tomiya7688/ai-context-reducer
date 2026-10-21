# Give the AI instructions for the files it will change
> Japanese version: [AIに作業場所に合った指示書を読ませる](../../jp/手法/AIに作業場所に合った指示書を読ませる.md)


To give the AI project rules, use instruction files. First identify the file to change, then walk down the folders leading to it. Have the AI read any instruction files along that path, starting with the project-wide instructions. Do not have it read files in a different app's folder. This gives the AI the rules for the task without making it read unrelated procedures.

You can use one instruction file for the whole project, or separate files for folders that need their own rules. Filenames differ between AI products; this example uses `AGENTS.md`.

Imagine an app with desktop and web versions that have different settings screens and different ways to check them.

## Example: asking the AI to fix desktop settings

A user asks the AI, "Fix the desktop settings screen." The target file is `apps/desktop/src/settings/config.py`. The project has placed its instructions like this:

```text
repo/
  AGENTS.md
  apps/
    desktop/
      AGENTS.md
      src/settings/
        AGENTS.md
        config.py
    web/
      AGENTS.md
```

Starting at the project folder and following the path to `config.py`, we find these three instruction files. Have the AI read them in this order:

- `repo/AGENTS.md`: the settings-file format shared by the whole project
- `apps/desktop/AGENTS.md`: how to check the desktop version
- `apps/desktop/src/settings/AGENTS.md`: rules for settings code

`apps/web/AGENTS.md` is outside the path to the file being changed, so do not read it. It covers the web version and does not apply to this desktop change.

## What to put in each guide

- Top-level guide: rules shared by all apps
- App guide: how to build or check that app
- Feature guide: rules for that feature
- Task request: the goal and how to tell when the work is done

Do not copy shared rules into every guide. Write only information that applies to that app or feature. Then a shared rule needs to be updated in only one place.

## Start with a short instruction file

For a small project, one root `AGENTS.md` or equivalent AI instruction file is enough. Keep only shared rules and links to details there. `AGENTS.md` is one common filename for project instructions; different AI products may or may not load it automatically. If yours does not, tell the AI where to find it in the task request.

Start with the [AGENTS.md template](../../../templates/AGENTS.md) and remove examples that do not fit your project. Stable facts such as project features and limits can go in the [project context template](../../../templates/PROJECT_CONTEXT.md). Keeping rules separate from facts lets you give the AI only the information needed for a task.

In the root `AGENTS.md`, link to each detailed guide and say which work needs it. For example:

```markdown
- Read `PROJECT_CONTEXT.md` when checking project features or limits.
- Read `docs/data-format.md` when changing saved-data behavior.
```

If the AI product does not load `AGENTS.md` automatically, include its path and the relevant linked guide in the task request.

Some AI products also support reusable instructions called **skills**. Use one for a repeated procedure, such as the same release checks. The product defines where to put it and how to call it; follow those instructions, then tell the AI to use that skill for the relevant task.

```text
Shared project rules: AGENTS.md
Desktop-specific rules: apps/desktop/AGENTS.md
Reusable release procedure: registered release skill
```

## Keep instructions small

- Put only rules for most tasks and links to details in the root file.
- Put rules for one folder in that folder's guide.
- Make a skill only for a repeated procedure; put one-off work in the task request.
- Do not copy the same rule into several guides or skills.
- Remove or update instructions and examples that are no longer used.

After you add a new instruction, ask the AI to do a simple task and check that it actually reads or invokes the instruction. If your tool can show which files it loaded, check that record. If it cannot, compare the reported paths, the diff, and the check results with what the guide says. Do not treat the AI's own statement as proof that a file was loaded automatically. Update the links and commands in your guides whenever files move or tests change.

## When instructions conflict

The top-level guide states conditions for the whole project; a guide in a lower folder adds conditions for that location. For example, if the top-level guide says "do not change the stored format," a desktop-only guide must not quietly cancel that condition. The task request states the goal and completion conditions for this task, but it does not silently disable a long-lived rule.

Which instruction takes priority depends on the AI and the project's rules. If you find a conflict, do not pick one by a private rule: check the relevant specification or original document. If you still cannot decide, have the AI report the conflict before it changes anything.

## When separate guides help

- The project has multiple apps, such as desktop and web versions.
- Different apps or features have different ways to build or check them.
- The top-level guide makes the AI read many steps unrelated to its task.

## When they are unnecessary

For a small project, if you can point the AI to the needed files and checks with one short guide, separate folder guides are unnecessary. Do not create a guide in every folder.

## AI product differences

AI products differ in whether they load folder-specific guides automatically and which filenames they recognize. Check the documentation for the product you use. If it does not load guides automatically, tell the AI in the top-level guide to check the guides along the path to the target file, or point it to the needed guides when assigning the task.

## Tell the AI what to do

```text
First identify the file to change. Starting at the project folder, follow the folders leading to that file and read each `AGENTS.md` in order. Do not read instruction files under a different app. Report which files you read, including any loaded automatically.
If this AI product does not load them automatically, open the listed files yourself.
```

## Why this reduces context

For a desktop change, give the AI shared rules and desktop instructions, but leave web-only guidance out. It can start without reading every product's procedures, and shared rules only need to be updated in one place.

## Optional helper tool

- [scoped-guides](../../../tools/common/small/scoped-guides/README.md) finds the guides that may apply from a target file's parent folders and lists only their paths and reasons. Use it instead of walking up the folders by hand.

## Terms

- **Hierarchical Context / scoped instructions**: Splitting instructions so the AI reads the ones that match the location of the work.
