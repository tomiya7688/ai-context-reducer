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

## Explicitly Deferred / Out of Scope
今回やらないことを必要に応じて明示する。

- Deferred behavior:
- Out-of-scope modules:
- Future work reference:

非対象範囲を探索・実装の境界として扱い、現在タスクの完了に不要なら読まない・変更しない。

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

## Policy Context
現在タスクに適用される規約だけを強さ付きで記載する。

- Required rules:
- Recommended rules:
- Advisory / review targets:
- Checker result:

### Active Exceptions
規約例外がある場合だけ記載する。

- Rule:
- Reason:
- Scope:
- Mitigation / alternative:
- Removal condition / review:
- Source of truth:

確定違反と警告候補を混同しない。規約全文は必要な場合だけ原典を読む。

## Relevant Architecture
今回必要な構造だけを短く記載する。

- 

## Exploration Status
- Goal understood: yes / no
- Required constraints known: yes / no
- Acceptance known: yes / no
- Target source/tests identified: yes / no
- Deferred scope known: yes / no

すべて十分なら追加探索を止め、必要な実装・検証だけへ進む。

## Validation / Completion Gates
- Build:
- Targeted tests:
- Evidence coverage / count:
- Deterministic runtime / smoke:
- Structured evaluation log:
- Generated / distribution artifact:
- Artifact smoke:
- Visual / interactive confirmation:
- Generated docs / data consistency:
- Performance measurement:
- Policy checks:
- Other checks:
- Unverified areas:

変更の性質に合う evidence だけを選ぶ。すべてを常時実行しない。
検証コマンドが成功しても、`0 tests`・空走査・対象外のみの検査など、実質的に対象を確認していない場合は成功根拠にしない。
source tree と最終成果物が異なる場合は、必要に応じて成果物生成後の起動・必須ファイル・初期化などを直接 smoke test する。
ランダム性や時間依存がある場合は、可能なら seed / input / timestep / frame count などを固定する。
UI・描画・レイアウトの正しさが Acceptance に含まれる場合は、テスト成功だけで断定せず visual confirmation を使う。
Policy checker は confirmed violation と warning / review candidate を分けて扱う。
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
- Goal / Required / Acceptance と非対象範囲が実装可能な粒度まで揃ったら探索を止める。
- 明示的に deferred / out of scope とされた挙動や領域へ、現在タスクに必要でない限り探索・変更を広げない。
- リポジトリ全体、全 Issue、全 docs を無条件に含めない。
- roadmap / backlog / index など非実装タスクを現在タスク候補から除外できる場合は除外する。
- remote 変更確認では compact delta を先に使い、必要な changed files だけ読む。
- タスクのメタデータから必要資料をルーティングできる場合はそれを優先する。
- Issue 本文など長い入力は、原典への参照を残した上で compact summary にする。
- 規約は Required / Recommended / Advisory を区別し、現在タスクに適用されるものだけ入れる。
- checker の confirmed violation と warning / review candidate を分離する。
- 規約例外は reason / scope / mitigation / removal condition を最小限に記録する。
- diff は必要なら上限を設ける。
- generated artifacts は作業対象か判断に必要な場合だけ含める。
- 情報源ごとの責務を守り、同じ詳細情報を複数文書へ再掲しない。
- 要約だけで判断できない場合は原典を参照する。
- 状態や前提が曖昧な場合は推測で埋めず、原典確認へ戻る。
- unrelated refactor を混ぜない。
- 性能最適化は、対象の正しさを検証するテストや契約がない段階では現在タスクへ混ぜない。
- validation は変更種別に応じて smallest sufficient evidence を選び、不要な全検証・大量ログを避ける。
- 検証結果は exit code だけでなく、対象を実際に検査した evidence か確認する。
- source と成果物が異なる場合は、必要なら生成成果物を直接検証する。
- テストで確認できない UI / visual / runtime behavior を推測で補完しない。
- 古い Context Pack を原典として扱わない。
- 作業終了後に長期保存すべき内容は正式な設計文書・Issue・コードへ反映する。
- このテンプレートは拡張可能とし、標準項目を壊さない範囲でプロジェクト固有項目を追加してよい。
