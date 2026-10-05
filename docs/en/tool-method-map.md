# Map of Methods to Optional Tools

> Japanese Source of Truth: [手法と補助ツールの対応表](../jp/手法と補助ツールの対応表.md)

Every method can be used without a dedicated tool. If you want to automate a recurring task, use this map to find a helper for the purpose. Read the method first; if manual steps or tools already available in your project are sufficient, you do not need to add another tool.

All tools in this map are optional. Commands, inputs, outputs, and operating conditions belong in each tool's README, not in the method descriptions.

## Find candidates and check results mechanically

| Method | Optional helper | What it does | Required? |
|---|---|---|---|
| [Source Structure Index](source-structure-index.md) | [source-structure-index](../../tools/common/large/source-structure-index/README.md), language-specific analysis such as [language-run](../../tools/common/small/language-run/README.md) | Indexes definitions, callers, and dependencies; returns candidates by name or changed file. Runs supported lightweight analyzers and saves results. | No |
| [Choose tests from change impact](change-impact-routing.md) | [affected-tests (Python)](../../tools/python/medium/affected-tests/README.md), [affected-tests (Go)](../../tools/go/medium/affected-tests/README.md), source-structure-index | Finds tests that may be affected by changed code. | No |
| [Check syntax](syntax-health-validation.md) | [syntax-health](../../tools/common/small/syntax-health/README.md) | Runs an available compatible parser and reports candidate syntax errors. | No; only when a compatible parser is available |
| [Check rules that apply](policy-routing.md) | [policy-index](../../tools/common/medium/policy-index/README.md), [policy-check](../../tools/common/medium/policy-check/README.md) | Finds relevant rules in policy documents and checks files against rules that can be expressed mechanically. | No |
| [Choose necessary validation](validation-routing.md) | [validation-plan](../../tools/common/medium/validation-plan/README.md) | Suggests initial validation candidates from changed file paths. | No |

## Combine recurring steps

| Method | Optional helper | What it does | Required? |
|---|---|---|---|
| [Task and change guides](task-routing.md) | [change-router](../../tools/common/medium/change-router/README.md), [tool-selector](../../tools/common/small/tool-selector/README.md) | Suggests tests and docs from changed files; selects available helper tools and their order. | No |
| [Prepare a task note or Context Pack](context-pack.md) | [context-pack-builder](../../tools/common/medium/context-pack-builder/README.md) | Drafts a task note with goals, references, and completion criteria from task materials. | No |
| [Instructions by location](hierarchical-context.md) | [scoped-guides](../../tools/common/small/scoped-guides/README.md) | Finds candidate guides in the target file's parent folders. | No |
| [Create standard text and files](boilerplate-generation.md) | [template](../../tools/common/medium/template/README.md) | Replaces template placeholders with supplied values and checks for unresolved placeholders or drift. | No |

## Read only relevant information

| Method | Optional helper | What it does | Required? |
|---|---|---|---|
| [Context Manifest](context-manifest.md) | [context-manifest](../../tools/common/large/context-manifest/README.md) | Builds a reference catalog with file roles and priorities. | No |
| [Prioritize reading candidates](context-priority.md) | [context-budget](../../tools/common/large/context-budget/README.md), [hotspot-report](../../tools/common/large/hotspot-report/README.md) | Estimates candidate size and reports large or deep files to consider. It does not determine relevance. | No; supporting signals only |
| [Check remote changes first](remote-context.md) | [remote-delta](../../tools/common/medium/remote-delta/README.md) | Summarizes local and remote Git changes in a compact list. | No |
| [Set a stop condition](exploration-control.md) | [acceptance-extractor](../../tools/common/medium/acceptance-extractor/README.md), [exploration-stop-check](../../tools/common/medium/exploration-stop-check/README.md) | Extracts goals and criteria from task notes; checks whether enough information exists to stop exploring. | No |
| [Normally skip unrelated files](context-exclusion.md) | [ignore-candidates](../../tools/common/medium/ignore-candidates/README.md) | Suggests paths that may be low priority to read; it does not change ignore rules. | No; it only suggests candidates |
| [Map file and module responsibilities](responsibility-map.md) | [responsibility-candidates](../../tools/common/medium/responsibility-candidates/README.md) | Drafts a responsibility table from file paths; people verify the roles in source material. | No |
| [Choose what to read from existing boundaries](architecture-boundary-routing.md) | [architecture-boundary-router](../../tools/common/medium/architecture-boundary-router/README.md) | Uses existing architecture information to suggest boundaries and files to inspect first. | No |
| [Manage repeated documentation](documentation-duplication-control.md) | [doc-duplicate-hints](../../tools/common/medium/doc-duplicate-hints/README.md) | Suggests similar documents for review; it does not choose a source of truth or merge content. | No; it only suggests candidates |
| [Choose analysis for a language](language-tool-setup.md) | [language-setup](../../tools/common/small/language-setup/README.md), [language-run](../../tools/common/small/language-run/README.md), deeper [acr-toolbox](../../tools/common/native/acr-toolbox/README.md) analysis when needed | Checks project languages and available runtimes, runs supported lightweight analysis, and provides deeper analysis when needed. | No |
| [Reduce additional installations](portable-tools.md) | [materialize-tools](../../tools/common/small/materialize-tools/README.md), language-setup | Places distributed portable tools without installing a new runtime. | No |

This map lists representative helpers in this repository. For guidance on choosing external tools, see [External Tool Reference Policy](external-tool-reference-policy.md). For all commands and distribution details, see [tools/README.md](../../tools/README.md).

## How to use this map

First choose a method from the user's problem and decide what result is needed. Use the table to find an optional helper, read its README, and run it only if it is available. Give the AI relevant candidates rather than the full output, then verify selected code and tests. Having a tool does not by itself reduce context.

> I need to investigate [task]. If an available helper supports the method, run it and show only relevant candidates with reasons. Check the selected original sources and tests, then report results and anything not verified.

## Terminology

“Helper tool” means optional mechanical assistance. The person selects the method and references; the tool narrows candidates and the AI checks the selected sources. This can be called **tool-assisted Context Routing**.
