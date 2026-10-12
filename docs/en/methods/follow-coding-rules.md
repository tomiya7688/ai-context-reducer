# Have the AI read coding rules and check its changes

> Japanese source: [AIにコードの決まりを読ませ、変更後に確かめさせる](../../jp/手法/AIにコードの決まりを読ませ、変更後に確かめさせる.md)

Do you repeatedly correct function names added by an AI or point out that it recreated existing functionality? “Follow the existing style” may not tell it what to preserve or how to check compliance.

Keep the rules in one place, have the AI apply them to the current change, and check its diff against them afterward. Separate mechanically checkable names and formatting from decisions that require reading what the code does. This can reduce the need for you to point out every violation.

## When to use it and how to decide

- Use it when you repeatedly point out the same naming, reuse, or dependency rules. Start with one recurring rule.
- If short instructions and checks already work, add references and a check of the changes to your request. Do not copy the rules into another file.
- Put conditions for a single task in that request. Move them to shared instructions when they become lasting rules.
- Use existing automatic checks for name formats or whitespace. To judge what a function does or whether an existing component fits, have the AI inspect implementations and callers.

## Steps to use it

### 1. Find existing rules and checks

Before having the AI write new rules, ask it to inspect these locations.

| Location | What it establishes | What to check |
| --- | --- | --- |
| Project instructions and contributor guidance such as `CONTRIBUTING.md` | Conditions, scope, and procedures | Whether detailed rules live elsewhere |
| Formatting settings such as `.editorconfig` | Whitespace and line ending settings | Whether the editor or checker supports them |
| Check configurations and command lists | Automated rules and how to run them | Target files and enabled rules; a file alone does not ensure execution |
| Existing code and tests | Component usage and required behavior | Older code may violate current rules |

This repository explains finding rules in [Check rules related to the current change](../policy-routing.md) and using instructions by location in [Separate rules by location](../hierarchical-context.md).

### 2. Save concrete rules in one place

The following is a fictional JavaScript project, not this repository’s rules. Replace file paths and commands with ones that exist in your project.

Use the relevant section of an existing rule document. If there is none, you could save the following as `docs/development/coding-rules.md`.

```markdown
# Coding rules

Scope: handwritten code under src/settings/. Do not edit generated files.

- R1 Required: name functions like loadSettings, with a lowercase first word
  and capitalized subsequent words. Preserve externally defined names.
  Check the format with the existing naming check, and check the meaning against the diff.
- R2 Required: before adding JSON file reading, inspect readJson in src/io/readJson.js.
  Reuse it if its input, return value, and failure behavior fit; do not duplicate that processing.
  Otherwise report the mismatched conditions with evidence.
- R3 Required: do not add external dependency packages for this settings feature.
  If you think one is needed, report why and stop without adding it.
  Check diffs of dependency files and new imports.

Check commands: use format:check, lint, and test:settings defined in package.json.
Confirm that lint includes a naming check; otherwise inspect R1 name formats in the diff too.
```

Scope, requirements, exceptions, and verification steps are easier for both the AI and people to judge than “use clean names.” Labels such as R1 let reports refer to rules briefly.

Keep detailed rules in contributor guidance that people can read. Put only the condition and reference in the AI’s entry instructions, for example in the root `AGENTS.md`.

```text
When changing code under src/settings/, read docs/development/coding-rules.md.
Identify applicable items before editing, then check the changed diff against each item afterward.
```

Use an existing instruction entry point with a different filename if your project already has one. Naming a file `AGENTS.md` does not make every AI read it automatically.

### 3. Request the steps before and after editing together

```text
Add the feature for reading a settings file.
First read AGENTS.md and instruction files that apply to the target folder.
Briefly list applicable items from docs/development/coding-rules.md,
components to reuse, and existing check commands before editing.
Do not reread instructions whose contents were already loaded automatically.

After editing, check the current diff against R1–R3.
Run the specified existing checks for rules they can verify, such as formatting.
Also inspect code and diffs for meaning, reuse suitability, and added dependencies.
Fix violations within this task’s changes and rerun the necessary checks for those fixes.
Do not disable rules or checks to make the checks pass.
If required rules conflict, show their locations and the conflict.
If explicit precedence rules do not resolve it, ask before proceeding with the affected changes.
Finally report evidence for each item, execution results, and unverified items briefly.
Do not report checks that could not run or did not cover the files as successful.
```

In a chat that cannot read files, attach or paste applicable rules, relevant code, and check results. A path alone does not pass the contents. Run checks the AI cannot execute yourself and supply the results, or leave them marked as not run.

