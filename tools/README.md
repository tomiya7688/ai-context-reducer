# Tools

AIへ渡す情報量を減らすための前処理・routing・validation補助ツール群です。

## Entry

```text
Windows: tools/setup.bat <project-root>
Linux/macOS: tools/setup.sh <project-root>
```

不足runtime / SDKは自動installしません。利用可能なnative / Python / external toolだけを候補化します。セットアップ時はcompatibleなSmall language analyzerだけ自動実行し、full resultは対象projectの `.acr/language/` へ保存します。

通常のrouting入口は次です。

```text
analyze-and-recommend / acr-toolbox analyze
  -> repository / runtime facts
  -> tool-selector / acr-toolbox select
  -> orient -> search -> scope -> inspect -> validate -> stop
```

`analyze` は同じtoolを重複して推薦しません。推薦するtoolの順序と、調査を終える条件は `tool-selector` / `acr-toolbox select` が決めます。

## Development routing

`tools/` 自体にもContext Reducerを適用します。

```text
tools/README.md
  -> tools/AI_CONTEXT.md
  -> target subtree local guide
  -> target tool README
  -> taskに対応するsource / tests / run-or-build script
  -> direct dependency only if needed
```

Goal・入出力契約・変更対象・validationが揃ったら探索を止めます。

分割もこの目的で行います。変更内容から関係するfileへ進み、無関係な処理を読まずに必要な確認まで行える構造を優先します。

### Self-application examples

次のtoolは、変更内容に応じて読む場所を絞り、各ファイルの役割を分け、必要な資料だけを読み、確認に必要な情報がそろったら調査を終える構成にしています。

```text
change-router
context-pack-builder
remote-delta
architecture-boundary-router
structural-search
context-manifest
context-budget
policy-index
doc-duplicate-hints
source-structure-index
tool-selector
```

複数の変更理由を持つ場合、必要に応じて次の責務へ分離します。

```text
entrypoint      -> CLI / compact output
commander       -> orchestration / routing
messenger       -> Git / filesystem / external process / profile等のboundary I/O
processing      -> matching / analysis / rendering
```

小さい単一責務toolは形式だけでは分割しません。分割後にagentのworking setが実際に小さくなる場合だけ採用します。

## Output policy

Machine outputの共通契約は `tools/JSON_CONTRACT.md` をSource of Truthとします。

- JSONが自然な結果形式なら、README/helpを毎回読まなくても意味が分かる自己説明的JSONを優先する
- 同じ事実をprose summaryとstructured fieldへ二重に入れない
- successful empty / unavailable / failure / truncated / unknownを区別する
- agent向け出力はbounded / compact
- full source / full log / full treeを既定出力にしない
- uncertainty / fallback / truncationを明示する
- 原典へ戻れるpath / symbol / reasonを残す
- 変更に関係する確認を優先する
- Markdown生成など成果物形式自体が目的のtoolは、無理にJSON化しない

Tool内部では、agentの探索を置き換えるためにscope全体やfile本文を読んで構いません。精度を落としてまで内部I/Oを減らすことは目的ではありません。

```text
agent context should be bounded
internal work may be broad
accuracy > internal scan minimization
```

## Python / Go

Python版とGo版は独立実装です。

- Python: build不要。stdlib中心。必要なら `run.bat` / `run.sh`
- Go: stdlib中心。`build.bat` / `build.sh` で test + build
- generic toolは合理的なら両方へ実装する
- 共有コードではなくCLI契約・fixture・testで整合を取る

## Validation

`.github/workflows/test-tools.yml` は `tools/**` 更新時に次を検証します。

```text
Python -> compileall + 各 tests/test_*.py をstdlibだけで実行
Go     -> tools配下の全 go.mod を列挙して go test ./...
```

portable binary buildも `go test ./...` 成功後だけartifact buildへ進みます。

## Native toolbox

`tools/common/native/acr-toolbox` はCommon機能のportable Go binaryです。Release buildでは `acr-toolbox version` でversion / commit / OS / architectureを確認できます。

主なsubcommand:

```text
analyze select search find tree stats doc-index slice
compact-log compact-diff remote-delta git-history-health syntax-health
structure-index context-budget hotspot-report context-manifest context-pack-builder
change-router validation-plan responsibility-candidates policy-index
doc-duplicate-hints ignore-candidates acceptance-extractor exploration-stop-check
materialize scoped-guides policy-check template version language-setup language-run language-medium-run language-large-plan language-large-run language-env env
```

## Categories

```text
common/small   shallow profile / cheap search
common/medium  routing / direct dependency / task context
common/large   graph / context-cost / whole-scope analysis
python         Python-specific analysis
go             Go-specific analysis
csharp/c/cpp/gdscript
profiles       optional project-type / routing input
```

## Main routing tools

