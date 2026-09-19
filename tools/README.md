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

`analyze` はtool推薦を重複保持しません。ordered tool routingとexploration-stop条件のSource of Truthは `tool-selector` / `acr-toolbox select` です。

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

分割もこの目的で行います。一般的な設計美ではなく、変更内容から必要fileへ直接routingでき、無関係な責務を読まずtargeted validationまで進める構造を優先します。

### Self-application examples

次のtoolは、このrepositoryの Task Routing / Responsibility Map / Hierarchical Context / Exploration Stop の考え方を開発構造そのものへ適用しています。

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
- targeted validationを優先する
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

`tools/common/native/acr-toolbox` はCommon機能のportable Go binaryです。

主なsubcommand:

```text
analyze select search find tree stats doc-index slice
compact-log compact-diff remote-delta git-history-health syntax-health
structure-index context-budget hotspot-report context-manifest context-pack-builder
change-router validation-plan responsibility-candidates policy-index
doc-duplicate-hints ignore-candidates acceptance-extractor exploration-stop-check
materialize scoped-guides policy-check language-setup language-run language-medium-run language-large-plan language-large-run language-env env
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
Repository facts          -> analyze-and-recommend / acr-toolbox analyze
Language tool selection   -> language-setup / acr-toolbox language-setup
Shallow language analysis -> language-run / acr-toolbox language-run
Medium dependency routing -> acr-toolbox language-medium-run
Large backend planning    -> acr-toolbox language-large-plan
Scoped instructions       -> scoped-guides / acr-toolbox scoped-guides
Ordered tool routing      -> tool-selector / acr-toolbox select
Search-first              -> search / find / structural-search / tree / doc-index / slice
Exploration stop          -> acceptance-extractor / exploration-stop-check
Remote delta              -> remote-delta / compact-diff
Responsibility            -> responsibility-candidates
Change routing            -> change-router
Architecture hints        -> architecture-boundary-router + project-provided profile
Affected tests            -> affected-tests
Policy routing            -> policy-index / policy-check / acr-toolbox policy-check
Validation                -> validation-plan / syntax-health / compact-log
Context pack              -> context-pack-builder
Source structure          -> language-specific symbols / dependency / graph tools -> source-structure-index
Context priority          -> context-manifest / context-budget / hotspot-report
Git history health        -> git-history-health
```

`tool-selector` は候補を `orient -> search -> scope -> inspect -> validate -> stop` の順で返します。各entryは `phase / activation / availability / reason` を持ち、external backendが必要なtoolは利用可能性もrouting時点で反映します。

`structural-search` はplain text searchでは候補が広すぎる場合に構文形状で絞ります。既に `ast-grep` があればbackendとして再利用し、無ければPython sourceだけstdlib AST fallbackを使います。外部toolは自動installしません。

`source-structure-index` はlanguage-specific analyzerや外部indexerの結果を共通IRへ正規化し、full indexをagentへ再出力せず、`query` / bounded `expand` で必要部分だけ返します。SCIP / Tree-sitter等の完全再実装ではありません。Python版と `acr-toolbox structure-index` は同じindex formatを読み書きしますが、実装コードは共有しません。

`architecture-boundary-router` は特定architectureへの適合checkerではありません。対象projectが既に持つ責務・境界情報を任意profileとして渡した場合だけ、最初のworking set選択に使います。

UPD Commanderを含む外部設計手法は、tools内部の責務分離や実装構造の参考にできますが、ai-context-reducerの機能要件・適合条件・標準architectureにはしません。

## Core rules

- full source / logs / docsをagentへ再出力しない
- generated outputをSource of Truthにしない
- runtime / SDK / packageを勝手にinstallしない
- Small repoへ不要なLarge解析を持ち込まない
- external toolが既にある場合は高品質backendとして使ってよい
- toolの維持コストがagent-context削減効果を上回るなら追加しない

詳細は各tool README、`tools/AI_CONTEXT.md`、`tools/JSON_CONTRACT.md`、`tools/NATIVE_COVERAGE.md`、`docs/portable-tools.md` を参照してください。


## Language portability

```text
Small  -> acr-toolbox native shallow symbols
Medium -> acr-toolbox native dependency/project-map fallback
Large  -> existing SDK/compiler/parser when justified
```

Small/Medium routingはPythonや各言語SDKが無くても成立します。Largeや高精度解析だけ既存runtime/compiler/parserを利用し、自動installはしません。


Large解析は `language-large-plan` でbackend候補を確認してから、必要な場合だけ `language-large-run --allow-heavy` を明示実行します。SCIP / Universal Ctags が利用可能なら source-structure-index へ統合し、無ければMedium evidenceで止めます。