Save recurring review steps in, for example, `docs/development/coding-check.md`, and reference them from the entry instructions for code changes. If the AI supports registering reusable procedures, that feature can also be used. Keep the rule text in its original location; store its reference and the review sequence in the procedure.

### 4. Report automated checks separately from checks of meaning

| Item | What an automatic check can establish | What requires inspecting diffs or code |
| --- | --- | --- |
| R1 Naming | Name formats, if a naming rule is enabled | Whether `loadSettings` actually loads settings and preserves externally used names |
| R2 Reuse | Disallowed imports, if such checks exist | Whether `readJson` inputs, outputs, and failure behavior fit; finding it in search is insufficient |
| R3 No added dependencies | Changes to dependency files, if configured | New imports, dependency files, or bundled code; dependency files alone may be insufficient |
| Settings behavior | Inputs and expected results covered by relevant tests | Whether tests cover this change and necessary failure cases |

The following illustrates a report format, not actual execution results.

```text
R1: Added loadSettings. Naming check passed for its format.
    Inspected its body and caller to confirm it handles settings loading.
R2: Reused readJson from src/io/readJson.js.
    Checked inputs, return value, and failure behavior; added no duplicate JSON reader.
R3: Checked diffs of dependency files, added files, and imports. No external dependencies added.
Checks: Ran format:check, lint, and test:settings successfully.
Unverified: Behavior through actual screen operations.
```

“I read the rules” is not evidence of compliance. Compare reported locations with the diff yourself. Passing every configured check does not establish compliance with uncovered rules, meaningful names, or appropriate design.

If checks fail, have the AI distinguish problems introduced by this change from pre-existing problems. Fix current violations and report unrelated existing problems with locations and impact. Do not format or fix unrelated files. Have the AI inspect diffs produced by automatic fixes too.

## Keep rules short and consistent

Keep shared rules in one location and add folder-specific rules only for that location. Distinguish requirements from recommendations. Do not infer prohibitions merely from sample code. Record who authorized an exception, its scope, and reason; do not extend it to other tasks.

If written rules and check settings disagree, inspect established precedence and exceptions. If none resolve it, a person decides the intended rule and aligns the document and configuration. Do not let the AI choose whichever makes passing easier.

Make recurring rules concrete, update old paths, and remove unused examples. Keep the root instructions as short guidance to relevant rules and checks instead of packing every feature’s rules into them.

## Why this can reduce context use, and its limits

A stable location for rules and review steps can reduce repeated lengthy instructions and correction exchanges. Use mechanical checks for what they can decide, then give the AI relevant diagnostics and rules for the change. This can also reduce unrelated rules and large success logs passed as input.

Loading instructions and reviewing changes also consume input. Reattaching already loaded instructions or copying all rules into reports can increase usage. Report items, evidence, and results briefly, while preserving diagnostic details needed for failures. Do not omit required checks or evidence to reduce reading. Compliance and savings are not guaranteed, and this repository has not measured the savings.

## Supporting tools

Before adding a tool, check whether existing project settings and checks suffice. These are examples of available mechanisms.

- **[EditorConfig](https://editorconfig.org/):** Passes `.editorconfig` settings to supporting editors to align whitespace and line endings. It does not check meaning or all project rules, and unsupported editors do not apply the settings.
- **[Prettier](https://prettier.io/docs/comparison):** Formats code in supported languages. It can format or check formatting, but does not decide whether to reuse an existing component.
- **[ESLint](https://eslint.org/docs/latest/use/core-concepts/):** Checks JavaScript and other configured code against enabled rules and reports violations. It operates within its configured rules and target scope. It can check issues beyond formatting, but not every project requirement.
- **[Git’s pre-commit processing](https://git-scm.com/docs/githooks):** Can invoke existing checks before commits or at other configured events. Only checks actually configured and invoked apply. **[pre-commit](https://pre-commit.com/)** manages that configuration and execution. Initial runs may obtain environments or programs for checks, so use existing checks first when avoiding additional environments matters.
- **Shared repository checks:** Run configured checks and tests when changes are submitted. They can address forgotten local checks, but coverage depends on configured triggers and checks. Not run and not applicable differ from success.

## About this method

Checking your changes against rules is called **self-review**. Checks that inspect code structure or style without running the program are **static analysis**. A tool that reports rule violations is a **linter**; a tool that aligns presentation is a **formatter**. Automated checks triggered by changes in a shared repository are part of **CI (continuous integration)**.

This is a practical combination of existing instructions, self-review, and automated checks. It does not require a specially named new technique or a particular AI product.
