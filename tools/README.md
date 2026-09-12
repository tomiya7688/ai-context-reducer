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
│  ├─ small/
│  ├─ medium/
│  └─ large/
└─ csharp/
   ├─ small/
   ├─ medium/
   └─ large/
```

- `common`: 言語非依存
- `python`: Python 固有の構造解析
- `csharp`: C# 固有の構造解析
- `small`: 小規模 repo でも導入コストが低い
- `medium`: 複数 module / docs / tests がある repo 向け
- `large`: 大規模 repo で全体走査を避けるための索引生成向け

スクリプト本体は `tools/<category>/<size>/<tool>/script/` に置きます。

## 現在のツール

| Category | Size | Tool | Purpose |
|---|---|---|---|
| Common | Small | `repo-profile` | repo の規模・言語・主要ディレクトリを compact に判定 |
| Common | Medium | `compact-diff` | changed files / shortstat / bounded diff を生成 |
| Common | Large | `context-manifest` | AI が読む候補を優先度付き manifest にする |
| Python | Small | `python-symbols` | AST から class / function を抽出 |
| Python | Medium | `python-import-map` | import 関係を compact に抽出 |
| CSharp | Small | `csharp-symbols` | namespace / class / method 候補を抽出 |
| CSharp | Medium | `csharp-project-map` | csproj と source の対応を compact に一覧化 |

## 方針

- 出力は AI へ貼りやすい短い text / JSON を優先する。
- full source を再出力しない。
- 大規模 repo では bounded output を優先する。
- 解析結果は索引であり、必要なら原典へ戻る。
- optional dependency を増やしすぎず、可能な限り標準ライブラリで動かす。
