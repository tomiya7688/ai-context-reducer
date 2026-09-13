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

## When to split a tool

小さい単一責務toolを形式だけで分割しない。CLI/orchestration、external I/O、analysis、formattingが独立した変更理由を持ち、分割後にworking setが小さくなる場合だけ分ける。

複数境界を持つtoolでは、必要に応じて次の内部構造を使える。

```text
entrypoint
  -> Commander相当: orchestration / routing
  -> Messenger相当: external boundary I/O
  -> Processing相当: concrete analysis / transformation
```

これは内部構造であり、公開CLIや対象repoへUPD構造を要求しない。

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
- 分割するならworking setが実際に小さくなるか
- targeted validationを定義できるか
