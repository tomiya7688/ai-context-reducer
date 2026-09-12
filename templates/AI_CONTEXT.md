# AI Context

## Project
- Name:
- Purpose:
- Main language / runtime:

## Current Goal
現在このプロジェクトで優先している目的を短く記載する。

## Architecture
主要構成だけを書く。

```text
src/
tools/
docs/
tests/
```

## Read First
AI が最初に読むべき資料だけを書く。

## Current State
現在の実装能力・主要制約・明確な未実装事項を短くまとめた文書がある場合だけ指定する。

- State summary:

詳細仕様や Issue 本文をここへ複製しない。

## Remote Context
複数の AI / チャット / 開発者が remote を変更する可能性がある場合に使う。

- Remote context command / tool:
- Base branch:
- Auto-update policy:

作業開始時は full remote diff を読む前に、commit subjects、changed files、diff stat、bounded diff excerpt などの compact remote context を優先する。

自動更新を行う場合は fast-forward のみに限定し、dirty worktree や local divergence がある場合は停止する。

## Source Structure Index
ソース構造を機械解析した索引がある場合に指定する。

- Index / atlas tool:
- Output / cache:
- Supported languages:
- Refresh rule:

利用可能な場合は、全ソースを先に読む代わりに module / class / function / call / dependency などの構造索引を使う。
対象シンボルから callers / callees / direct dependencies / matching tests の順に、必要な範囲だけ段階的に広げる。

## Current Task Context
現在の作業を短くまとめた Context Pack / Issue summary / handoff がある場合は、その場所を優先入口として指定する。

- Context file:
- Issue / Task:

この入口がある場合、全 Issue や全ドキュメントを先に走査しない。

## Exploration Stop Condition
探索を続ける条件ではなく、止める条件を明示する。

- Goal が理解できている
- Required constraints が分かっている
- Acceptance / completion condition が分かっている
- 対象 source / tests が特定できている

この条件を満たしたら、追加の資料読み込みは「実装・検証に必要な場合だけ」に切り替える。

## Task Routing
Issue ラベル、タスク種別、対象モジュールなどから読む資料を限定できる場合に使う。

例:
- `spec:architecture` -> `docs/architecture.md`
- `spec:runtime` -> `docs/runtime.md`
- `spec:data` -> `docs/data-format.md`

必要に応じて「対象 source -> matching tests -> 詳細 docs」のように読む順番も指定する。

## Change Routing Map
変更カテゴリから最初に読む実装・先に走らせるテスト・必要時だけ読む資料を直接引ける場合に使う。

例:
- `UI` -> `src/app/...` -> `tests/test_app_...` -> `docs/ui.md`
- `save` -> `src/data/...` -> `tests/test_save_...` -> `docs/data.md`

巨大な README / SPEC / 設計文書は、最初から全文を読まず見出し・キーワード検索で対象節を特定してから読む。

## Responsibility Map
file / module ごとの責務を短くまとめた canonical map がある場合に指定する。

- Responsibility map:
- Update rule:

AI はファイル名だけで責務を推測せず、利用可能ならこの map から候補を絞る。
責務説明が短い1文で表せなくなった場合は、file / class / module の責務が広がりすぎていないか確認する signal として扱う。

## Policy Checks
coding rules のうち機械判定できる部分を checker / lint へ移している場合に指定する。

- Checker command / tool:
- Exception / ignore policy:

成功時は長いログではなく `OK` 等の結果だけを保持し、問題がある場合だけ compact findings を読む。
責務分離・semantic ownership など機械判定しにくい設計規約は、無理に checker 化せず targeted review に残す。

## Information Responsibilities
同じ詳細情報を複数箇所へ重複させないため、情報源の役割を必要に応じて指定する。

- README:
- AI context / agent guide:
- Current state summary:
- Detailed docs:
- Issues / tasks:
- Source / tests:
- Generated artifacts:

## Read When Needed
必要になった場合だけ読む資料・ディレクトリを書く。

## Ignore Normally
- build outputs
- cache
- generated files
- datasets
- logs
- unrelated historical files
- unrelated issues
- unrelated docs
- runtime saves
- evaluation outputs
- backups
- reference-only datasets

生成物・実測出力・セーブ・バックアップ類は、その対象自体が作業対象の場合だけ読むことを基本とする。

## Current Work
- Task:
- Related files:
- Related docs:

## Important Constraints
今回の判断に必要な重要制約だけを書く。詳細規約は別文書へ置く。

必要に応じて、変更で破ってはいけない既知の invariant を短く列挙する。

## Validation
作業完了前に実行すべき標準検証がある場合だけ書く。

- Targeted tests:
- Build:
- Full / standard tests:
- Generated docs / consistency:
- Reproducibility conditions:
- Policy checks:
- Other checks:
- Unverified areas:

小変更では targeted tests を先に実行し、完了前に標準検証へ進む。
機械判定可能な規約は checker 結果を利用し、成功時は長い規約全文やログを保持しない。
成功時は結果だけを保持し、失敗時のみ必要なログを追加する。
未確認領域が残る場合は、全体を追加走査する代わりに明示して引き継ぐ。

## Context Priority
- P0: このファイル、現在タスク、必須制約
- P1: 現在の変更対象
- P2: 直接依存するコード・設計
- P3: 参考資料
- P4: 履歴・補助情報

## Working Rules
- リポジトリ全体を無条件に読まない。
- Search first, read second。まず検索・索引・changed files で候補を絞り、全文読み込みは必要な対象だけにする。
- Goal / Required / Acceptance が実装可能な粒度まで揃ったら探索を止める。
- roadmap / backlog / index など、実装タスクではない項目を現在作業候補から除外できる場合は先に除外する。
- remote 変更の可能性がある場合は、full diff より compact remote context を先に確認する。
- remote changed files は現在タスクに関係するものだけ優先して読む。
- Source Structure Index がある場合は、全ソース走査より先に利用する。
- 構造情報は必要箇所への索引として扱い、判断に必要なら原典へ戻る。
- 呼び出し・依存グラフは bounded traversal を優先し、無制限に周辺コードを広げない。
- Current Task Context がある場合は最初に読む。
- Current State は現在の能力と制約の把握に使い、詳細仕様の代替にしない。
- タスクのメタデータから必要資料を絞れる場合は Task Routing を使う。
- Change Routing Map がある場合は対象 source と matching tests を先に特定する。
- Responsibility Map がある場合は file / module の責務確認と候補絞り込みに使う。
- 機械判定可能な coding rules は可能なら checker / lint の compact result を優先し、規約全文を常時コンテキストへ入れない。
- 大きな文書は全文読み込みより対象見出し検索を先に使う。
- 変更確認では、まず changed files、diff stat、commit summary、validation result を見る。
- full diff は実装・レビュー・問題調査に必要な場合だけ読む。
- generated artifacts は必要な場合だけ読む。
- 大量データ変換は再実行可能な手段と dry-run を優先する。
- 必要な周辺情報だけ追加取得する。
- 要約だけで判断できない場合は原典を確認する。
- 状態や前提が曖昧な場合は推測で補完せず、追加の原典確認へ進む。
- unrelated refactor を現在タスクへ混ぜない。
- 新規・変更コードへ規約を適用するために、無関係な legacy code を一括改修しない。
- 正確性をコンテキスト削減率より優先する。

## Source of Truth
- Architecture:
- Specification:
- Coding rules:
- Issues:
