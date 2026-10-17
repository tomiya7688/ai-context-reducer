# Write a README that leads people and AI to the information they need

> Japanese source: [人とAIが必要な情報へ進めるREADMEを書く](../../jp/手法/人とAIが必要な情報へ進めるREADMEを書く.md)

If readers cannot work out how to start, or you repeatedly explain where specifications and work rules are when asking AI for changes, organize the README as an entry point. Briefly state its purpose and first trial, then direct readers to detailed operations, specifications, and development procedures.

Give people requesting AI work a heading that identifies which sources to provide. Links alone do not ensure that the AI reads them automatically; name the sources in requests or instruction files too.

## Decide what belongs in the README

| Reader’s purpose | What to include | Example detail location |
| --- | --- | --- |
| Understand the project | Purpose, audience, main limitations or release status | Feature explanation if needed |
| Try it once | First operation and expected result | `docs/getting-started.md` |
| Look up operations or specifications | Links describing what readers will learn | `docs/usage.md`, `docs/csv-format.md` |
| Ask questions or report problems | Actual contact channel and instructions | `docs/support.md` or the existing support destination |
| Request AI changes | Work rules, relevant specifications, and checks | `AGENTS.md`, `docs/development.md` |

These are example locations. Reuse existing documents and channels without duplicating information in new files. A small project may keep short explanations in one README.

Consider separation when people repeatedly read the same long explanations, copied specifications disagree, or newcomers cannot choose their next page. Keep short explanations in place when following another link would cost more effort.

## Steps to use the method

### 1. Decide who will read it and what they should try first

For example: “Someone familiar with CSV but new to this tool can try formatting dates once.” Verify purpose, audience, prerequisites, sample input, operations, and expected results against existing documentation or actual behavior.

Do not have the AI invent launch commands, unsupported features, or unused support channels. Mark unknown items for confirmation. The first procedure may differ for end users and developers.

### 2. Locate details and write a short guide

This fictional CSV tool illustrates a layout. You do not have to reorganize an existing project to match it.

```text
README.md                  Purpose, first trial, and next sources
AGENTS.md                  AI work rules and references
docs/getting-started.md     Prerequisites, setup, and first operation
docs/usage.md               Detailed operations
docs/csv-format.md          Supported dates and CSV format
docs/development.md         Development and checking procedures
docs/support.md             Contact channel and required report information
```

For example, a root `README.md` could contain the following. Replace explanations and links with real ones for your project. Link definitions at the bottom match the fictional layout above.

```markdown
# CSV date formatter

A tool that normalizes CSV dates to YYYY-MM-DD.
Check [CSV format specifications][format] for supported input.

## Try it first

Follow [setup and the first operation][start] to process one sample CSV.
The first trial is complete when the sample 2026/10/17 becomes 2026-10-17.

## Detailed usage and support

- [Operations][usage]: Find settings and error-handling instructions.
- [Support][support]: Find where to report problems and what information to include.

## When asking AI to make changes

First have it read the [work rules][rules].
For CSV format changes, supply the [format specification][format].
Supply the [development procedures][development] for checks.
For other tasks, add only relevant sources.

[start]: docs/getting-started.md
[usage]: docs/usage.md
[format]: docs/csv-format.md
[support]: docs/support.md
[rules]: AGENTS.md
[development]: docs/development.md
```

Use action-oriented headings such as “Try it first” and “When asking AI to make changes,” rather than only “Overview” and “Other.” Describe what links explain instead of labeling them merely “here.”

For files in the same project, use paths relative to the README. `docs/csv-format.md` means the file inside the `docs` folder next to that README. From another document location, adjust the path relative to that document.

Keep detailed specifications, operations, and work rules in their respective source documents. Put short purposes and references in the README without copying full specifications. Update links and short descriptions when behavior or file locations change.

### 3. Direct AI instructions to the relevant section and sources

If the example project uses `AGENTS.md`, add a short guide such as:

```text
For the first task, check README.md’s “When asking AI to make changes” section.
For CSV date-format changes, read docs/csv-format.md and check effects on consumers.
For checks, read the docs/development.md procedures relevant to this change.
Do not read every linked source solely because it is linked.
Do not follow links back to reread instruction files already checked at the same revision.
```

Keep conditions and locations here, without copying detailed specifications. Preserve existing rules and add only a short guide. Automatic instruction loading differs by environment; check settings or read records.

If instructions do not load automatically, or for one-time work, specify them in the request.

```text
I want to change the CSV date format. First read AGENTS.md and
README.md’s “When asking AI to make changes” section.
Follow it to docs/csv-format.md and the checking procedures for this change.
Inspect relevant consumers too. Briefly state the sources read and why they apply.
Do not copy detailed specifications into the README.
```

For a chat that cannot read files, attach or paste the section, applicable rules, and required specifications or code. Paths alone do not supply content. If the README conflicts with specifications or code, have the AI check current facts in original sources and report outdated guidance.

### 4. Supply material and scope when asking AI to revise a README

```text
Make the README let a newcomer try the tool once and check the result.
The reader knows CSV but does not know this tool’s operations.

Inspect the existing README, setup, usage, specification, development docs, and support destination.
Briefly identify purpose, first operation, expected result, detailed documentation, and support.
For people asking AI for changes, identify work rules, specifications, and checks by change type.
Use existing relative links without copying full details.

Do not invent missing information or unverified commands; report gaps.
Preserve required sections; explain any necessary heading or scope changes.
Change only the README proposal and necessary navigation links, not implementation or specifications.
Report consulted sources, link destinations, gaps, and unverified operations.
```

If the structure keeps changing, use [headings and order supplied beforehand](write-from-document-outline.md). README organization does not require a simultaneous project redesign.

### 5. Check destinations and their actual contents yourself

- Check that newcomers can find purpose, first operation and expected result, details, and support.
- Confirm not only that links exist but that their destinations contain the promised explanation.
- Give the AI one task and compare reported rules and sources with visible work records or responses.
- Keep unperformed operations and unread sources unverified. Link checks do not establish successful operations or actual AI reading.

## Why this can reduce searching and reading

Short, purpose-based entry points help people avoid rediscovering setup or support information. Giving the AI the current section and necessary references can avoid sending unrelated operating instructions or long histories each time. Keeping details in one place also reduces comparisons between inconsistent copies.

Reading destinations and maintaining navigation still take work. Having the AI read every linked page can increase usage. A shorter README alone does not establish lower consumption; preserve required evidence and compare actual reading scope or measurable usage.

## Supporting tools and features

- **Heading-based tables of contents:** Jump to the relevant section. They can help locate starting points in longer READMEs.
- **Markdown preview:** Shows reader-facing formatting for Markdown, a format using symbols for headings and links. It can help inspect readability in the destination environment.
- **Link checking:** Finds missing destinations. It can reveal navigation missed during moves; destination content and operating results need separate checks.

## About this organization

Use purpose-based README links together with explicit instructions telling the AI what to read. GitHub describes purpose, getting started, support, and relative links; Google also recommends a short overview with usage, contact information, and related documentation. See [GitHub’s guide](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes) and [Google’s guide](https://google.github.io/styleguide/docguide/READMEs.html).

[Diátaxis](https://diataxis.fr/) distinguishes learning-oriented material, task-oriented procedures, technical reference, and explanation. It is a documentation framework, not a measurement of usage savings for this README example or these AI requests.
