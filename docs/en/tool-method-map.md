# Map of Methods to Optional Tools

> Japanese Source of Truth: [手法と補助ツールの対応表](../jp/ツールとの対応.md)

Every method can be used without a dedicated tool. If you want to automate a recurring task, use this map to find a helper for the purpose. Read the method first; if manual steps or tools already available in your project are sufficient, you do not need to add another tool.

All tools in this map are optional. Commands, inputs, outputs, and operating conditions belong in each tool's README, not in the method descriptions.

## Find candidates and check results mechanically

| Method | Optional helper | Required? |
|---|---|---|
| [Source Structure Index](source-structure-index.md) | [source-structure-index](../../tools/common/large/source-structure-index/README.md), language-specific analysis such as [language-run](../../tools/common/small/language-run/README.md) | No |
| [Choose tests from change impact](change-impact-routing.md) | [affected-tests (Python)](../../tools/python/medium/affected-tests/README.md), [affected-tests (Go)](../../tools/go/medium/affected-tests/README.md), source-structure-index | No |
| [Check syntax](syntax-health-validation.md) | [syntax-health](../../tools/common/small/syntax-health/README.md) | No; only when a compatible parser is available |
| [Check rules that apply](policy-routing.md) | [policy-index](../../tools/common/medium/policy-index/README.md), [policy-check](../../tools/common/medium/policy-check/README.md) | No |
| [Choose necessary validation](validation-routing.md) | [validation-plan](../../tools/common/medium/validation-plan/README.md) | No |

## Combine recurring steps

| Method | Optional helper | Required? |
|---|---|---|
| [Task and change guides](task-routing.md) | [change-router](../../tools/common/medium/change-router/README.md), [tool-selector](../../tools/common/small/tool-selector/README.md) | No |
| [Prepare a task note or Context Pack](context-pack.md) | [context-pack-builder](../../tools/common/medium/context-pack-builder/README.md) | No |
| [Instructions by location](hierarchical-context.md) | [scoped-guides](../../tools/common/small/scoped-guides/README.md) | No |
| [Create standard text and files](boilerplate-generation.md) | [template](../../tools/common/medium/template/README.md) | No |

## Read only relevant information

| Method | Optional helper | Required? |
|---|---|---|
| [Context Manifest](context-manifest.md) | [context-manifest](../../tools/common/large/context-manifest/README.md) | No |
| [Prioritize reading candidates](context-priority.md) | [context-budget](../../tools/common/large/context-budget/README.md), [hotspot-report](../../tools/common/large/hotspot-report/README.md) | No; supporting signals only |
| [Check remote changes first](remote-context.md) | [remote-delta](../../tools/common/medium/remote-delta/README.md) | No |
| [Set a stop condition](exploration-control.md) | [acceptance-extractor](../../tools/common/medium/acceptance-extractor/README.md), [exploration-stop-check](../../tools/common/medium/exploration-stop-check/README.md) | No |
| [Normally skip unrelated files](context-exclusion.md) | [ignore-candidates](../../tools/common/medium/ignore-candidates/README.md) | No; it only suggests candidates |
| [Map file and module responsibilities](responsibility-map.md) | [responsibility-candidates](../../tools/common/medium/responsibility-candidates/README.md) | No |
| [Choose what to read from existing boundaries](architecture-boundary-routing.md) | [architecture-boundary-router](../../tools/common/medium/architecture-boundary-router/README.md) | No |
| [Manage repeated documentation](documentation-duplication-control.md) | [doc-duplicate-hints](../../tools/common/medium/doc-duplicate-hints/README.md) | No; it only suggests candidates |
| [Choose analysis for a language](language-tool-setup.md) | [language-setup](../../tools/common/small/language-setup/README.md), [language-run](../../tools/common/small/language-run/README.md), deeper [acr-toolbox](../../tools/common/native/acr-toolbox/README.md) analysis when needed | No |
| [Reduce additional installations](portable-tools.md) | [materialize-tools](../../tools/common/small/materialize-tools/README.md), language-setup | No |

This map lists representative helpers in this repository. For guidance on choosing external tools, see [External Tool Reference Policy](external-tool-reference-policy.md). For all commands and distribution details, see [tools/README.md](../../tools/README.md).
