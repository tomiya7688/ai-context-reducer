# Tools

AI に渡す情報量を減らすための前処理ツール群です。

## 推奨入口

通常はまず次を使います。

```text
analyze-and-recommend
  -> repo規模 / 言語 / project type / docs / tests / Git状態を浅く判定
  -> 推奨手法と推奨toolを出す
  -> 必要なものだけ実行
```

入口:

`tools/common/small/analyze-and-recommend/script/analyze_and_recommend.py`

`tool-selector` はより低レベルな導入候補一覧が欲しい場合に使います。

外部ツールが使える環境では `external-tool-probe` で確認し、自前の簡易解析より既存の高品質ツールを優先できます。

## 分類

```text
tools/
├─ common/
│  ├─ small/
│  ├─ medium/
│  └─ large/
├─ python/
├─ csharp/
├─ go/
├─ c/
├─ cpp/
├─ gdscript/
└─ profiles/
```

各言語カテゴリは原則 `small / medium / large` に分けます。

- `small`: shallow profile / symbols。導入コストが低い
- `medium`: direct dependencies / routing / task context
- `large`: bounded graph / structure index / context cost analysis

スクリプト本体は `tools/<category>/<size>/<tool>/script/` に置きます。

## Common

| Size | Tool | Purpose / supporting method |
|---|---|---|
| Small | `analyze-and-recommend` | repoを浅く分析し、導入すべき手法とtoolをまとめて推薦 |
| Small | `tool-selector` | 規模・言語・project typeからtool候補を選択 |
| Small | `repo-profile` | repo規模・主要言語・主要ディレクトリ |
| Small | `project-type-profile` | game / gui / compiler / data-tool 等を推定 |
| Small | `external-tool-probe` | rg / fd / ctags / ast-grep 等の利用可否を確認 |
| Small | `doc-index` | Markdown見出しをcompact index化。Search-first / heading-first |
| Small | `file-role-map` | source / tests / docs / generated / asset 等へ分類 |
| Small | `source-of-truth-candidates` | 正式資料候補をファイル名から列挙。権威性は推測しない |
| Medium | `compact-diff` | changed files / shortstat / bounded diff |
| Medium | `remote-delta` | Remote Delta First用のahead/behind/files/commit要約 |
| Medium | `change-router` | changed fileからmatching tests/docs候補を出す |
| Medium | `acceptance-extractor` | Goal / Required / Acceptance / Deferred をMarkdownから抽出 |
| Medium | `exploration-stop-check` | broad explorationを止められる情報が揃ったか確認 |
| Medium | `validation-plan` | 変更種別からsmallest sufficient evidenceを提案 |
| Medium | `context-pack-builder` | Git stateから小さいContext Pack骨組みを生成 |
| Medium | `policy-index` | 長い規約からmust/should/必須/推奨候補だけ索引化 |
| Medium | `responsibility-candidates` | Responsibility Mapの空テンプレート候補を生成 |
| Medium | `doc-duplicate-hints` | 複数文書に重複した長文候補を検出 |
| Medium | `compact-log` | error/warning/failure行 + bounded tailだけ残す |
| Medium | `ignore-candidates` | 通常コンテキストから外せそうなpath候補を列挙 |
| Large | `context-manifest` | AIが読む候補を優先度付きmanifest化 |
| Large | `hotspot-report` | 大きいファイル・深いpathを候補化 |
| Large | `target-slice` | 検索hit周辺だけbounded excerptとして取得 |
| Large | `context-budget` | 全文読みした場合の概算token量と巨大候補を表示 |

## Language-specific

| Language | Small | Medium | Large |
|---|---|---|---|
| Python | `python-symbols` | `python-import-map` | `python-module-graph` |
| CSharp | `csharp-symbols` | `csharp-project-map` | `csharp-project-graph` |
| Go | `go-symbols` | `go-import-map` | `go-package-graph` |
| C | `c-symbols` | `c-include-map` | `c-include-graph` |
| C++ | `cpp-symbols` | `cpp-include-map` | `cpp-include-graph` |
| GDScript | `gdscript-symbols` | `gdscript-dependency-map` | `godot-scene-graph` |

## このリポジトリの手法との対応

```text
Search-first / Read-second
  -> doc-index / target-slice / external rg/fd

Exploration Stop Condition
  -> acceptance-extractor / exploration-stop-check

Remote Delta First
  -> remote-delta / compact-diff

Responsibility Map
  -> responsibility-candidates

Change Routing Map
  -> change-router

Policy Routing
  -> policy-index / external Semgrep等

Validation Routing
  -> validation-plan / compact-log

Context Pack
  -> context-pack-builder

Source Structure Index
  -> language-specific symbols/dependency/graph tools

Context Priority / avoid full-repo reads
  -> context-manifest / context-budget / hotspot-report

Information responsibility / avoid duplicate docs
  -> source-of-truth-candidates / doc-duplicate-hints
```

## Project type profiles

`tools/profiles/README.md` にタイプ別推奨をまとめます。

- Game: scene/resource map、deterministic validation、visual confirmation
- GUI: headless-first + visual confirmation
- Compiler / Language: symbol/index + dependency graph + regression tests
- Data Tool: dry-run + disposable workspace + generated-data validation
- Packaged App: artifact-boundary validation
- Simulation / AI: deterministic seam + structured observation
- Rule-heavy: Policy Routing + Responsibility Map + targeted checker

複数タイプに該当して構いません。

## 推奨選択フロー

```text
analyze-and-recommend
  -> project profile
  -> recommended techniques
  -> recommended tools

external-tool-probe
  -> 高品質な既存toolがあれば優先

Small tools
  -> current taskに必要なら Medium
  -> 巨大repo / 高コスト領域だけ Large
```

最初から全toolやLarge解析を使いません。

## 外部ツール

既存ツールで代替した方が強い領域は再実装しません。詳細は `docs/external-tools.md` を参照してください。

候補:

- ripgrep
- fd
- ast-grep
- Universal Ctags
- Tree-sitter
- scc
- git-sizer
- Semgrep

## 方針

- 出力は AI へ渡しやすい短い text / JSON を優先する。
- full source / full logs / full docs を再出力しない。
- 大規模 repo では bounded / truncated output を明示する。
- 解析結果は索引であり、判断に必要なら原典へ戻る。
- optional dependency を増やしすぎず、可能な限り標準ライブラリで動かす。
- 正規表現ベースの解析は完全な parser の代替ではない。
- 高品質な外部toolが既にある場合は、軽量fallbackを維持しつつ外部toolを優先してよい。
- toolの導入・維持コストが削減効果を上回る場合は導入しない。
