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

## Current Task Context
現在の作業を短くまとめた Context Pack / Issue summary / handoff がある場合は、その場所を優先入口として指定する。

- Context file:
- Issue / Task:

この入口がある場合、全 Issue や全ドキュメントを先に走査しない。

## Task Routing
Issue ラベル、タスク種別、対象モジュールなどから読む資料を限定できる場合に使う。

例:
- `spec:architecture` -> `docs/architecture.md`
- `spec:runtime` -> `docs/runtime.md`
- `spec:data` -> `docs/data-format.md`

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

## Current Work
- Task:
- Related files:
- Related docs:

## Important Constraints
今回の判断に必要な重要制約だけを書く。詳細規約は別文書へ置く。

## Validation
作業完了前に実行すべき標準検証がある場合だけ書く。

- Build:
- Tests:
- Other checks:

## Context Priority
- P0: このファイル、現在タスク、必須制約
- P1: 現在の変更対象
- P2: 直接依存するコード・設計
- P3: 参考資料
- P4: 履歴・補助情報

## Working Rules
- リポジトリ全体を無条件に読まない。
- Current Task Context がある場合は最初に読む。
- タスクのメタデータから必要資料を絞れる場合は Task Routing を使う。
- 変更確認では、まず changed files、diff stat、commit summary、validation result を見る。
- full diff は実装・レビュー・問題調査に必要な場合だけ読む。
- 必要な周辺情報だけ追加取得する。
- 要約だけで判断できない場合は原典を確認する。
- 正確性をコンテキスト削減率より優先する。

## Source of Truth
- Architecture:
- Specification:
- Coding rules:
- Issues:
