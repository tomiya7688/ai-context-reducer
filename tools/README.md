# Tools

AI に渡す情報量を減らすための前処理ツール群です。

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
- `medium`: direct dependencies / project map
- `large`: bounded graph / structure index。全体走査の代替

スクリプト本体は `tools/<category>/<size>/<tool>/script/` に置きます。

## Common

| Size | Tool | Purpose |
|---|---|---|
| Small | `repo-profile` | repo の規模・主要言語・主要ディレクトリを判定 |
| Small | `project-type-profile` | game / gui / compiler / data-tool 等の特性を推定 |
| Medium | `compact-diff` | changed files / shortstat / bounded diff |
| Large | `context-manifest` | AI が読む候補を優先度付き manifest にする |

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

`tools/profiles/README.md` にタイプ別の推奨をまとめます。

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
repo-profile
  -> Small / Medium / Large
project-type-profile
  -> project characteristics
language-specific tools
  -> symbols / direct dependencies / bounded graph
```

AI は最初から Large tools を使わず、必要な粒度まで段階的に上げます。

## 方針

- 出力は AI へ渡しやすい短い text / JSON を優先する。
- full source を再出力しない。
- 大規模 repo では bounded / truncated output を明示する。
- 解析結果は索引であり、判断に必要なら原典へ戻る。
- optional dependency を増やしすぎず、可能な限り標準ライブラリで動かす。
- 正規表現ベースの解析は完全な parser の代替ではない。精密判断が必要なら公式 parser / compiler / source を使う。
