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
| context-size routing estimate | `context-budget` | `acr-toolbox context-budget` |
| large/deep file routing | `hotspot-report` | `acr-toolbox hotspot-report` |
| prioritized repository context manifest | `context-manifest` | `acr-toolbox context-manifest` |
| Context Pack Markdown generation | `context-pack-builder` | `acr-toolbox context-pack-builder` |
| changed file -> test/doc routing | `change-router` | `acr-toolbox change-router` |
| changed file -> validation-kind routing | `validation-plan` | `acr-toolbox validation-plan` |
| Responsibility Map starter Markdown | `responsibility-candidates` | `acr-toolbox responsibility-candidates` |
| Goal/Required/Acceptance/Deferred extraction | `acceptance-extractor` | `acr-toolbox acceptance-extractor` |
| exploration stop heuristic | `exploration-stop-check` | `acr-toolbox exploration-stop-check` |
| reusable source structure index / bounded graph expansion / affected scope | `source-structure-index` | `acr-toolbox structure-index` |
| safe portable tool materialization | `materialize-tools` | `acr-toolbox materialize` |
| language runtime detection | `language-environment-plan` | `acr-toolbox language-env` |
| runtime/environment check | `environment-plan` の一部 | `acr-toolbox env` |
| affected test selection | Python `affected-tests` | standalone Go `affected-tests` |
| Go symbol extraction | previous Python implementation | standalone Go `go-symbols` |
| Go import map | previous Python implementation | standalone Go `go-import-map` |
| Go package graph | previous Python implementation | standalone Go `go-package-graph` |

Windows / Linux / macOS では prebuilt/native binaryを優先し、利用できない場合は対応するPython implementationまたは別fallbackへ切り替えます。

Standalone Go toolsは各directoryの `build.bat` / `build.sh` で一発buildできる形を基本とします。

`materialize-tools` はbootstrap用途でも使えるよう、Python版とは独立して `acr-toolbox materialize` を持ちます。native版は実行中のtoolbox自身とOS向けwrapperを `bin/` + root wrapper layoutへ配置し、preview / conflict protection / hash manifestを同じ契約で提供します。

`context-budget` / `hotspot-report` もPythonとGoで実装コードを共有せず、自己説明的JSON契約とtargeted testで意味を揃えます。内部scanは既定でunlimited、agentへの返却だけをboundedにする方針です。

`context-manifest` はPython/nativeともfull repository scanを許容し、priority manifestだけをboundedに返します。`context-pack-builder` は成果物がMarkdownなのでJSON化せず、Git取得状態の意味とMarkdown contractをtestで揃えます。

`change-router` は内部test/doc indexを既定unlimitedにし、agent-visible routesだけをboundedにします。`validation-plan` はtoken-based path classificationでshort substring false positiveを避けます。両方ともPython/Goを共有コードなしで実装します。

`responsibility-candidates` もMarkdown artifactを維持した独立実装です。内部code scanは既定unlimited、table rowsだけをboundedにし、stat/walk/truncationはMarkdown commentで伝えます。

`acceptance-extractor` / `exploration-stop-check` も独立実装です。英語termのword-boundary semantics、日本語term、truncation、missing/read errorをtestで合わせます。

## Python-only / not yet native

現時点で次は Python implementation が中心です。

### Common medium
- `policy-index`
- `doc-duplicate-hints`
- `ignore-candidates`
- `structural-search`

`structural-search` は外部 `ast-grep` が存在すればそのnative parserをbackendとして再利用し、無い場合だけPython stdlib AST fallbackを使います。Goで低品質な独自multi-language parserを重複実装するより、この境界を維持します。

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

次の候補は、native化そのものより利用頻度とmaintenance costを見て判断します。

1. `policy-index`
2. `doc-duplicate-hints` / `ignore-candidates`
3. project-specific / language-specific analysis only when maintenance cost is justified

`structural-search` はexternal `ast-grep` reuseを優先するため、native coverageのためだけに別parserを作りません。

Python側へgenericな新規toolを追加した場合、Go側に同等機能を実装できるなら積極的に追加します。ただし共有コード化はせず、入出力契約とtestで対応を保ちます。

原則は native coverage 100% を目的化せず、**インストール不要にする効果が高い機能を優先して native 化する**ことです。
