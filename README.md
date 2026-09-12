# ai-context-reducer

AI / Codex を利用した開発で、必要以上にコンテキストを消費しないための設計方針・運用方法をまとめるリポジトリです。

このリポジトリ自体は **文書・設計を中心** とします。必要に応じて補助ツールを追加することはありますが、ツール実装そのものを主目的にはしません。

## 目的

- AI に渡す情報量を減らす
- 必要な情報や設計意図を失わない
- 毎回リポジトリ全体を読み直さなくても作業できる状態を作る
- 差分・索引・要約を使って必要な情報へ素早く到達できるようにする
- 各プロジェクトで乱立したコンテキスト削減手法を共通方針として整理する
- この方針自体を導入するためのコンテキスト消費も小さく保つ
- 実際のプロジェクトで有効だった手法を後から共通仕様へ取り込める構造を保つ

## 基本原則

> AI に大量の情報を読ませて必要情報を探させるのではなく、必要情報を先に選別・要約してから AI へ渡す。

また、要約は原典の代替ではなく **索引** として扱います。判断に必要な場合は、必ず元のコード・文書へ戻れる構造を維持します。

もう一つ重要なのは、必要情報が揃った後も探索を続けないことです。

> Goal / Required / Acceptance と必要な非対象範囲が実装可能な粒度まで揃ったら、追加探索を止める。

## 最短導入

別プロジェクトへ導入する場合は、まずこのリポジトリの README と `templates/AI_CONTEXT.md` だけを入口として使います。

AI には次のように依頼できます。

```text
このプロジェクトに ai-context-reducer の方針を導入してください。
リポジトリ全体を無条件に読まず、README と AI_CONTEXT.md 相当の索引、現在の作業対象を優先してください。
必要なら templates/AI_CONTEXT.md を参考に、対象プロジェクト用の AI_CONTEXT.md を最小構成で作成してください。
```

詳しい導入例は [`docs/adoption-prompt.md`](docs/adoption-prompt.md) を参照してください。

## このリポジトリで扱うもの

- コンテキスト削減の基本原則
- 情報の優先度・階層化
- AI が最初に読む Context Map / Index
- Git 差分を中心とした作業フロー
- Remote Delta First による作業開始時の状態同期
- Source Structure Index によるコード全体走査の削減
- Search-first / Read-second と探索停止条件
- Explicit Deferred / Out of Scope による作業境界
- Change Routing Map による source / tests / docs の直接ルーティング
- ソースコードや設計資料の要約方針
- Context Pack の考え方
- Task Capsule と metadata-driven document routing
- Acceptance-first task packet と changed-symbol routing
- compact change summary / validation result を使った変更確認
- targeted tests と未確認領域を明示した限定的 validation
- correctness boundary を作ってから必要な最適化へ進む運用
- 再実行可能なデータ変換と dry-run
- 各プロジェクトへの導入方法
- 実運用からの手法の逆輸入・標準化
- 必要に応じた補助ツールの設計・実装

## 文書

- 基本方針: [`docs/guide.md`](docs/guide.md)
- 導入プロンプト: [`docs/adoption-prompt.md`](docs/adoption-prompt.md)
- Context Pack: [`docs/context-pack.md`](docs/context-pack.md)
- Task Routing / Compact Workflow: [`docs/task-routing.md`](docs/task-routing.md)
- Exploration Control / Stop Conditions: [`docs/exploration-control.md`](docs/exploration-control.md)
- Change Routing Map: [`docs/change-routing-map.md`](docs/change-routing-map.md)
- Remote Context / Remote Delta First: [`docs/remote-context.md`](docs/remote-context.md)
- Source Structure Index: [`docs/source-structure-index.md`](docs/source-structure-index.md)
- AI Context テンプレート: [`templates/AI_CONTEXT.md`](templates/AI_CONTEXT.md)
- Context Pack テンプレート: [`templates/CONTEXT_PACK.md`](templates/CONTEXT_PACK.md)

## 外部プロジェクトと実装例

Kadoka 系を含む外部リポジトリは、実運用の参考元であり、手法の具体的な **実装例 / 参考実装** として紹介できます。

標準仕様そのものは外部プロジェクトに依存させません。

- 有効な手法は抽象化して取り込む
- 外部プロジェクトを必須依存にはしない
- 特定ツールの CLI、ファイル形式、ディレクトリ構造を標準仕様にはしない
- 同じ標準を別実装でも満たせるようにする
- 実装例として外部リポジトリを紹介・参照することは許容する
- 外部側の変更を自動的に標準へ追従させず、必要な手法だけ改めて評価して取り込む

実装例:

- `kadoka_code_atlas`: Source Structure Index、共通 IR、call graph、bounded traversal
- `comfyUI_support_tools`: Search-first / Read-second、優先Issue選択、Acceptance 抽出、分割 Context Packet、bounded diff、探索停止条件
- `kadocacio`: 変更対象 → source → targeted tests の対応表、巨大仕様書の見出し検索、重要 invariant、dry-run 付き再実行可能変換、簡潔な最終報告
- `Kadoka-shougi-ai`: narrow task、明示的 deferred behavior、対象 subsystem / acceptance tests の固定、correctness tests 前の先行最適化を避ける運用

これらがなくても各標準は成立します。

## 想定用途

Bitlang、ゲーム開発、AI 関連ツールなど、規模や言語が異なるプロジェクトでも共通利用できる方式を目指します。

このリポジトリでは特定の AI 製品、プログラミング言語、外部プロジェクトだけに依存しない方針を優先します。

標準仕様は固定物ではありません。実際のプロジェクトで有効だった方法を検証し、共通利用する価値があるものは段階的に取り込みます。ただし、既存の最小構成を壊す変更よりも、任意拡張として追加する方法を優先します。