```text
プロジェクト情報を調べる -> analyze-and-recommend / acr-toolbox analyze
言語と解析環境を調べる -> language-setup / acr-toolbox language-setup
コードを軽く調べる -> language-run / acr-toolbox language-run
ファイル間の関係を調べる -> acr-toolbox language-medium-run
詳しい解析の準備をする -> acr-toolbox language-large-plan
作業場所に合う指示を読む -> scoped-guides / acr-toolbox scoped-guides
使うtoolを決める -> tool-selector / acr-toolbox select
検索して場所を探す -> search / find / structural-search / tree / doc-index / slice
調査を終える条件を確かめる -> acceptance-extractor / exploration-stop-check
共有先との差分を見る -> remote-delta / compact-diff
各ファイルの担当を整理する -> responsibility-candidates
変更内容から読む場所を探す -> change-router
機能ごとの境界を調べる -> architecture-boundary-router (optional)
変更に関係するテストを探す -> affected-tests
作業に関係する規則を探す・確認する -> policy-index / policy-check / acr-toolbox policy-check
似た説明がある文書を探す -> doc-duplicate-hints
普段は読ませないファイルの候補を調べる -> ignore-candidates
ひな型からファイルを作る -> template / acr-toolbox template
Validation                -> validation-plan / Syntax Health Validation -> syntax-health (when available) / compact-log
Context pack              -> context-pack-builder
Source structure          -> language-specific symbols / dependency / graph tools -> source-structure-index
Context manifest          -> Context Manifest -> context-manifest (optional)
Context priority          -> Context Priority / Hotspot -> context-budget / hotspot-report (signals)
Git history health        -> git-history-health
```

`tool-selector` は候補を `orient -> search -> scope -> inspect -> validate -> stop` の順で返します。各entryは `phase / activation / availability / reason` を持ち、external backendが必要なtoolは利用可能性もrouting時点で反映します。

`structural-search` はplain text searchでは候補が広すぎる場合に構文形状で絞ります。既に `ast-grep` があればbackendとして再利用し、無ければPython sourceだけstdlib AST fallbackを使います。外部toolは自動installしません。

`source-structure-index` はlanguage-specific analyzerや外部indexerの結果を共通IRへ正規化し、full indexをagentへ再出力せず、`query` / bounded `expand` で必要部分だけ返します。SCIP / Tree-sitter等の完全再実装ではありません。Python版と `acr-toolbox structure-index` は同じindex formatを読み書きしますが、実装コードは共有しません。

`context-manifest` は [資料の場所を短い一覧にする](../docs/jp/手法/資料の場所を短い一覧にする.md) の補助実装です。手法のSource of Truthはdocs側にあり、repository-wide file listやtool固有priorityを手法そのものにはしません。agentへ渡すmanifestはpointer中心かつboundedにし、現在taskとの関連でworking setを選びます。

`context-budget` / `hotspot-report` は [今回読むファイルを選ぶ](../docs/jp/手法/今回読むファイルを選ぶ.md) の補助signalです。size / cost / depth等はtask relevanceの代わりではなく、高精度routingやsliceが必要な場所を判断する材料として使います。hotspot上位を自動的に読む対象にはしません。

`doc-duplicate-hints` は [同じ説明を何度も書かない](../docs/jp/手法/同じ説明を何度も書かない.md) のhint実装です。重複候補を絞るだけで、どちらがSource of Truthか、intentional duplicationか、削除可能かは決定しません。自動削除・自動統合には使いません。

`ignore-candidates` は [AIに普段読ませないファイルを決める](../docs/jp/手法/AIに普段読ませないファイルを決める.md) の候補提示実装です。generated / logs / vendor / caches等を通常contextから外す候補を示すだけで、Source of Truth判定や `.gitignore` 等への適用は行いません。validationで必要なartifactはtask-specific evidenceとして別扱いします。

`syntax-health` は [まず、コードの構文チェックをする](../docs/jp/手法/まず、コードの構文チェックをする.md) の補助実装です。利用可能なparserの結果をcheap evidenceへ圧縮するだけで、syntax successをsemantic correctnessやtask completionとはみなしません。parser / grammarを自動installせず、必要なtargeted tests / compiler / runtime validationへroutingします。

`architecture-boundary-router` は [機能ごとのコードの分け方から読む場所を決める](../docs/jp/手法/機能ごとのコードの分け方から読む場所を決める.md) の補助実装です。手法のSource of Truthはdocs側にあり、tool仕様やprofile形式を手法そのものにはしません。対象projectが既に持つ責務・境界情報を任意profileとして渡した場合だけ、最初のworking set選択に使い、特定architectureへの適合checkerにはしません。

UPD Commanderを含む外部設計手法は、tools内部の責務分離や実装構造の参考にできますが、ai-context-reducerの機能要件・適合条件・標準architectureにはしません。

## Core rules

- full source / logs / docsをagentへ再出力しない
- generated outputをSource of Truthにしない
- runtime / SDK / packageを勝手にinstallしない
- Small repoへ不要なLarge解析を持ち込まない
- external toolが既にある場合は高品質backendとして使ってよい
- toolの維持コストがagent-context削減効果を上回るなら追加しない

詳細は各tool README、`tools/AI_CONTEXT.md`、`tools/JSON_CONTRACT.md`、`tools/NATIVE_COVERAGE.md`、`docs/internal/jp/追加インストールを減らすツール運用.md` を参照してください。


## Language portability

```text
Small  -> acr-toolbox native shallow symbols
Medium -> acr-toolbox native dependency/project-map fallback
Large  -> existing SDK/compiler/parser when justified
```

Small/Medium routingはPythonや各言語SDKが無くても成立します。Largeや高精度解析だけ既存runtime/compiler/parserを利用し、自動installはしません。


Large解析は `language-large-plan` でbackend候補を確認してから、必要な場合だけ `language-large-run --allow-heavy` を明示実行します。SCIP / Universal Ctags が利用可能なら source-structure-index へ統合し、無ければMedium evidenceで止めます。
