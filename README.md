# ai-context-reducer

日本語 | [English](README.en.md)

AI / Codex / Claude Code を使った開発で、AIに必要以上の情報を読ませず、必要な設計・実装情報へ正確にたどり着くための考え方と手法をまとめたリポジトリです。

中心にあるのは手法と文書です。繰り返し作業や機械的に処理できる部分をAIのコンテキスト外へ出すために、補助的なportable toolも提供します。主要なCommon機能は `acr-toolbox` 単体バイナリで利用できます。

## まず理解する3原則

コンテキスト削減の基本は次の3つです。

1. 静的解析できるものは静的解析する
2. よく使う操作をまとめる
3. 一部だけ読ませる

個別の手法やtoolは、ほとんどがこの3つのどれか、または組み合わせです。詳細は [`docs/jp/コンテキスト削減の基本.md`](docs/jp/コンテキスト削減の基本.md) を参照してください。

## 目標

> AI に大量の情報を読ませて必要情報を探させるのではなく、必要情報を先に選別・ルーティングしてから AI へ渡す。

さらに、必要情報が揃ったら探索を続けません。

> Goal / Required / Acceptance / working set が十分なら、追加探索を止める。

優先順位は次です。

```text
正確性
  > 作業対象への到達速度
  > コンテキスト削減量
  > 自動化の多さ
```

要約は原典の代替ではなく索引として扱い、必要なら source / tests / docs / diff へ戻れる状態を維持します。

## リリースとダウンロード

