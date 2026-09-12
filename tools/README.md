# Tools

AI に渡す情報量を減らすための前処理ツール群です。

## 最初に使うもの

```text
tool-selector
  -> repo規模 / 言語 / project type を浅く判定
  -> recommended / conditional tools を出す
  -> 必要なものだけ実行
```

`tools/common/small/tool-selector/script/tool_selector.py` を導入判断の入口にします。

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

- `small`: symbols / shallow profile。小規模 repo でも低コスト
- `medium`: direct dependencies / project map / task routing
- `large`: bounded graph / structure index / hotspot analysis

スクリプト本体は `tools/<category>/<size>/<tool>/script/` に置きます。

## Common

| Size | Tool | Purpose |
|---|---|---|
| Small | `tool-selector` | repoを浅く分析し導入ツールを推薦 |
| Small | `repo-profile` | repo規模・主要言語・主要ディレクトリ |
| Small | `project-type-profile` | game / gui / compiler / data-tool 等を推定 |
| Small | `external-tool-probe` | rg / fd / ctags / ast-grep 等の利用可否を確認 |
| Small | `doc-index` | Markdown見出しをcompact index化 |
| Small | `file-role-map` | source / tests / docs / generated / asset 等へ分類 |
| Medium | `compact-diff` | changed files / shortstat / bounded diff |
| Medium | `change-router` | changed fileからmatching tests/docs候補を出す |
| Medium | `validation-plan` | 変更種別からsmallest sufficient evidenceを提案 |
| Medium | `context-pack-builder` | git stateから小さいContext Pack骨組みを生成 |
| Medium | `ignore-candidates` | 通常コンテキストから外せそうなpath候補を列挙 |
| Large | `context-manifest` | AIが読む候補を優先度付きmanifest化 |
| Large | `hotspot-report` | 大きいファイル・深いpathを候補化 |
| Large | `target-slice` | 検索hit周辺だけbounded excerptとして取得 |

## Language-specific

| Language | Small | Medium | Large |
|---|---|---|---|
| Python | `python-symbols` | `python-import-map` | `python-module-graph` |
| CSharp | `csharp-symbols` | `csharp-project-map` | `csharp-project-graph` |
| Go | `go-symbols` | `go-import-map` | `go-package-graph` |
| C | `c-symbols` | `c-include-map` | `c-include-graph` |
| C++ | `cpp-symbols` | `cpp-include-map` | `cpp-include-graph` |
| GDScript | `gdscript-symbols` | `gdscript-dependency-map` | `godot-scene-graph` |

## Project type profiles

`tools/profiles/README.md` にタイプ別推奨をまとめます。

代表例:

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
tool-selector
  -> Small / Medium / Large
  -> project characteristics
  -> major language
  -> recommended tools

external-tool-probe
  -> 既存の高品質toolがあれば優先

Small tools
  -> insufficientなら Medium
  -> 巨大repoだけ Large
```

最初から Large tools を使いません。

## 外部ツール

既存ツールで代替した方が強い領域は再実装しません。

代表例は `docs/external-tools.md` を参照してください。

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
- full source を再出力しない。
- 大規模 repo では bounded / truncated output を明示する。
- 解析結果は索引であり、判断に必要なら原典へ戻る。
- optional dependency を増やしすぎず、可能な限り標準ライブラリで動かす。
- 正規表現ベースの解析は完全な parser の代替ではない。
- 高品質な外部toolが既にある場合は、軽量fallbackを維持しつつ外部toolを優先してよい。
- toolの導入・維持コストが削減効果を上回る場合は導入しない。
