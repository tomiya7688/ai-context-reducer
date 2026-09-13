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

### When to split a tool

小さい単一責務toolを形式だけで分割しない。次のうち複数が独立して変更される場合に分割を検討する。

- CLI / dispatch / orchestration
- external boundary I/O: filesystem / Git / process / environment
- parsing / analysis / matching等の実処理
- output formatting / serialization

複数境界を持つtoolでは、必要に応じてUPD設計を内部構造へ適用できる。

```text
entrypoint
  -> Commander相当: orchestration / routing only
  -> Messenger相当: external boundary I/O
  -> Processing相当: concrete analysis / transformation
```

これは内部責務の分離方法であり、公開CLIや対象repositoryへUPD構造を要求するものではない。

分割後に「1つの小変更で読むfile数が増えるだけ」であれば分割しない。分割により変更理由ごとのworking setが小さくなる場合だけ採用する。

## Tool implementation rules

- full source / full log / full treeを既定出力にしない
- bounded / compact / summary-firstを既定にする
- truncation / uncertainty / fallbackを明示する
- index / analysis resultは原典の代替にしない
- missing runtime / SDK / packageを勝手にinstallしない
- Small repoへ高コスト解析を持ち込まない

### Scan classes

repo traversalは目的で区別する。

1. `targeted`: explicit file/pathだけを見る。repo rootへ広げない。
2. `bounded-index`: routing/index作成のためscopeを走査する。prune + scan budget必須。
3. `whole-scope-analysis`: graph/stats/hotspot等、指定scope全体を見ること自体が目的。全走査は許容するがprune + budget + truncation表示を持つ。

`whole-scope-analysis` だからといってdependency/generated/cacheを読む理由にはならない。必要な場合だけ明示optionで含める。

### Internal scan budget

出力だけをtruncateして内部で全repoを無制限に読む実装は、Context Reducerの目的に反する。

- generated / dependency / cache directoryは、結果から除外するだけでなくtraversal自体をpruneする
- repo-wide scanが必要なtoolは、`--max-files` / `--max-visited` / depth / scope等のscan budgetを持つ
- scan上限へ到達した場合は、結果が不完全であることを明示する
- changed itemごとに同じrepo scanを繰り返さず、必要なら1回のbounded indexを再利用する
- explicit paths / scopeが与えられた場合はrepo rootへ勝手に探索を広げない
- broader scanは安全性や精度上必要な場合にだけ、利用者が意図的に拡張できる形にする

`bounded output != bounded work` であることを常に区別する。

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
- scan classが明確か
- outputだけでなくinternal scanもboundedか
- 分割するならworking setが実際に小さくなるか
- targeted validationを定義できるか

満たさない場合は実装しない。
