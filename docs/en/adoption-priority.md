# Adoption Priority

> Japanese Source of Truth: [導入優先度](../jp/導入優先度.md)

Use this guide to decide which methods fit a project. The goal is not to adopt every method. Choose a method when it can reduce a recurring problem, such as repeatedly searching for the same references, reading unrelated areas, or trying to determine which checks are needed.

## Example: do not add a large system for a small change

Suppose a small game has an obvious place for its volume setting and its test. A short guide that names the file and the test is enough to start. Building a function index or a system that selects tests from each change would add work to create and maintain the system.

On the other hand, in a large project with several applications, a settings change may require finding the affected screens, loading code, and tests each time. A task guide or a change guide can help. Add a method when it reduces investigation that actually happens repeatedly.

## How to choose

### 1. Name one recurring cost

“Reduce what the AI reads” does not say which method is needed. Look at recent work and describe a concrete problem, such as:

- Finding the files to inspect first for every change
- Reading a whole large source file because the relevant part is unclear
- Looking up every test for a small change
- Continuing “just in case” searches after the answer is already clear
- Comparing multiple documents that repeat the same explanation

You do not need to build a dedicated system for a one-time problem or work whose target is already obvious.

### 2. Start by keeping the entry point short

For many projects, a small guide is enough. It should point to:

- A starting point for reaching the current work target
- The authoritative explanation or specification
- The checks needed after a change
- A way to report areas that have not been checked

If the project already has a guide such as `AGENTS.md`, improve it instead of adding a second guide with the same role. When the AI tool supports Skills, put repeated task workflows there rather than loading every procedure for every task. Link to detailed rules and specifications rather than copying them. [Basic Policy](guide.md) and [Context Reduction Basics](context-reduction-basics.md) explain how to use an entry point and narrow the material to read.

### 3. Choose one method that matches the problem

| Recurring problem | First method to consider | Why it helps |
|---|---|---|
| The places to inspect change by task and must be rediscovered | [Task Routing](task-routing.md) | Connects a task type to the first documentation, code, and tests to inspect |
| Finding affected areas from a change | [Change Routing Map](change-routing-map.md) | Reuses the inspection locations associated with each kind of change |
| Reading large files from beginning to end | [Context Priority](context-priority.md), [Source Structure Index](source-structure-index.md) | Narrows files or functions before reading the full source |
| Rechecking information that is already known | [Exploration Control](exploration-control.md), [Evidence Budget](evidence-budget.md) | Defines what needs to be known before making a decision |
| Finding tests from scratch for every change | [Validation Routing](validation-routing.md), [Change / Test Impact Routing](change-impact-routing.md) | Starts with checks and test candidates related to the change |
| Rereading the same rules or explanations | [Hierarchical Context](hierarchical-context.md), [Policy Routing](policy-routing.md), [Documentation Duplication Control](documentation-duplication-control.md) | Lets the reader use only explanations needed for the current location or check |

See the [Method Index](method-index.md) for method summaries. Try only the method that addresses the most frequent problem first; do not adopt everything at once.

### 4. Check whether it is worth keeping

After adoption, check whether:

- The guide leads to the change target without guesswork
- You read fewer unrelated files or explanations
- You still run the checks the change requires
- Updating the guide or index takes less time than it saves

If there is no benefit, simplify or remove the method. Make sure an outdated guide can lead to a broader investigation, and keep the wider checks needed for changes to shared code or public specifications. Reducing reading must not remove necessary verification.

## Guidance by project characteristics

Do not judge size by file count alone. Consider whether the work target is easy to find and whether the same investigation happens repeatedly.

- **Small:** If the target code and tests are obvious, a short entry point and the needed tests are enough. Before building an index or automated selector, see whether a direct pointer will work.
- **Several features or documents:** If the places to inspect depend on the task, consider task or change routing. Add a short current-state note when descriptions no longer make current capabilities and constraints clear.
- **Large codebase or slow tests:** Consider a source structure index if people repeatedly search large files for relevant parts. Narrow test candidates from change impact only when running the full suite is expensive and the relationship between changes and tests is known. Keep a way to run broader checks for shared code or public specifications.
- **Several people or AIs update the same repository:** Consider checking changes since the last known state before starting, and keeping a short record of the current goal and change boundaries.
- **GUI or generated artifacts:** Add the execution or distribution checks needed when a screen must be inspected or the delivered artifact differs from source. Do not make these extra steps standard for every project.

## Decision rule

Add a method when the investigation time it repeatedly saves is greater than the time needed to adopt and maintain it. Keep accuracy and required checks, then decide from whether it actually reduced reading or search time.

### Example comparison

Suppose the same kind of task takes 12 minutes to locate its target and happens eight times a month. That is about 96 minutes of searching. If an entry guide takes 30 minutes to create and 10 minutes each month to update, and reduces each search to 3 minutes, the monthly work becomes about 34 minutes; even after maintenance, the guide is worthwhile. For a one-time task that takes 12 minutes to investigate, spending 30 minutes on a dedicated index is not worthwhile.

These numbers illustrate the comparison; they are not universal thresholds. Use the actual frequency and search time from recent work, and include the effort needed to keep the method current.

## Example request to the AI

> Identify one investigation step repeated in recent tasks and choose one method from the table to reduce it. Compare what the user would create, how the AI would receive it, the work it saves, and its setup and maintenance cost. Prefer using an existing system when it is sufficient.

## Optional tools and terminology

Use the [Method Index](method-index.md) to choose a method and the [method-to-tool map](tool-method-map.md) to find optional helpers. This process is called **Method Adoption** or method selection.
