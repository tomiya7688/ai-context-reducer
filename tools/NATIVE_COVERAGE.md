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
| Git history / repository object health | `git-history-health` | `acr-toolbox git-history-health` |
| syntax health via existing Tree-sitter parser | `syntax-health` | `acr-toolbox syntax-health` |
| context-size routing estimate | `context-budget` | `acr-toolbox context-budget` |
| large/deep file routing | `hotspot-report` | `acr-toolbox hotspot-report` |
| prioritized repository context manifest | `context-manifest` | `acr-toolbox context-manifest` |
| Context Pack Markdown generation | `context-pack-builder` | `acr-toolbox context-pack-builder` |
| changed file -> test/doc routing | `change-router` | `acr-toolbox change-router` |
| changed file -> validation-kind routing | `validation-plan` | `acr-toolbox validation-plan` |
| Responsibility Map starter Markdown | `responsibility-candidates` | `acr-toolbox responsibility-candidates` |
| policy/rule routing index | `policy-index` | `acr-toolbox policy-index` |
| repeated documentation hints | `doc-duplicate-hints` | `acr-toolbox doc-duplicate-hints` |
| low-value context path hints | `ignore-candidates` | `acr-toolbox ignore-candidates` |
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

`text-search` / `path-find` / `repo-stats` はPython/nativeともself-describing JSONをSource of Truthにし、PATH上に既存 `rg` / `fd` / `scc` があればoptional backendとして再利用します。未導入ならnormal portable fallback、見つかったbackendが失敗した場合だけfallback情報を返します。external backendのraw schemaはcallerへ漏らしません。

`git-history-health` もPython/nativeを独立実装し、既存 `git-sizer --json --json-version=2` の出力から concern threshold以上のmetricだけをbounded JSONへ圧縮します。Git object graph analyzerは再実装せず、git-sizer未導入時は `external_backend_unavailable` を返します。保存済みJSONは `--json-input` で同じcontractへ変換できます。

`syntax-health` は既存 `tree-sitter parse --json-summary` を利用し、parse tree全文ではなく syntax issue fileだけを返します。Tree-sitter runtimeやgrammarは自動installせず、保存済みsummaryを `--json-input` で同じcontractへ正規化できます。Python/nativeは共有コードを持たず、fixture testでfield semanticsを合わせます。

`path-find` の内部scan capと `repo-stats` のper-file size capは既定0=unlimitedです。明示的なperformance/safety capだけが解析完全性を制限し、その事実はJSONで区別します。

`context-budget` / `hotspot-report` もPythonとGoで実装コードを共有せず、自己説明的JSON契約とtargeted testで意味を揃えます。内部scanは既定でunlimited、agentへの返却だけをboundedにする方針です。

`context-manifest` はPython/nativeともfull repository scanを許容し、priority manifestだけをboundedに返します。`context-pack-builder` は成果物がMarkdownなのでJSON化せず、Git取得状態の意味とMarkdown contractをtestで揃えます。

`change-router` は内部test/doc indexを既定unlimitedにし、agent-visible routesだけをboundedにします。`validation-plan` はtoken-based path classificationでshort substring false positiveを避けます。両方ともPython/Goを共有コードなしで実装します。

`responsibility-candidates` もMarkdown artifactを維持した独立実装です。内部code scanは既定unlimited、table rowsだけをboundedにし、stat/walk/truncationはMarkdown commentで伝えます。

`policy-index` はdependency/generated docsを除外し、英語rule語をword boundaryで判定します。`doc-duplicate-hints` はfull document scan後にgroup/occurrenceだけをboundedにし、同じ本文をoccurrenceごとに重複出力しません。いずれもPython/nativeを独立実装し、JSON contractとtestで揃えます。

`ignore-candidates` は候補directory自体を1件返した時点でsubtreeをpruneし、同じ低価値tree配下の大量fileを重複候補として列挙しません。JSONに `matched_rule` を含め、候補理由を出力だけで判断できます。

`acceptance-extractor` / `exploration-stop-check` も独立実装です。英語termのword-boundary semantics、日本語term、truncation、missing/read errorをtestで合わせます。

## Python-only / not yet native

現時点でCommon generic toolのうち、意図的にPython fallbackを残している主なものは次です。

### Common medium
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

Common generic toolsは、低品質なparser重複を避ける `structural-search` を除き、主要なportable候補をかなりnative化できました。次はcoverage率ではなく、project-specific / language-specific analysisのmaintenance costと利用頻度を見て判断します。

`structural-search` はexternal `ast-grep` reuseを優先するため、native coverageのためだけに別parserを作りません。

Python側へgenericな新規toolを追加した場合、Go側に同等機能を実装できるなら積極的に追加します。ただし共有コード化はせず、入出力契約とtestで対応を保ちます。

原則は native coverage 100% を目的化せず、**インストール不要にする効果が高い機能を優先して native 化する**ことです。
