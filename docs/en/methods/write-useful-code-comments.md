# Have the AI write code comments that help readers

> Japanese source: [AIに読む人の役に立つコードコメントを書かせる](../../jp/手法/AIに読む人の役に立つコードコメントを書かせる.md)

Asking an AI to “add comments” may produce explanations such as “get the value” or “return the result” that merely repeat the code. Attempts to shorten comments can also remove required declaration comments or present inferred reasons as established facts.

Provide comment rules and the intended reader first, then ask for information that reader cannot readily learn from the code alone. Explain inputs and results to people using a function, and reasons and constraints to people changing its implementation.

## When to use it and how to decide

- For functions used by other code, document what callers need to know: input units, return values, and failure behavior.
- Inside implementations, explain ordering constraints, compatibility branches, or special meanings of values, with evidence.
- If names and code make an explanation obvious and comments are optional, you need not add it. If comments are required, keep them and describe the declaration’s role, inputs, and results concretely.
- If an old comment disagrees with the implementation, first determine whether the comment needs updating or the implementation violates the intended specification.

## Steps to use it

### 1. Specify comment rules and readers

Have the AI read instructions that apply to the target file, comment rules, and nearby examples. Examples illustrate style; older comments that conflict with rules are not authoritative.

If no rule document exists, save team-agreed scope, language, required items, and checks in, for example, `docs/development/comment-rules.md`. If rules already exist in `CONTRIBUTING.md` or elsewhere, use that location rather than copying them.

Put a reference in the AI’s entry instructions, such as `AGENTS.md`.

```text
When adding or changing code, read docs/development/comment-rules.md.
Separate information for callers from reasons needed by maintainers,
and check that changed code agrees with existing comments.
```

Specify readers in the request, such as “developers calling this function” or “developers later changing this implementation.” Follow project requirements for format, language, and mandatory locations first.

