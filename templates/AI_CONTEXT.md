# AI Context

> AIが最初に読む小さい索引。詳細仕様をここへ複製しない。
> 該当しない Optional 項目は削除してよい。

## Project
- Name:
- Purpose:
- Main language / runtime:

## Source of Truth
- Architecture:
- Specification:
- Coding rules:
- Issues / tasks:
- Source / tests:

## Read First
現在の作業で最初に読む入口だけを書く。

- Current task / issue:
- Current state summary:
- Primary source area:
- Matching tests:

## Read When Needed
必要時だけ読む docs / source / generated information を列挙する。

- 

## Ignore Normally
- build outputs / cache
- generated files
- large logs / datasets
- runtime saves / backups
- unrelated issues / docs / history

## Current Task Rules
- Goal / Required / Acceptance が十分なら追加探索を止める。
- Search first, read second。
- target source -> matching tests -> detailed docs の順を優先する。
- unrelated refactor を混ぜない。
- 要約だけで判断できない場合は原典へ戻る。

## Important Constraints
今回の判断で破ってはいけない invariant / compatibility / safety 条件だけを書く。

- 

## Validation
変更内容に必要なものだけ残す。

- Targeted tests:
- Build / smoke:
- Policy checks:
- Visual / runtime evidence:
- Artifact validation:
- Unverified areas:

成功ログ全文は残さず、失敗時だけ必要範囲を追加する。

## Context Priority
- P0: current task / required constraints
- P1: target source / tests
- P2: direct dependencies
- P3: reference docs
- P4: history / auxiliary information

---

# Optional Routing

以下は効果がある場合だけ残す。導入判断は `docs/adoption-priority.md` を参照する。

## Current State
READMEだけでは現在の能力・制約・未実装を把握しにくい場合。

- State summary:

## Remote Delta
複数AI・複数チャット・複数人がremoteを変更する場合。

- Base branch:
- Compact remote context command / tool:
- Update policy: fast-forward only / manual / other

full diffより commit summary / changed files / diff stat を先に見る。

## Task / Change Routing
Issue種別や変更カテゴリから source / tests / docs を直接選べる場合。

例:

```text
save -> src/data/... -> tests/test_save... -> docs/data.md
UI   -> src/ui/...   -> tests/test_ui...   -> docs/ui.md
```

## Responsibility Map
file / module が多く、名前だけでは責務を判断しづらい場合。

- Map:

## Source Structure Index
巨大codebaseで symbol / call / dependency 探索が重い場合。

- Index / tool:
- Refresh rule:

bounded traversal を優先し、無制限に周辺コードへ広げない。

## Policy Checks
機械判定できる規約が多い場合。

- Checker:
- Exception source:

confirmed violation と warning / review candidate を分ける。

## Special Validation
該当するものだけ残す。

- Headless-first:
- Disposable workspace:
- Deterministic seed / input:
- RNG / clock / environment seam:
- Structured runtime observation:
- Visual confirmation:
- Packaged artifact smoke:

## Working Rules
- リポジトリ全体、全docs、全Issuesを無条件に読まない。
- 大きな文書は見出し・キーワード検索で対象節を絞る。
- changed files / symbols が分かる場合はそこから始める。
- generated artifacts は対象自体が作業対象の場合だけ読む。
- diff / logs は必要なら bounded にする。
- 不明点が実装・検証中に発生した場合だけ探索を再開する。
- 正確性をコンテキスト削減率より優先する。
