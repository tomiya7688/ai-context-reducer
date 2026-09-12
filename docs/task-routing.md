# Task Routing / Compact Workflow

この文書は、実運用で有効だったコンテキスト削減手法を汎用化したものです。

最初の実例として `Kadoka-othello-AI` の運用から取り込んでいますが、特定プロジェクト・特定AIに依存しない形で扱います。

## 1. Task Capsule

現在の Issue / Task をそのまま全量読ませるのではなく、短い作業用 Context Pack を生成します。

最低限含めるもの:

- Issue / Task ID
- title
- priority
- labels / task type
- compact summary
- relevant documents
- validation rule
- source of truth への参照

この Task Capsule を AI の現在タスク入口として扱います。

重要なのは、Task Capsule を長期的な仕様書にしないことです。必要なら Issue、設計文書、コードなど原典へ戻ります。

## 2. Priority-first task selection

複数の未完了タスクがある場合、すべてを AI に読ませて選ばせる必要はありません。

Issue tracker などに優先度が存在する場合は、機械的に次のタスクを絞り込んでから AI に渡します。

例:

```text
P0 -> P1 -> P2 -> P3 -> unlabeled
```

同一優先度の並び順はプロジェクト側で決めます。

優先度選択自体はコンテキスト外で処理できる単純作業なので、可能ならツールや既存 Issue metadata を利用します。

## 3. Metadata-driven document routing

Issue のラベル、タスク種別、対象モジュールなどを、必要な設計資料へのルートとして使います。

例:

```text
spec:architecture -> docs/architecture.md
spec:runtime      -> docs/runtime.md
spec:protocol     -> docs/protocol.md
spec:data         -> docs/data-format.md
```

AI に `docs/` 全体を読ませて関連文書を探させるのではなく、まず metadata で候補を減らします。

該当ルールがない場合のみ、直接関係する資料を追加で探します。

この mapping は `AI_CONTEXT.md`、設定ファイル、補助ツールなど、プロジェクトに適した場所へ置いて構いません。

## 4. Compact issue summary

Issue 本文や依頼文が長い場合は、作業開始時に短い summary を作ります。

summary は原典の代替ではありません。

- URL / Issue ID など原典への参照を残す
- コードブロックや装飾を無条件に複製しない
- 目的、制約、完了条件を優先する
- 判断に不足があれば原典へ戻る

長さを固定値で厳密に規定する必要はありませんが、「元の Issue をそのまま Context Pack に再掲する」状態は避けます。

## 5. Compact change inspection

通常の変更確認では full diff を最初から読ませず、まず次を確認します。

```text
changed file names
    +
diff stat / shortstat
    +
commit summary
    +
validation result
```

ここで問題が見つかった場合、または実装レビューに必要な場合だけ full diff や該当ファイルを読みます。

この方式は、PR 作成、進捗確認、AI 間の引き継ぎなど、変更内容の概要だけで十分な場面で特に有効です。

## 6. Validation before handoff / PR

変更内容の説明を大量に生成する前に、標準の build / test / lint などを実行します。

Context Pack や PR summary には長いログを残すのではなく、通常は結果だけを記載します。

例:

```text
Validation
- build: passed
- tests: passed
```

失敗時のみ必要なログ範囲を追加します。

これにより、正常系で大量ログを AI に渡すことを避けます。

## 7. State chaining

Task Capsule に Issue ID や task ID を残しておくと、後続工程で再利用できます。

例:

```text
Issue
  -> Task Capsule
  -> branch / work
  -> compact change summary
  -> PR
```

同じ識別子を使うことで、AI が毎工程で「何の作業だったか」を再探索する必要を減らせます。

ただし Task Capsule 自体を source of truth にはせず、Issue や正式文書への参照を維持します。

## 8. 標準化レベル

今回取り込む考え方は次のように扱います。

### 標準推奨

- Current Task Context を優先入口にする
- タスク metadata から必要文書を絞る
- full diff より先に compact change summary を見る
- 正常系の build/test は結果だけを保持する
- Task Capsule から原典へ戻れるようにする

### 任意実装

- Issue の自動優先度選択
- Issue 本文の自動 compact 化
- label -> document mapping の自動処理
- PR summary の自動生成
- branch / PR 作成の自動化

これらは有効ですが、GitHub、特定OS、特定AIへの依存を標準仕様にはしません。

## 9. 今後の逆輸入

他プロジェクトから手法を取り込む場合、この文書へそのまま追加するとは限りません。

まず以下を確認します。

- 複数プロジェクトで再利用できるか
- 実際にコンテキスト削減に寄与するか
- 正確性を損なわないか
- 導入コストが低いか
- 既存仕様を壊さず追加できるか

十分に汎用化できたものだけ標準推奨へ昇格させます。
