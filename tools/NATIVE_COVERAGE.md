# Native Tools Coverage

`acr-toolbox` は Common tools のうち、導入頻度が高く依存を増やしたくない機能を Go 製単一バイナリへ統合します。

Go language-specific / portable fallback toolは、`acr-toolbox` へ無理に統合せず standalone Go binary として持つ場合があります。

## Native available

| Method / use | Python tool | Native implementation |
|---|---|---|
| repository analysis | `analyze-and-recommend` | `acr-toolbox analyze` |
| Search-first text search | `text-search` | `acr-toolbox search` |
| path search | `path-find` | `acr-toolbox find` |
| bounded tree | `tree-view` | `acr-toolbox tree` |
| repo statistics | `repo-stats` | `acr-toolbox stats` |
| heading-first docs | `doc-index` | `acr-toolbox doc-index` |
| bounded source excerpt | `target-slice` | `acr-toolbox slice` |
| compact validation logs | `compact-log` | `acr-toolbox compact-log` |
| compact Git diff | `compact-diff` | `acr-toolbox compact-diff` |
| remote delta | `remote-delta` | `acr-toolbox remote-delta` |
| language runtime detection | `language-environment-plan` | `acr-toolbox language-env` |
| runtime/environment check | `environment-plan` の一部 | `acr-toolbox env` |
| affected test selection | Python `affected-tests` | standalone Go `affected-tests` |
| Go symbol extraction | previous Python implementation | standalone Go `go-symbols` |
| Go import map | previous Python implementation | standalone Go `go-import-map` |
| Go package graph | previous Python implementation | standalone Go `go-package-graph` |

Windows / Linux / macOS では prebuilt/native binaryを優先し、利用できない場合は対応するPython implementationまたは別fallbackへ切り替えます。

Standalone Go toolsは各directoryの `build.bat` / `build.sh` で一発buildできる形を基本とします。

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
- C / C++ symbols / include / graph
- GDScript symbols / dependency / Godot scene graph

Go symbols / import map / package graph はGoネイティブ化済みです。

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

Python側へgenericな新規toolを追加した場合、Go側に同等機能を実装できるなら積極的に追加します。ただし共有コード化はせず、入出力契約とtestで対応を保ちます。

原則は native coverage 100% を目的化せず、**インストール不要にする効果が高い機能を優先して native 化する**ことです。