In this repository, [Issue #51](https://github.com/tomiya7688/ai-context-reducer/issues/51) defines a policy for Japanese structured comments immediately before declarations under `tools/`, with ordinary Japanese comments inside implementations. Do not apply that policy uniformly to other projects or every language. Check the target project’s authoritative rules and checks available at that time.

### 2. Decide what belongs at each comment location

| Location | What readers need to know | Example content |
| --- | --- | --- |
| Function or type declaration | What it provides and conditions for using it | Input meanings and units, return values, state changes, failure behavior |
| Inside processing | Why an order or value matters and what changes could break | Compatibility constraints, ordering reasons, conditions that must always hold |
| Code with detailed design documentation | Which decision applies here | A short essential reason and a reference to the detailed section |

Keep essential meaning in the comment so readers do not have to open another document every time. Store lengthy design history in the design document.

The following is a fictional Python project, not this repository’s format rules. Assume the stated behavior has been checked against its implementation and specification.

Compare these comments for callers.

```python
# Before: merely restates the name
def read_timeout(settings):
    """Get the timeout."""
    ...
```

```python
# After: describes conditions callers need
def read_timeout(settings):
    """Return the configured timeout in seconds; default to 30, and raise ValueError for nonpositive values."""
    ...
```

This explains units, the default, and the handling of nonpositive values. The `...` represents omitted implementation. Repeating the name or parameter list does not establish these facts.

For an internal comment, suppose the design document records that older configurations defaulted to 30 seconds and compatibility must be preserved.

```python
# Before: repeats the next line
# Get the timeout from settings.
timeout = settings.get("timeout_seconds", 30)
```

```python
# After: explains a reason to know before changing the value
# Preserve the previous 30-second default so older configurations keep their behavior.
timeout = settings.get("timeout_seconds", 30)
```

Seeing 30 in code does not establish compatibility as the historical reason. If the reason is not recorded, do not have the AI invent it. Verify and provide evidence as described in [Share decision reasons](share-decision-reasons.md). Document observable behavior and report any unknown reason separately.

### 3. Decide whether to add, update, or remove comments

| Situation | What to ask the AI to do |
| --- | --- |
| A required location lacks a comment | Fill required items with declaration-specific meaning; leave no empty template |
| Important units, constraints, or reasons are unclear from code | Verify evidence and add a short explanation |
| Behavior changed and the explanation is outdated | Verify the intended specification and implementation, then update the explanation with the change |
| A comment only repeats code | Check whether it is required; make required content concrete, or remove it if optional and removable |
| Comment and code disagree, or a reason lacks evidence | Establish the intended behavior or reason; report what remains unresolved |

In a project requiring comments for each declaration, do not remove them merely because the code is obvious. If responsibility, processing, parameters, and return values are mandatory, describe what this declaration does, accepts, and returns. Generic filler such as “perform processing” is not useful even if it fills every field.

### 4. Request preparation and a review of the changes together

Replace these paths with files that exist in your project.

```text
Review and revise comments for changed sections of src/settings/reader.py.
First read applicable instructions and docs/development/comment-rules.md.
Check required locations, items, language, and format. Use nearby examples as guidance, not outdated rules.
Declaration comments are for developers using this function; internal comments are for developers maintaining it.
Inspect the changed processing, callers, relevant specifications, and tests.
This task changes comments only; do not change implementation.

For each comment, ask what readers learn that the code alone does not make clear.
Keep required explanations and make roles, inputs, and results concrete.
Write reasons or guarantees only when supported; report unknowns.
If comments and code disagree and you cannot establish which is correct, ask before revising that part.
If required rules conflict and explicit precedence does not resolve them, show the locations and ask.

After editing, check the diff against rules for required items, useful content, and agreement with implementation.
If an existing comment checker is available, confirm its scope and invocation, then run it.
Briefly report added, updated, or removed locations, what readers learn and its evidence,
check results, and unverified areas.
Do not report checks that were not run or did not cover the files as successful.
```

In a chat that cannot read files, attach or paste rules, the target code and its callers, necessary specifications, and the diff. Paths alone do not provide contents. If the AI cannot run checks, supply results yourself or have it report them as not run.

A report could look like this. It illustrates the format, not actual check results.

```text
Updated reader.py / read_timeout documentation:
  Callers can identify units, defaults, and handling of nonpositive values.
  Evidence: function body, caller, settings specification, and relevant tests.
Updated the default-value internal comment:
  Explained retaining 30 seconds, supported by the design document’s compatibility section.
Format check: Existing comment check passed; it covers required fields and syntax.
Unverified: A first-time developer still needs to judge whether the content communicates enough.
Implementation diff: None.
```

[Have the AI read coding rules and check its changes](follow-coding-rules.md) also explains storing rules and reviewing changes. Do not copy the same rule text into the comment procedure.

## Check completion

Have the AI check correspondence between content and evidence, not just field presence. Also compare important conditions and reasons with their original sources yourself.

- **Format:** Do declaration targets, required fields, language, and syntax follow the rules? Use automatic checks within their actual coverage.
- **Content:** Can readers learn the declaration’s specific role, usage conditions, or reasons? Are there empty fields or generic filler?
- **Agreement:** Do inputs, results, errors, and state changes match the implementation? Does rewriting a comment conceal an implementation/specification mismatch?
- **Evidence:** Were design reasons or guarantees such as “always succeeds” guessed?
- **Scope:** Were unnecessary comments added in bulk? Did implementation changes enter a comment-only task?

Passing a format check does not establish usefulness or factual accuracy. Judge whether readers can understand usage and change constraints rather than treating more comments or characters as success.

## Why this can reduce context use, and its limits

Providing rules and readers first, then reviewing comments for changed code, can reduce repeated corrections of format or missing information. Short comments containing important conditions can also reduce reading whole functions or historical discussions merely to learn how to use them.

Added comments consume input too. Repeating long design history or obvious explanations at every declaration can have the opposite effect. Keep necessary conditions and reasons short, and detailed history in one place. When the task needs implementation verification, inspect original code and tests rather than relying on comments alone. Savings from this comment method have not been measured.

## Supporting tools

- **Existing comment checks:** Check comment presence, required fields, or syntax. They can verify mandated format; useful content needs separate review.
- **Editor function documentation display:** Shows explanations attached to declarations. It can help check whether callers can find necessary information. Supported formats depend on the language and editor.
- **Git diff:** Shows comment and implementation changes together. It helps find missed documentation updates or implementation changes mixed into comment revisions.

## About this method

Explanations near declarations that describe usage and conditions are called **documentation comments**. In Python, explanatory strings placed at the start of functions and similar definitions are called **docstrings**.

[Go’s comment guide](https://go.dev/doc/comment) separates caller-facing behavior and results from internal implementation details. [Python’s PEP 257](https://peps.python.org/pep-0257/) discusses behavior, parameters, return values, side effects, exceptions, and usage conditions. [Google’s C++ guide](https://google.github.io/styleguide/cppguide.html#Comments) advises against restating obvious code and explains describing intent for unclear processing. Side effects are changes to files or other state beyond a returned value.

These are language- or organization-specific guidelines. Go and Python even differ in how descriptions begin; do not transplant formatting or required locations uniformly. Follow the target project’s rules.
