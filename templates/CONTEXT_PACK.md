# Context Pack

> 現在タスクに必要な情報だけをまとめる一時パケット。
> 原典ではなく索引。不要な Optional 項目は削除する。

## Task
- Goal:
- Required:
- Acceptance:
- Task / Issue:
- Priority:

## Out of Scope
今回やらないことだけ必要に応じて書く。

- 

## Working Set
- Target files:
- Changed files / symbols:
- Matching tests:
- Direct dependencies:

## Required Constraints
- 

## Routed References
最初に読むものだけ。

- Read first:
- Read only if needed:

## Validation
変更内容に必要な evidence だけ残す。

- Targeted tests:
- Build / smoke:
- Runtime / visual evidence:
- Policy checks:
- Artifact validation:
- Evidence coverage / count:
- Unverified areas:

`0 tests`、空走査、対象外だけの検査は成功根拠にしない。
成功時は結果だけ残し、失敗時だけ必要なログを追加する。

## Change Summary
- Changed files:
- Diff stat / shortstat:
- Validation result:

full diff は実装・レビュー・問題調査に必要な場合だけ読む。

## Exploration Status
- Goal understood: yes / no
- Required known: yes / no
- Acceptance known: yes / no
- Working set identified: yes / no
- Out of scope known: yes / no

十分なら探索を止める。不明点が実装・検証中に発生した場合だけ追加探索する。

---

# Optional Extensions

該当する場合だけ追加する。

## Project / Current State
- State summary reference:

## Remote Delta
- Ahead / behind:
- Relevant remote commits:
- Relevant changed files:
- Diff stat:
- Bounded diff excerpt:

## Policy Context
- Required rules:
- Recommended rules:
- Advisory / review targets:
- Checker result:

### Active Exception
- Rule:
- Reason:
- Scope:
- Mitigation:
- Removal condition:
- Source of truth:

## Relevant Architecture
- 

## Special Validation
- Headless validation:
- Disposable workspace:
- Deterministic seed / input:
- RNG / clock / environment seam:
- Structured evaluation:
- Visual confirmation:
- Generated / distribution artifact:
- Artifact smoke:
- Performance measurement:

## Source Excerpts
原典全文が不要な場合だけ最小抜粋を置く。

## Packet Split
長くなる場合は1ファイルに詰め込まず分割してよい。

```text
task.md
files.txt
symbols.txt
constraints.md
diff.patch
```

## Context Priority
- P0: task / required constraints
- P1: target source / tests
- P2: direct dependencies
- P3: references
- P4: history / auxiliary

## Rules
- Search first, read second。
- repo全体、全Issues、全docsを無条件に含めない。
- deferred / out-of-scope へ探索を広げない。
- remote変更は compact delta を先に見る。
- 規約は現在タスクに適用されるものだけ入れる。
- diff / logs は必要なら bounded にする。
- generated artifacts は必要な場合だけ含める。
- unrelated refactor を混ぜない。
- validation は smallest sufficient evidence を選ぶ。
- UI / visual correctness をテスト結果だけで推測しない。
- 古い Context Pack を source of truth にしない。
