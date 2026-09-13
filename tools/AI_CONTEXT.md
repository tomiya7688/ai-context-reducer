# Tools AI Context

`tools/` 自体にも AI Context Reducer の原則を適用します。

## Goal

対象toolと直接依存だけで変更を完結できる構造を維持し、tools全体を毎回読み直さない。

最適化対象は **agentへ渡るcontext量と、必要情報へ到達するまでのagent側探索量** です。

Tool自身がagentの代わりに広くファイルを読むことは問題ありません。広い解析によってcompactな結果を返せるなら、それはContext Reducerとして有効です。

## Read routing

1. `tools/README.md`
2. この `tools/AI_CONTEXT.md`
3. 対象subtreeのlocal guide
4. 対象toolのREADME / source / tests / run-or-build script

別言語・別category・別toolは、契約・依存・互換性確認が必要な場合だけ読む。

## Stop condition

Goal / 入出力契約 / 直接変更対象 / validation / 既存toolとの重複有無が揃ったら探索を止める。

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

UPD Commander等の外部設計手法は内部実装規律の参考にしてよい。ただし、ai-context-reducerはそれらの適合checkerではなく、固有layer名・class名・命名規則を要求しない。逆に外部設計手法そのものをContext Reducerとして扱わない。

## Context Reducerを使った分割基準

分割判断は一般的な「綺麗な設計」ではなく、**このrepository自身のContext Reducer手法をtools開発へ適用できるか**で行う。

分割後、典型的な変更タスクについて次が成立するなら分割価値がある。

### 1. Task Routing

変更内容から最初に読むfileを直接絞れる。

```text
CLI option / dispatch変更
  -> entrypoint / commander相当

Git / filesystem境界変更
  -> messenger相当

解析ロジック変更
  -> processing相当

output contract変更
  -> formatter / serializer + contract test
```

変更理由が違うのに毎回同じ巨大fileを読む必要があるなら、分割候補とする。

### 2. Responsibility Map

各file/moduleの責務を短い1文で説明できることを目標にする。

責務説明が `A and B and C` のように複数の独立責務を並べないと書けない場合、理解負債のsignalとして分割を検討する。

### 3. Hierarchical Context

root policyを読んだ後、対象tool内でさらに局所的なworking setへ絞れる構造にする。

小変更のために同じtool directory内の全sourceを読む必要がある構造は避ける。ただし、分割によって逆に読むfile数や契約数が増えるだけなら分割しない。

### 4. Exploration Stop

agentが次を把握した時点で追加探索を止められる構造にする。

- 変更責務
- target file/module
- direct contract
- targeted validation

無関係な責務を確認しないと安全性を判断できない場合は、責務境界を見直す。

### 5. Change / Validation Routing

変更責務からtargeted test / build / smokeへ直接到達できるようにする。

```text
processing変更 -> processing tests
boundary変更   -> boundary contract tests
CLI変更        -> CLI smoke / parsing tests
shared contract変更 -> broader compatibility test
```

毎回full suiteしか安全なvalidation routeがない場合は、test responsibilityも見直す。

### 6. Source of Truthを増やしすぎない

分割のために同じ仕様・定数・schemaを複数fileへ複製しない。

分割後もcanonical contractを1箇所に保ち、他moduleはそれを参照する。Context Reducerのための分割がSource of Truthの分散を起こすなら採用しない。

### 分割しない条件

次の場合は小さい単一責務toolのまま保つ。

- 1fileを読むだけで責務全体を短く理解できる
- 変更理由がほぼ同じ
- targeted validationも同じ
- 分割するとimport / contract / file traversalが増えてagentのworking setが広がる
- cosmeticなCommander / Messenger / Processing分割にしかならない

必要な場合は内部構造として次を使える。

```text
entrypoint
  -> Commander相当: orchestration / routing
  -> Messenger相当: external boundary I/O
  -> Processing相当: concrete analysis / transformation
```

これはtools開発のworking setを狭めるための内部設計であり、公開CLIや解析対象repoへUPD構造を要求するものではない。

この基準により、`tools/` は「Context Reducerを提供するだけでなく、自身の開発にもTask Routing / Responsibility Map / Hierarchical Context / Exploration Stop / Targeted Validationを適用している」と説明できる状態を維持する。

## Tool implementation rules

- full source / full log / full treeをagent向け既定出力にしない
- bounded / compact / summary-firstをagent向け既定出力にする
- truncation / uncertainty / fallbackを明示する
- index / analysis resultは原典の代替にしない
- missing runtime / SDK / packageを勝手にinstallしない
- 精度のためにtool内部で広く読むことと、agentへ大量情報を渡すことを混同しない

## Scan classes

- `targeted`: explicit pathだけを見る。
- `routing-index`: routingのためscopeを横断し、candidate / reason / pointerへ圧縮する。
- `whole-scope-analysis`: graph / stats / hotspot等のため指定scope全体を読んでよい。
- `exact-analysis`: token estimate / dependency resolution / policy check等、精度のため実内容を読んでよい。

scan budgetは正しさを損なう必須制限ではなく、安全弁・performance optionとして扱う。

- 完全性が必要ならscope全体を読めるようにする
- `--max-files` 等を持つ場合は unlimited を選択可能にする
- limit到達時は不完全であることを明示する
- 不要なgenerated / dependency / cacheはpruneしてよい
- 必要なら明示optionで含められるようにする
- 同じ情報の無意味な再scanは避ける

```text
agent context should be bounded
internal work may be broad
accuracy > internal scan minimization
```

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

## New tool checklist

- 既存toolで代用できないか
- external toolの方が保守コストが低くないか
- repeated agent-context saving > adoption + maintenance cost か
- scan classが明確か
- broad scanがagent探索を置き換える価値を持つか
- outputはagent向けにcompactか
- 不完全解析ならその事実を明示できるか
- Task Routingで最初に読むfileを絞れるか
- Responsibility Mapとして責務を短く説明できるか
- targeted validationへ直接routingできるか
- 分割するならagent working setが実際に小さくなるか
