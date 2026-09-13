# Tools AI Context

`tools/` 自体にも AI Context Reducer の原則を適用します。

## Goal

ツールを追加・修正するときに `tools/` 全体を毎回読まず、対象toolと直接依存だけで作業を完結できる構造を維持する。

## Read routing

最初に読む範囲は原則として次だけです。

1. `tools/README.md`
2. この `tools/AI_CONTEXT.md`
3. 対象言語/subtreeのlocal guideがあればそれ
4. 対象toolのREADME / source / tests / build or run script

別言語・別category・別toolは、依存・契約・互換性確認が必要になった場合だけ追加で読む。

## Stop condition

次が揃ったら探索を止める。

- Goal が明確
- 対象toolの入出力契約が分かる
- 直接変更対象が分かる
- 必要なtest / build / smoke validationが分かる
- 既存toolとの重複有無を確認した

「念のため」で `tools/` 全体、全言語版、全READMEを読まない。

## Source of Truth

優先順位:

```text
対象toolのsource + tests
  > 対象tool README / local guide
  > tools/README.md の共通方針
  > generated output / dist artifacts
```

生成済みbinary、`dist/`、一時出力はSource of Truthにしない。

## Tool implementation rules

- full source / full log / full tree を既定出力にしない
- bounded / compact / summary-firstを既定にする
- truncationした場合は明示する
- JSON等のmachine-readable outputを必要に応じて持つ
- failure時も巨大ログをそのまま再出力せず、原因に必要な範囲を優先する
- index / analysis result は原典の代替にしない
- external toolが無くても可能な範囲でportable fallbackを保つ
- runtime / SDK / packageを勝手にinstallしない
- 小さいrepoへ高コスト解析を持ち込まない

## Python / Go

Python版とGo版は独立実装とする。

- Python: build不要。stdlib中心。必要なら `run.bat` / `run.sh`
- Go: stdlib中心。`build.bat` / `build.sh` からtest + buildを一発実行
- Python generic toolに対しGo版が合理的に実装できる場合は積極的に対応する
- 両版は共有コードではなく、入出力契約とfixture/testで整合を取る

言語固有差があるtoolは、機械的に同じ実装へ揃えない。

## Validation routing

変更内容に応じて最小十分な検証を選ぶ。

```text
README/docs only -> link/path/example確認
Python tool      -> 対象scriptのsyntax/smoke + fixtureがあればtargeted test
Go tool          -> 対象directoryで go test + build
build scripts    -> 対象OS向けscript構文 + 生成path確認
shared contract  -> Python/Go双方の同一fixture結果を比較
```

共通CLI契約やJSON schemaを変えた場合だけbroader validationへ広げる。

## Context-efficient tests

- 成功時はpass件数または短い要約だけ残す
- failure時は失敗test / stderrの必要部分を優先する
- fixtureは小さく、目的ごとに分離する
- 大規模repo fixtureをそのまま複製しない

## New tool checklist

新規toolを追加する前に確認する。

- 既存toolで代用できないか
- 外部toolを使う方が保守コストが低くないか
- repeated context saving が adoption + maintenance cost を上回るか
- Small / Medium / Large のどこに属するか
- outputをboundedにできるか
- targeted validationを定義できるか

満たさない場合は実装しない。

## Completion report

完了報告は原則として次だけでよい。

```text
Changed:
- tool/path

Validation:
- targeted result

Compatibility:
- relevant Python/Go/external relation

Unverified:
- none / explicit item
```
