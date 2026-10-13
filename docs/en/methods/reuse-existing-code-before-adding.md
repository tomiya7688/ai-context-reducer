# Have the AI inspect existing code before adding similar responsibilities

> Japanese source: [AIに既存コードを調べさせ、似た役割の追加を防ぐ](../../jp/手法/AIに既存コードを調べさせ、似た役割の追加を防ぐ.md)

An AI may add `SettingsLoader` or `loadConfigData` even though `readSettingsFile` already reads settings files. Following naming conventions does not resolve the duplication of responsibilities.

A function is a callable unit of processing; a class groups behavior or state; a variable lets code refer to a value by name.

Before drafting code, describe the required work and have the AI find functions, classes, or variables that already handle it. Check whether those components meet the current conditions before choosing to reuse, extend, or create a new component.

## When to use it and how to decide

- Use it when adding a screen or command to existing functionality, or when similar functions and classes keep being added.
- When names do not reveal candidates, use inputs, outputs, data, callers, and related tests as search clues.
- Similar code may belong in separate components when conditions or reasons for change differ. Do not combine everything merely to reduce duplication.
- For a small, one-off change, a short response listing candidates and the decision is sufficient. Save a note when work will be resumed later.

## Steps to use it

### 1. Describe the work and conditions before requesting a name

Instead of “create a settings reader class,” provide the following.

```text
Add a command that reads a settings file and displays its contents.
Use the same JSON format as the existing screen.
Preserve handling of invalid files and existing screen loading behavior.
First inspect existing loading code and decide whether it fits this task.
Scope: the command, necessary shared processing, and relevant tests.
```

Inputs, outputs, failure behavior, and conditions to preserve help the AI find the same responsibility under different names. Provide file formats and requirements verified against project specifications.

### 2. Inspect candidate definitions, users, and tests

The following is a fictional project. Replace paths with locations in your project.

| Search clue | What to inspect | What it establishes |
| --- | --- | --- |
| Settings loading | Names such as `readSettingsFile` or `loadConfig`, and terms such as settings, JSON, or file loading | Candidates whose names differ |
| File format and failure behavior | `docs/specs/settings.md`, implementations, and relevant tests | Whether required inputs, results, and errors fit |
| Actual usage | Callers, construction sites, and imports | Which features use it and their assumptions |
| Variables holding similar state | Creation, update, and disposal locations | Who manages the state and how long it lasts |
| Intended responsibility boundaries | Shared-code documentation and allowed dependencies | Whether this part of the project may use the component |

Finding a candidate does not establish that it can be reused. Have the AI open its definition and users and inspect related tests. Do not force private components into public use or couple a command to screen-only code.

Start with the current feature and shared processing. Expand to other candidates when evidence points to the same work elsewhere. An unsuccessful search is not proof that a component does not exist anywhere in the project. Report search scope and uninspected areas.

### 3. Compare reuse, extension, and new creation

| Decision | Criteria | Settings example |
| --- | --- | --- |
| Reuse as is | Inputs, results, failure behavior, and allowed usage fit | Call the shared `readSettingsFile(path)` from the command |
| Extend an existing component | Fill a gap within the same responsibility while preserving existing callers’ expectations | Add necessary result information after checking the impact on existing users |
| Create a new component | Work or requirements differ, and modifying the existing component would break boundaries or behavior | Keep network settings retrieval separate from file loading |

When extending a component, locate users of changed inputs or results and check that their calls and behavior remain valid. Do not create a “shared component” that merely accumulates switches for unrelated jobs.

For a new component, report conditions existing candidates cannot meet, its responsibility, its users, and its name. Network retrieval may remain separate while reusing existing JSON interpretation afterward. Decide both the boundary and reusable parts.

Identical current values do not make variables interchangeable. `savedSettings` may hold committed values while `draftSettings` holds edits that can be cancelled. Sharing one value may cause edits to modify committed state prematurely. Inspect creation, updating actors or processing, and disposal.