公開済みarchiveは [GitHub Releases](https://github.com/tomiya7688/ai-context-reducer/releases) から取得できます。

現在のv1.0.x Portable Distributionでは次の6環境向けarchiveを配布します。v1.0.1はv1.0.0と同じbundle構成・CLI / JSON contractを維持するパッチ版です。

- Windows x64 / arm64
- Linux x64 / arm64
- macOS x64 / arm64

各archiveには次を含みます。

- `acr-toolbox`
- `go-symbols`
- `go-import-map`
- `go-package-graph`
- `affected-tests`
- `README.md`
- `TOOLS_README.md`
- `LICENSE`
- `RELEASE_MANIFEST.json`

Releaseには6archive共通の `SHA256SUMS` も添付します。

配布前にGitHub Actions上で、6環境すべてについて **実際に配布するbinaryをnative buildし、そのbinaryでE2Eを実行してからarchive化し、さらにarchiveを再展開して内容を検査** します。source上のunit testだけではRelease gateを通しません。

```text
acr-toolbox version
acr-toolbox analyze <project-root>
acr-toolbox select <project-root>
```

`acr-toolbox version` はrelease version / commit / OS / architectureをJSONで返します。

v1.1.0では軽量な通常版を維持したまま、別archiveとしてGUI Hub付きFull Bundleを追加します。Full Bundleは通常版CLI contractを維持するsupersetで、利用者にGo toolchainの追加導入を要求しません。構成は [`docs/jp/Full Bundleの配布構成.md`](docs/jp/Full%20Bundleの配布構成.md)、Release手順は [`docs/jp/リリース手順.md`](docs/jp/リリース手順.md) を参照してください。

## Codex / Claude Code へ導入させる

最初に読ませる入口は基本的に次の4つだけです。

1. この `README.md`
2. [`docs/jp/コンテキスト削減の基本.md`](docs/jp/コンテキスト削減の基本.md)
3. [`docs/jp/導入優先度.md`](docs/jp/導入優先度.md)
4. [`templates/AI_CONTEXT.md`](templates/AI_CONTEXT.md)

その上で対象repoを shallow inspection し、**全部ではなく効果が高い手法だけ**導入させます。

そのまま使える依頼文は [`docs/jp/導入依頼文.md`](docs/jp/導入依頼文.md) にあります。

## 最小コア

ほぼ全プロジェクトで有効な Core は小さく保ちます。

- 小さい `AI_CONTEXT.md` または同等のAI入口
- Search first, read second
- Goal / Required / Acceptance が揃ったら探索停止
- Source of Truth の明示
- unrelated refactor を現在タスクへ混ぜない
- targeted validation
- 未確認領域を `Unverified` として明示
- logs / generated artifacts / history を通常コンテキストから除外

小規模repoではここまでで終了して構いません。

## 効果に応じて追加する

追加手法は、対象プロジェクトの特徴から選びます。

| 状況 | 優先する手法 |
|---|---|
| docs / Issues / subsystem が多い | Task Routing / Change Routing Map |
| file / module の責務が分かりにくい | Responsibility Map |
| 既存architectureに責務境界・層・正式な通信経路が明示されている | Architecture Boundary Routing |
| monorepo / multi-appで局所ルールが多い | Hierarchical Context / Scoped AI Instructions |
| Required evidenceが揃っても探索が止まりにくい | Evidence Budget / bounded evidence collection |
| 現在の能力・制約がREADMEだけでは分からない | Current State summary |
| 複数AI・複数チャット・複数人がremoteを更新 | Remote Delta First |
| 巨大codebase・call/dependency探索が重い | Source Structure Index / changed-symbol routing |
| test suiteが大きく毎回full runしている | Change / Test Impact Routing |
| GUI / game / editor | headless-first + visual confirmation when needed |
| random / time-dependent / simulation | deterministic seam / fixed input / bounded runtime |
| package / distribution がsourceと異なる | artifact-boundary validation |
| 保存・変換・exportで一時ファイルが増える | disposable validation workspace |
| coding rules が多い | Policy Routing + compact policy checks |
| license / NOTICE / header 等が反復する | Boilerplate Generation |

詳細な優先度と「こういうプロジェクト向き」は [`docs/jp/導入優先度.md`](docs/jp/導入優先度.md) を参照してください。

## 標準フロー

```text
AI_CONTEXT / existing agent guide
        ↓
shallow inspection
        ↓
project signals を分類
        ↓
current task: Goal / Required / Acceptance
        ↓
Search / Index / Routing
        ↓
必要十分なら探索停止
        ↓
target source / symbols / matching tests
        ↓
implementation
        ↓
smallest sufficient validation
        ↓
compact result + Unverified areas
```

remote競合があり得る場合は、実装前に compact remote delta を挟みます。

## 文書

日本語文書は [`docs/jp/`](docs/jp/) をSource of Truthとします。英語版は [`docs/en/`](docs/en/) に翻訳として配置し、日英対応は [`docs/DOCUMENT_MAP.json`](docs/DOCUMENT_MAP.json) で管理します。英語入口は [`README.en.md`](README.en.md) です。

導入時に全部読む必要はありません。

- **手法一覧**: [`docs/jp/手法一覧.md`](docs/jp/手法一覧.md) — 各手法を一言で確認し、必要な詳細文書へ移動する目次
- 基本原則: [`docs/jp/コンテキスト削減の基本.md`](docs/jp/コンテキスト削減の基本.md)
- 導入判断: [`docs/jp/導入優先度.md`](docs/jp/導入優先度.md)
- 導入プロンプト: [`docs/jp/導入依頼文.md`](docs/jp/導入依頼文.md)
- 基本方針: [`docs/jp/基本方針.md`](docs/jp/基本方針.md)
- 外部ツール掲載基準: [`docs/jp/外部ツール掲載基準.md`](docs/jp/外部ツール掲載基準.md)
- Release / completion gate: [`docs/jp/リリース手順.md`](docs/jp/リリース手順.md)
- AI入口テンプレート: [`templates/AI_CONTEXT.md`](templates/AI_CONTEXT.md)
- Task用テンプレート: [`templates/CONTEXT_PACK.md`](templates/CONTEXT_PACK.md)

個別手法の詳細リンクはREADMEへ列挙せず、[`docs/jp/手法一覧.md`](docs/jp/手法一覧.md) にまとめます。

## 外部プロジェクトとの関係

外部リポジトリや既存プロジェクトの実装から有効な考え方を学ぶことはありますが、AI Context Reducer の標準は特定の参考プロジェクトへ依存しません。

- 有効な手法だけ一般化して取り込む
- 外部repoを必須依存にしない
- 特定CLI・ファイル形式・ディレクトリ構成を標準化しない
- 同じ原則を別実装でも満たせるようにする

外部ツールへ具体的にリンクする場合は、原則として **無料 / 商用利用可能 / 通常利用時のクレジット明示不要 / ポータブルまたは導入容易** の4条件をすべて満たすものだけに限定します。詳細は [`docs/jp/外部ツール掲載基準.md`](docs/jp/外部ツール掲載基準.md) を参照してください。

## 導入しすぎない

このプロジェクトの方針そのものがコンテキスト肥大化を起こしてはいけません。

```text
expected repeated context saving
    > adoption + maintenance cost
```

を満たさない仕組みは追加しません。

小さいrepoには小さい仕組み、大きいrepoには必要なrouting/indexを追加する、という適応型の導入を標準とします。

## License

このリポジトリの内容は、文書・設計・テンプレート・スクリプト・ユーティリティ・ツール類を含め、すべて [MIT License](LICENSE) で提供します。

このリポジトリからリンク・参照している外部プロジェクトや外部コンテンツについては、それぞれの配布元で定められたライセンスに従ってください。
