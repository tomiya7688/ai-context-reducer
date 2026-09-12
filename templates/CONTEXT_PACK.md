# Context Pack

> 作業ごとに必要な情報だけをまとめる一時的な入力パッケージ。
> 固定の巨大文書にはしない。必要に応じて原典から再構築する。

## Task
- Goal:
- Expected result:
- Issue / Task:
- Priority:
- Labels / Type:

## Compact Summary
Issue や依頼文をそのまま大量転載せず、今回の作業に必要な要点だけを短くまとめる。

## Project Context
- Project:
- Relevant area:
- Current state:

## Routed References
タスクのラベル・種別・対象モジュールなどから選ばれた資料だけを列挙する。

- 

## Changes / Working Set
- Changed files:
- Target files:
- Direct dependencies:

## Required Constraints
今回の作業で必ず守る制約だけを記載する。

- 

## Relevant Architecture
今回必要な構造だけを短く記載する。

- 

## Validation
- Build:
- Tests:
- Other checks:

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

## Optional Extensions
- performance notes
- runtime environment
- generated summary
- dependency notes
- handoff notes
- project-specific metadata

## Rules
- リポジトリ全体、全 Issue、全 docs を無条件に含めない。
- タスクのメタデータから必要資料をルーティングできる場合はそれを優先する。
- Issue 本文など長い入力は、原典への参照を残した上で compact summary にする。
- 要約だけで判断できない場合は原典を参照する。
- 古い Context Pack を原典として扱わない。
- 作業終了後に長期保存すべき内容は正式な設計文書・Issue・コードへ反映する。
- このテンプレートは拡張可能とし、標準項目を壊さない範囲でプロジェクト固有項目を追加してよい。
