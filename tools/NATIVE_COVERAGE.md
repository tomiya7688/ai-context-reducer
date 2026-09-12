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
| compact Git diff | `compact-diff` | `compact-diff` |
| remote delta | `remote-delta` | `remote-delta` |
| language runtime detection | `language-environment-plan` | `language-env` |
| runtime/environment check | `environment-plan` の一部 | `env` |

Windows / Linux / macOS では prebuilt `acr-toolbox` を優先し、利用できない場合は Python implementation へ fallback します。

## Python-only / not yet native

現時点で次は Python implementation が中心です。

### Common medium
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

言語固有解析は native 化を急がず、まず対象言語の標準環境が存在するかを `language-env` で判定します。

- Python: `python3` / `python`
- C#: `dotnet`
- Go: `go`
- C: `gcc` / `clang` / `cc`
- C++: `g++` / `clang++` / `c++`
- GDScript: `godot4` / `godot`

対応環境が無い場合は、依存を自動インストールせずその言語固有toolをスキップします。高品質な external parser / compiler / `ctags` / `ast-grep` 等が既に利用可能なら、それらも優先候補にできます。

## Native priority

次の統合優先順位を推奨します。

1. `context-budget` / `hotspot-report`
2. `acceptance-extractor` / `exploration-stop-check`
3. `context-manifest` / `context-pack-builder`
4. `change-router` / `validation-plan`
5. project-specific / language-specific analysis only when maintenance cost is justified

原則は native coverage 100% を目標にせず、**インストール不要にする効果が高い機能だけ native 化する**ことです。
