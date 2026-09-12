# Context Pack

> 作業ごとに必要な情報だけをまとめる一時的な入力パッケージ。
> 固定の巨大文書にはしない。必要に応じて原典から再構築する。

## Task
- Goal:
- Required:
- Acceptance / completion condition:
- Issue / Task:
- Priority:
- Labels / Type:

## Compact Summary
Issue や依頼文をそのまま大量転載せず、今回の作業に必要な要点だけを短くまとめる。

## Project Context
- Project:
- Relevant area:
- Current state summary:

現在の実装能力・制約を短くまとめた状態文書がある場合は参照だけを置く。詳細仕様を複製しない。

## Remote Delta
remote 側に別の AI / チャット / 開発者による変更があり得る場合だけ使う。

- Local / remote state:
- Ahead / behind:
- Remote commit summary:
- Relevant changed files:
- Diff stat:
- Bounded diff excerpt:

full remote diff は必要な場合だけ読む。自動更新する場合は fast-forward のみに限定し、dirty / diverged 状態では停止する。

## Routed References
タスクのラベル・種別・対象モジュールなどから選ばれた資料だけを列挙する。

- Read first:
- Read only if needed:

必要に応じて `target source -> matching tests -> detailed docs` の順で読む。

## Changes / Working Set
- Changed files:
- Changed symbols:
- Target files:
- Direct dependencies:

## Required Constraints
今回の作業で必ず守る制約だけを記載する。

- 

## Relevant Architecture
今回必要な構造だけを短く記載する。

- 

## Exploration Status
- Goal understood: yes / no
- Required constraints known: yes / no
- Acceptance known: yes / no
- Target source/tests identified: yes / no

すべて十分なら追加探索を止め、必要な実装・検証だけへ進む。

## Validation / Completion Gates
- Build:
- Tests:
- Generated docs / consistency:
- Other checks:
- Unverified areas:

成功時は結果だけを残す。失敗時のみ必要なログ範囲を追加する。
未確認領域は隠さず明示する。

## Change Summary
変更後の確認では、full diff より先に次を使う。

- Changed file names:
- Diff stat / shortstat:
- Commit summary:
- Validation result:

full diff や長いログは実装・レビュー・問題調査に必要な場合のみ追加する。

## Source Excerpts
必要な場合のみ、コード・設定・ログなどの最小限の抜粋を入れる。

## Context Priority
- P0: 必須情報
- P1: 現在の変更対象
- P2: 直接依存
- P3: 参考情報
- P4: 履歴・補助情報

## Optional Packet Split
Context Pack が長くなる場合は、1ファイルへ詰め込まず再生成可能な小ファイルへ分離してよい。

例:
```text
task.md
files.txt
symbols.txt
constraints.md
diff.patch
```

## Optional Extensions
- current capabilities / limitations
- performance notes
- runtime environment
- generated summary
- dependency notes
- handoff notes
- project-specific metadata

## Rules
- Search first, read second。検索・索引・changed files で候補を絞ってから全文を読む。
- Goal / Required / Acceptance が実装可能な粒度まで揃ったら探索を止める。
- リポジトリ全体、全 Issue、全 docs を無条件に含めない。
- roadmap / backlog / index など非実装タスクを現在タスク候補から除外できる場合は除外する。
- remote 変更確認では compact delta を先に使い、必要な changed files だけ読む。
- タスクのメタデータから必要資料をルーティングできる場合はそれを優先する。
- Issue 本文など長い入力は、原典への参照を残した上で compact summary にする。
- diff は必要なら上限を設ける。
- generated artifacts は作業対象か判断に必要な場合だけ含める。
- 情報源ごとの責務を守り、同じ詳細情報を複数文書へ再掲しない。
- 要約だけで判断できない場合は原典を参照する。
- 状態や前提が曖昧な場合は推測で埋めず、原典確認へ戻る。
- unrelated refactor を混ぜない。
- 古い Context Pack を原典として扱わない。
- 作業終了後に長期保存すべき内容は正式な設計文書・Issue・コードへ反映する。
- このテンプレートは拡張可能とし、標準項目を壊さない範囲でプロジェクト固有項目を追加してよい。
