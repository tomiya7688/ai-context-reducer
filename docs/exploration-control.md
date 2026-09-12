# Exploration Control / Stop Conditions

この文書は、AI が「念のため」でリポジトリ全体へ探索を広げ続けることを防ぐための標準方針を定義します。

この考え方は複数の実運用プロジェクトを参考にしています。外部プロジェクトは実装例であり、標準仕様そのものは依存しません。

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
- Deferred scope: 今回やらない範囲が必要に応じて明確になっている

これらが十分なら追加探索を止めます。

新しい不明点が実装・検証中に発生した場合だけ、対応する原典を追加で取得します。

## 3. Explicit deferred scope

タスクには「今回やること」だけでなく「今回はやらないこと」を短く持てます。

例:

```text
Goal: legal move generation を追加する
Deferred: repetition / search / optimization
```

明示された deferred behavior / out-of-scope module は、現在タスクの完了に必要でない限り探索・変更対象へ広げません。

これは将来作業を否定するものではなく、現在の Context Pack の境界を固定するための情報です。将来作業は Issue や正式な計画へ参照を残します。

## 4. Non-task filtering

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

## 5. Acceptance-first task packet

Task Capsule / Context Pack では、Issue 本文全体より次の情報を優先します。

```text
Task ID
Priority
Title
Goal
Required constraints
Acceptance / completion conditions
Deferred / out of scope
Relevant files / symbols
Source of truth reference
```

Acceptance と deferred scope を早い段階で持つことで、探索の終了条件・検証条件・非対象範囲を同時に決められます。

## 6. Reproducible split packet

Context Pack は必ず1ファイルである必要はありません。

長くなる場合は、再生成可能な小さい構成要素へ分離できます。

```text
context/<task-id>/
├─ task.md
├─ files.txt
├─ symbols.txt
├─ constraints.md
└─ diff.patch
```

必要な部分だけ読め、機械生成情報を個別に更新できます。このディレクトリ名やファイル名は標準仕様ではありません。

## 7. Changed symbols

changed files だけでなく、変更対象ファイル内の class / function / method などの symbol 一覧を機械抽出できる場合は利用します。

これにより、1ファイルが大きい場合でも working set を先に絞れます。

## 8. Bounded diff

Task Packet に diff を含める場合、無制限に全文を複製しません。

- changed files / diff stat を先に確認する
- diff excerpt に必要なら上限を設定する
- truncated であることを明示する
- 判断に必要なら原典の full diff へ戻る

## 9. Unverified areas

安全性のために全リポジトリを読むのではなく、確認できていない範囲を明示します。

```text
Validation
- targeted tests: passed
- full integration test: not run
- platform-specific path: unverified
```

## 10. Scope containment

現在タスクと無関係な refactor は混ぜません。

また、性能最適化は対象挙動の正しさを固定するテスト・契約がない段階で先回りして行わないことを推奨します。まず correctness boundary を作り、その後に必要なら最適化タスクとして扱います。

これは変更量、レビュー量、必要コンテキストを抑え、最適化によって未確定仕様まで探索対象になることを防ぎます。

## 11. 実装例

- `comfyUI_support_tools`: Search-first / Read-second、Acceptance 抽出、bounded packet、探索停止条件
- `Kadoka-shougi-ai`: narrow task、明示的 deferred behavior、対象 subsystem / tests の固定、correctness tests 前の先行最適化を避ける運用

これらは参考例であり、同じ標準を別の Issue tracker、別言語、別ツールで実装して構いません。

## 12. 標準推奨

- Search first, read second
- Goal / Required / Acceptance を探索停止条件として使う
- 必要に応じて Deferred / Out of Scope を明示する
- 非実装タスクを次タスク候補から先に除外する
- Acceptance を Context Pack の早い段階に含める
- changed symbols を取得できる場合は working set 絞り込みに使う
- diff やログには必要に応じて上限を設ける
- 未確認領域は明示する
- unrelated refactor を現在タスクへ混ぜない
- correctness boundary がない段階で不要な性能最適化へ範囲を広げない
