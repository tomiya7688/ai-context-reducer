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

各ディレクトリの役割を1行程度で説明する。

## Read First
AI が最初に読むべき資料。

- `README.md`
- `docs/architecture.md`
- `docs/coding_rules.md`

存在しないものは書かない。

## Read When Needed
必要になった場合だけ読む。

- `src/...` : 実装変更時
- `tests/...` : テスト変更・不具合調査時
- `docs/...` : 詳細仕様確認時
- `tools/...` : 開発補助ツール変更時

## Ignore Normally
通常はコンテキストへ入れない。

- build outputs
- cache
- generated files
- datasets
- logs
- unrelated historical files

必要な場合は参照してよい。

## Current Work
現在進行中の変更や重要な作業があれば短く記載する。

- Task:
- Related files:
- Related docs:

長期間残る情報はここに置かず、正式な設計資料へ移す。

## Important Constraints
このプロジェクトで破ってはいけない重要事項のみ記載する。

- architecture constraints
- performance constraints
- compatibility constraints
- coding restrictions

詳細な規約そのものは別文書へ置く。

## Context Priority
基本優先度:

- P0: このファイルと必須制約
- P1: 現在の作業対象
- P2: 直接依存するコード・設計
- P3: 参考資料
- P4: 履歴・補助情報

## Working Rules
- リポジトリ全体を無条件に読まない。
- 変更時は Git 差分を優先する。
- 必要な周辺情報だけ追加取得する。
- 要約だけで判断できない場合は原典を確認する。
- 要約を原典の代替として扱わない。
- 正確性をコンテキスト削減率より優先する。

## Source of Truth
重要情報の正式な保存場所を必要に応じて記載する。

- Architecture:
- Specification:
- Coding rules:
- Issues:
