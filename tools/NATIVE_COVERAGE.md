# Native Tools Coverage

`acr-toolbox` は Common tools のうち、導入頻度が高く依存を増やしたくない機能を Go 製単一バイナリへ統合します。

## Native available

| Method / use | Python tool | Native subcommand |
|---|---|---|
| repository analysis | `analyze-and-recommend` | `analyze` |
| Search-first text search | `text-search` | `search` |
| path search | `path-find` | `find` |
| bounded tree | `tree-view` | `tree` |
| repo statistics | `repo-stats` | `stats` |
| heading-first docs | `doc-index` | `doc-index` |
| bounded source excerpt | `target-slice` | `slice` |
| compact validation logs | `compact-log` | `compact-log` |
| runtime/environment check | `environment-plan` の一部 | `env` |

Windows / Linux / macOS では prebuilt `acr-toolbox` を優先し、利用できない場合は Python implementation へ fallback します。

## Python-only / not yet native

現時点で次は Python implementation が中心です。

### Common medium
- `compact-diff`
- `remote-delta`
- `change-router`
- `acceptance-extractor`
- `exploration-stop-check`
- `validation-plan`
- `context-pack-builder`
- `policy-index`
- `responsibility-candidates`
- `doc-duplicate-hints`
- `ignore-candidates`
- `materialize-tools`

### Common large
- `context-manifest`
- `hotspot-report`
- `context-budget`

### Language-specific
- Python symbols / import / graph
- C# symbols / project / graph
- Go symbols / import / graph
- C / C++ symbols / include / graph
- GDScript symbols / dependency / Godot scene graph

言語固有解析は native 化を急がず、まず Common の繰り返し利用が多い処理を優先します。高品質な external parser / compiler / `ctags` / `ast-grep` 等が利用可能ならそれらも候補にします。

## Native priority

次の統合優先順位を推奨します。

1. `compact-diff` / `remote-delta`
2. `context-budget` / `hotspot-report`
3. `acceptance-extractor` / `exploration-stop-check`
4. `context-manifest` / `context-pack-builder`
5. project-specific / language-specific analysis only when maintenance cost is justified

原則は native coverage 100% を目標にせず、**インストール不要にする効果が高い機能だけ native 化する**ことです。
