# ai-context-reducer

AI / Codex / Claude Code を利用した開発で、必要以上にコンテキストを消費せず、必要な設計・実装情報へ正確に到達するための共通方針です。

このリポジトリ自体は **文書・設計中心** です。補助ツールは、繰り返し処理をAIのコンテキスト外へ移す価値がある場合だけ追加します。

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

## Codex / Claude Code へ導入させる

最初に読ませるのは基本的に次の3つだけです。

1. この `README.md`
2. [`docs/adoption-priority.md`](docs/adoption-priority.md)
3. [`templates/AI_CONTEXT.md`](templates/AI_CONTEXT.md)

その上で対象repoを shallow inspection し、**全部ではなく効果が高い手法だけ**導入させます。

そのまま使える依頼文は [`docs/adoption-prompt.md`](docs/adoption-prompt.md) にあります。

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

詳細な優先度と「こういうプロジェクト向き」は [`docs/adoption-priority.md`](docs/adoption-priority.md) を参照してください。

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

導入時に全部読む必要はありません。

- 導入判断: [`docs/adoption-priority.md`](docs/adoption-priority.md)
- 導入プロンプト: [`docs/adoption-prompt.md`](docs/adoption-prompt.md)
- 基本方針: [`docs/guide.md`](docs/guide.md)
- Context Pack: [`docs/context-pack.md`](docs/context-pack.md)
- Task Routing: [`docs/task-routing.md`](docs/task-routing.md)
- Exploration Control: [`docs/exploration-control.md`](docs/exploration-control.md)
- Evidence Budget: [`docs/evidence-budget.md`](docs/evidence-budget.md)
- Change Routing Map: [`docs/change-routing-map.md`](docs/change-routing-map.md)
- Hierarchical Context: [`docs/hierarchical-context.md`](docs/hierarchical-context.md)
- Validation Routing: [`docs/validation-routing.md`](docs/validation-routing.md)
- Change / Test Impact Routing: [`docs/change-impact-routing.md`](docs/change-impact-routing.md)
- Responsibility Map: [`docs/responsibility-map.md`](docs/responsibility-map.md)
- Policy Routing: [`docs/policy-routing.md`](docs/policy-routing.md)
- Remote Delta First: [`docs/remote-context.md`](docs/remote-context.md)
- Source Structure Index: [`docs/source-structure-index.md`](docs/source-structure-index.md)
- Boilerplate Generation: [`docs/boilerplate-generation.md`](docs/boilerplate-generation.md)
- 外部ツール掲載基準: [`docs/external-tool-reference-policy.md`](docs/external-tool-reference-policy.md)
- AI入口テンプレート: [`templates/AI_CONTEXT.md`](templates/AI_CONTEXT.md)
- Task用テンプレート: [`templates/CONTEXT_PACK.md`](templates/CONTEXT_PACK.md)

## 外部プロジェクトとの関係

Kadoka系を含む外部リポジトリは **実装例 / 参考実装** です。

- 有効な手法だけ一般化して取り込む
- 外部repoを必須依存にしない
- 特定CLI・ファイル形式・ディレクトリ構成を標準化しない
- 同じ原則を別実装でも満たせるようにする

外部ツールへ具体的にリンクする場合は、原則として **無料 / 商用利用可能 / 通常利用時のクレジット明示不要 / ポータブルまたは導入容易** の4条件をすべて満たすものだけに限定します。詳細は [`docs/external-tool-reference-policy.md`](docs/external-tool-reference-policy.md) を参照してください。

主な参考元:

- `AI_game_player`: Current State、情報源の責務分離、巨大repo運用
- `comfyUI_support_tools`: Search-first、探索停止、Acceptance-first、split packet
- `kadoka_code_atlas`: Source Structure Index、bounded graph traversal
- `kadocacio`: source / tests / docs の直接ルーティング
- `Bitlang`: Responsibility Map、compact policy checks
- `obake-no-sumika`: Validation Routing、structured runtime evidence
- `upd-commander-base-design`: Policy Routing、rule strength、exception record
- `kadoka_tetris_ai`: evidence validity、artifact smoke
- `dot_editor`: headless-first、disposable validation workspace
- `joke_programs`: RNG / clock 等の deterministic seam
- `Obake_Lisense`: canonical template + variables の定型文生成

これらがなくても標準は成立します。

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
