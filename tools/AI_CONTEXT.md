# Tools AI Context

`tools/` 自体にも AI Context Reducer の原則を適用します。

## Goal

対象toolと直接依存だけで変更を完結できる構造を維持し、tools全体を毎回読み直さない。

## Read routing

1. `tools/README.md`
2. この `tools/AI_CONTEXT.md`
3. 対象subtreeのlocal guide
4. 対象toolのREADME / source / tests / run-or-build script

別言語・別category・別toolは、契約・依存・互換性確認が必要な場合だけ読む。

## Stop condition

次が揃ったら探索を止める。

- Goal
- 入出力契約
- 直接変更対象
- 必要なvalidation
- 既存toolとの重複有無

## Source of Truth

```text
対象toolのsource + tests
  > 対象tool README / local guide
  > tools/README.md
  > generated output / dist
```

## Internal architecture rules

- CLI dispatcher / entrypoint はroutingに徹し、実処理を抱え込まない
- filesystem / Git / environment / parsing / formatting等の責務を必要に応じて分離する
- module間の越境は明示的な関数・データ契約を通す
- 実処理はその責務を所有するmoduleへ置く
- 無関係な複数機能を1ファイル理解へ強制する構造を避ける
- 共通化は理解・保守コストを実際に下げる場合だけ行う

UPD Commander等の外部設計手法は、これらの内部実装規律を考える参考には使ってよい。ただし、ai-context-reducerはそれらの適合checkerではなく、固有layer名・class名・命名規則を要求しない。

逆に、UPD Commander等の外部設計手法そのものをContext Reducerとして扱わない。設計手法側へAI_CONTEXTやcontext削減機能を必須導入することもしない。

## Tool implementation rules

- full source / full log / full treeを既定出力にしない
- bounded / compact / summary-firstを既定にする
- truncation / uncertainty / fallbackを明示する
- index / analysis resultは原典の代替にしない
- missing runtime / SDK / packageを勝手にinstallしない
- Small repoへ高コスト解析を持ち込まない

## Python / Go

- Python: build不要。stdlib中心。必要なら `run.bat` / `run.sh`
- Go: stdlib中心。`build.bat` / `build.sh` からtest + build
- generic toolは合理的なら両方へ実装する
- 共有コードではなくCLI契約・fixture・testで整合を取る

## Validation routing

```text
README/docs only -> link/path/example確認
Python tool      -> syntax/smoke + targeted test
Go tool          -> target directoryで go test + build
build scripts    -> script構文 + output path
shared contract  -> Python/Goのfixture結果比較
```

共通CLI契約やJSON schemaを変えた場合だけbroader validationへ広げる。

## New tool checklist

- 既存toolで代用できないか
- external toolの方が保守コストが低くないか
- repeated context saving > adoption + maintenance cost か
- outputをboundedにできるか
- targeted validationを定義できるか

満たさない場合は実装しない。