Similar code need not always be combined. [Kapser and Godfrey’s paper](https://plg.uwaterloo.ca/~migod/papers/2008/emse08-ClonePatterns.pdf) discusses understanding duplication reasons, stability, ownership, and clarity before deciding how to reorganize code. [1]

### 4. Record a short decision and provide the procedure to the AI

For interrupted or handed-over work, save the following as, for example, `docs/work/reuse-plan.md`. For short tasks, the same fields can be returned in a response.

```markdown
# How this task uses existing code

- Required work and conditions to preserve:
- Inspected candidates (definition, users, and test paths with function names or headings):
- Decision: reuse / extend / create
- Reason and conditions other choices cannot meet:
- New names and responsibilities, if added:
- Existing users affected:
- Existing checks to run after editing:
- Unknowns and uninspected areas:
```

Specify the note destination, specification location, and allowed scope. This request can be copied and adapted.

```text
Add a command that reads and displays a settings file.
Specification: docs/specs/settings.md, “Loading format and errors”
Preserve existing screen behavior. Read applicable work rules first.

Before editing, search for existing functions, classes, and state variables with the same responsibility.
Use inputs, outputs, data, and failure behavior as clues, not just names.
Inspect definitions, users, related tests, and responsibility-boundary documentation.
Compare reuse, extension, and new creation.
Save a brief decision with evidence in docs/work/reuse-plan.md.
For a new component, state conditions existing candidates cannot meet and its name and responsibility.
Do not combine distinct work or state just because names or code look similar.
If specifications or boundaries conflict, ask before making affected changes.

Implement within the requested scope, then list added names and responsibilities.
Check responsibility and processing overlap, impacts on existing users, dependency direction, and shared state.
Run relevant existing tests and type/reference checks for value types and call consistency. Report results and unverified areas.
Do not report unexecuted or inapplicable checks as successful.
```

In a chat that cannot read files, attach or paste specifications, candidate definitions and users, relevant tests, and diffs. Paths alone do not provide contents. You can first ask the AI for search suggestions, provide search results yourself, and then supply requested excerpts. Provide results for checks the AI cannot run, or leave them marked as not run.

For repeated use, put a short instruction in, for example, `AGENTS.md`: when adding functions, classes, or shared state, inspect existing candidates and users and explain the reuse/extend/create decision. Refer to a saved procedure for details. Do not repeatedly copy all rules or previous candidate lists. Explicitly specify the instruction location when the AI does not load it automatically.

### 5. Check added names and responsibilities against the diff

List both new functions, classes, and variables and existing components whose responsibility was expanded. For example, request the following report. It is fictional, not an execution result.

```text
Added: showSettingsCommand — displays loaded settings in command output.
Reused: readSettingsFile in src/settings/readSettingsFile.ts — reads the file.
Overlap: delegated file reading to the existing function; added no separate SettingsLoader.
Existing users: preserved screen calls and loading error handling.
State: kept savedSettings and draftSettings separate as committed and editing state.
Checks: relevant tests and type/reference checks passed.
Unverified: actual screen operations.
```

Compare reported definitions, users, and diffs yourself. Distinguish these checks.

- Was identical processing added under another name?
- Were components with similar names but distinct work combined?
- Did an extension change existing inputs, results, or errors?
- Were separate states shared or forbidden dependencies introduced?
- Do tests and type checks cover both the new usage and affected existing usages?

Searches and type checks alone cannot determine equivalence of responsibilities. Preserve unresolved conditions rather than claiming “no duplication” or “no impact on existing features.”

## How this differs from coding-rule guidance

[Have the AI read coding rules and check its changes](follow-coding-rules.md) explains passing applicable rules and checks to the AI. This guide explains how to determine which component to reuse, and what to do if it does not fit, when a rule calls for reuse. Passing a naming check does not settle that decision.

## Why this can reduce context use, and its limits

Narrowing inspection to candidate definitions, users, and tests can reduce unrelated files supplied to find components. Brief records of reused components and reasons for new ones can also reduce later comparisons of similar code and exchanges to undo duplicate additions.

Inspection and notes also consume input. Gathering unlimited candidates or repeatedly providing complete previous lists can have the opposite effect. Focus on conditions and evidence that affect the decision without omitting necessary implementations or tests. AI decision quality and context savings from this procedure have not been measured.

## Supporting tools

- **Name and text search:** Finds candidates by function names, data names, or words describing the processing, even when an exact name is absent.
- **Editor definition and usage search:** Navigates to declarations and usages to find potential impacts of changing existing components. Dynamic calls may not be found.
- **Function and type lists:** Show function and class locations to narrow candidates in large files.
- **Similar-code detection:** Identifies similar code as candidates for inspection. Determine responsibilities and whether to combine them by reading the code and its users.
- **Git diff:** Shows added names and processing alongside changed existing components for reviewing additions and role changes.

## About this method

Using an existing component for another task is **software reuse**. Similar code fragments in multiple locations are called **code clones**. [1] This guide is an AI request procedure for checking purpose and conditions before reuse.

The referenced paper examines why code is duplicated and its maintenance effects. It does not evaluate these requests, AI decision accuracy, or context savings.

## References

1. Cory J. Kapser, Michael W. Godfrey (2008). [“Cloning considered harmful” considered harmful: patterns of cloning in software](https://plg.uwaterloo.ca/~migod/papers/2008/emse08-ClonePatterns.pdf). *Empirical Software Engineering*. DOI: [10.1007/s10664-008-9076-6](https://doi.org/10.1007/s10664-008-9076-6).
