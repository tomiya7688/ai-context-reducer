# Exploration Control / Stop Conditions

この文書は、AI が「念のため」でリポジトリ全体へ探索を広げ続けることを防ぐための標準方針を定義します。

この考え方は `comfyUI_support_tools` の運用を参考にしています。外部プロジェクトは実装例であり、標準仕様そのものは依存しません。

## 1. Search first, read second

最初から全文を読むのではなく、検索・索引・changed files・Issue metadata で候補を絞ってから必要な原典だけを読みます。

```text
Search / metadata / index
    ↓
Candidate files / symbols
    ↓
Target source + matching tests
    ↓
Detailed docs only if needed
```

検索結果や構造索引は原典の代替ではなく、読む対象を絞るための入口です。

## 2. Exploration Stop Condition

コンテキスト削減では「何を読むか」だけでなく「いつ読むのを止めるか」を決めます。

実装へ進むための最低条件として、次を推奨します。

- Goal: 何を達成するか理解している
- Required: 必須制約・守るべき条件が分かっている
- Acceptance: 完了条件・検証条件が分かっている
- Working set: 対象 source / tests / docs が特定できている

これらが十分なら追加探索を止めます。

新しい不明点が実装・検証中に発生した場合だけ、対応する原典を追加で取得します。

## 3. Non-task filtering

Issue tracker には、実装作業以外の項目も混ざります。

例:

- roadmap
- backlog
- index / 索引
- policy
- meta issue
- umbrella issue

次タスクを機械選択する場合、これらを実装タスク候補から先に除外できる仕組みを推奨します。

AI に全 Issue を読ませて「どれが実装タスクか」を毎回判断させる必要はありません。

## 4. Acceptance-first task packet

Task Capsule / Context Pack では、Issue 本文全体より次の情報を優先します。

```text
Task ID
Priority
Title
Goal
Required constraints
Acceptance / completion conditions
Relevant files / symbols
Source of truth reference
```

特に Acceptance を早い段階で持つことで、探索の終了条件と検証条件を同時に決められます。

## 5. Reproducible split packet

Context Pack は必ず1ファイルである必要はありません。

長くなる場合は、再生成可能な小さい構成要素へ分離できます。

例:

```text
context/<task-id>/
├─ task.md
├─ files.txt
├─ symbols.txt
├─ constraints.md
└─ diff.patch
```

利点:

- 必要な部分だけ読める
- diff だけ上限を設定できる
- symbol list だけ再利用できる
- Task 本文と機械生成情報を分離できる
- パケット全体を原典から再構築しやすい

このディレクトリ名やファイル名は標準仕様ではありません。重要なのは、Context Pack を必要に応じて分割可能にすることです。

## 6. Changed symbols

changed files だけでなく、変更対象ファイル内の class / function / method などの symbol 一覧を機械抽出できる場合は利用します。

これにより、1ファイルが大きい場合でも「どのシンボルが今回の working set か」を先に絞れます。

Source Structure Index がある場合はそこから取得しても構いません。

## 7. Bounded diff

Task Packet に diff を含める場合、無制限に全文を複製しません。

- changed files を先に確認する
- diff stat を先に確認する
- diff excerpt に上限を設定できるようにする
- 切り捨てた場合は truncated であることを明示する
- 判断に必要なら原典の full diff へ戻る

## 8. Unverified areas

安全性のために全リポジトリを読むのではなく、確認できていない範囲を明示する方法を推奨します。

例:

```text
Validation
- targeted tests: passed
- full integration test: not run
- Windows-only path: unverified
```

「未確認」を正確に残すことで、コンテキスト節約のための推測や過剰な追加調査を避けられます。

## 9. Scope containment

現在タスクと無関係な refactor は混ぜません。

新しい規約を導入する場合も、新規・変更コードへ適用するために unrelated legacy code を一括修正しないことを推奨します。

これは変更量、レビュー量、必要コンテキストのすべてを増やすためです。

## 10. 実装例

`comfyUI_support_tools` には、次の考え方を実装した例があります。

- 優先度から1件の実装 Issue を選択
- roadmap / backlog / index 系 Issue の除外
- Acceptance 条件だけを compact packet に抽出
- task / files / symbols / constraints / bounded diff の分離
- Search-first, Read-second
- Goal / Required / Acceptance が揃ったら探索停止

この実装は参考例であり、同じ標準を別の Issue tracker、別言語、別ツールで実装して構いません。

## 11. 標準推奨

- Search first, read second
- Goal / Required / Acceptance を探索停止条件として使う
- 非実装タスクを次タスク候補から先に除外する
- Acceptance を Context Pack の早い段階に含める
- changed symbols を取得できる場合は working set 絞り込みに使う
- diff やログには必要に応じて上限を設ける
- 未確認領域は明示する
- unrelated refactor を現在タスクへ混ぜない
