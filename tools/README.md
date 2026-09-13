# Tools

AI に渡す情報量を減らすための前処理ツール群です。

## 推奨入口

通常は次だけ覚えれば十分です。

```text
Windows: tools/setup.bat <project-root>
Linux/macOS: tools/setup.sh <project-root>
```

セットアップは次を自動判定します。

- project規模 / 主要言語 / project type
- native `acr-toolbox` の利用可否
- Python fallback の利用可否
- Git
- Python / .NET / Go / C / C++ / Godot の既存実行環境
- optional external tools (`rg`, `fd`, `ctags`, `ast-grep` 等)

不足runtimeやSDKを勝手にインストールしません。使えるtoolだけを候補化します。

詳細は `docs/portable-tools.md` と `docs/language-tool-setup.md` を参照してください。

## Tools自身にもContext Reducerを適用する

`tools/` の開発・保守自体もこのrepositoryの原則に従います。

AIがtoolを変更するときは、最初から `tools/` 全体を読みません。

```text
tools/README.md
  -> tools/AI_CONTEXT.md
  -> target language/subtree local guide
  -> target tool README / source / tests / build-or-run script
  -> direct dependency only if needed
```

主なlocal guide:

- `tools/AI_CONTEXT.md`: tools全体のrouting / stop condition / Source of Truth / validation
- `tools/python/AI_CONTEXT.local.md`: Python tool固有の差分
- `tools/go/AI_CONTEXT.local.md`: Go tool固有の差分

対象toolのGoal・入出力契約・変更箇所・必要validationが揃ったら探索を止めます。別言語版、別category、全tool一覧は、互換性・依存・重複確認が必要な場合だけ追加で読みます。

ツール自身の出力も同じ考え方を守ります。

- summary / index first
- bounded output
- full source / full logs / full treeを既定出力にしない
- truncation / uncertainty / fallbackを明示する
- 解析結果から原典へ戻れるpath / symbol / reasonを残す
- targeted validationを優先し、共有contract変更時だけbroader validationへ広げる

新規・既存toolのレビューでは、機能が正しいだけでなく次も確認します。

- 不要な全repo scanをしていないか
- 既定出力が巨大にならないか
- limit / scope / targetを指定できるか
- 同じsourceを複数段で読み直していないか
- success時に巨大logを残していないか
- source-of-truthへ戻るpointerを失っていないか

これらに反するtoolは、機能追加より先にcontext-efficientな形へ修正します。

## Native toolbox

Commonで頻繁に使う機能は Go 製単一バイナリ `acr-toolbox` に統合します。

現在のsubcommand:

```text
analyze
search
find
tree
stats
doc-index
slice
compact-log
compact-diff
remote-delta
language-env
env
```

主な対応:

- `search`: `rg` の軽量fallback
- `find`: `fd` の軽量fallback
- `tree`: bounded tree
- `stats`: `scc` の簡易fallback
- `doc-index`: Markdown見出し索引
- `slice`: 必要箇所だけbounded excerpt
- `compact-log`: failure/warning中心のログ圧縮
- `compact-diff`: changed files / shortstat / bounded diff
- `remote-delta`: compact remote context
- `language-env`: 言語runtime/compiler検出

Windows / Linux / macOS の x64 / arm64 をGitHub Actionsでcross buildします。ローカルbuild用に `build.bat` / `build.sh` も置きます。

Native対応状況は `tools/NATIVE_COVERAGE.md` を参照してください。

## Runtime selection

```text
prebuilt native binary
  -> Python reference / fallback
  -> optional installed external tool
```

ただし `rg` / `fd` / `ctags` / `ast-grep` 等が既にある場合は、高速・高精度backendとして優先して構いません。

元repoからvariantを勝手に削除するのではなく、対象プロジェクトへ導入するときに必要なvariantだけ materialize します。

## Python / Go implementation policy

Python版とGo版は共有実装にせず、**完全に独立した実装**として扱います。

- Python版は build 不要の script を基本とし、必要なら `run.bat` / `run.sh` を置く
- Go版は `build.bat` / `build.sh` で一発buildできる単一binaryを基本とする
- generic toolをPython側へ追加した場合、Go側で同等機能を実装できない明確な理由がなければ、Go版も積極的に追加する
- 片側のbugや仕様変更をもう片側へ自動コピーせず、入出力契約とtestで互換性を保つ
- language-specific toolは言語差を尊重し、名前だけを機械的に一致させない

現在の主要対応:

```text
Python affected-tests  <-> Go affected-tests
python-symbols         <-> go-symbols
python-import-map      <-> go-import-map
python-module-graph    <-> go-package-graph
```

## Tool categories

```text
tools/
├─ common/
│  ├─ small/
│  ├─ medium/
│  ├─ large/
│  └─ native/
├─ python/
├─ csharp/
├─ go/
├─ c/
├─ cpp/
├─ gdscript/
└─ profiles/
```

- Small: shallow profile / symbols / cheap search
- Medium: direct dependency / routing / task context
- Large: bounded graph / structure index / context cost analysis

## Common tools

### Small

- `analyze-and-recommend`: repoと環境を浅く分析して推奨手法/toolを選ぶ
- `environment-plan`: OS / arch / native / Python / external toolを判定
- `language-environment-plan`: Python / .NET / Go / C / C++ / Godot環境を判定
- `tool-selector`: 規模・言語・project typeからtool候補を選択
- `repo-profile`, `repo-stats`, `project-type-profile`
- `text-search`, `path-find`, `tree-view`, `doc-index`
- `file-role-map`, `source-of-truth-candidates`

### Medium

- `compact-diff`, `remote-delta`
- `change-router`
- `architecture-boundary-router`: architecture profileからlayer / role / boundaryを分類し、最初に読むscopeを絞る
- `affected-tests`: changed filesからtest候補 / confidence / broader fallbackを選ぶ
- `acceptance-extractor`, `exploration-stop-check`
- `validation-plan`, `compact-log`
- `context-pack-builder`
- `policy-index`, `responsibility-candidates`
- `doc-duplicate-hints`, `ignore-candidates`

`architecture-boundary-router` は UPD Commander の責務境界と正式通信経路の考え方を一般化したものです。`tools/profiles/upd-commander.json` が最初の実例で、profileは原典の設計書を置き換えずrouting hintとして使います。

### Large

- `context-manifest`
- `hotspot-report`
- `target-slice`
- `context-budget`

## Language-specific tools

| Language | Small | Medium | Large | Existing environment signal |
|---|---|---|---|---|
| Python | `python-symbols` | `python-import-map` | `python-module-graph` | `python3` / `python` |
| C# | `csharp-symbols` | `csharp-project-map` | `csharp-project-graph` | `dotnet` |
| Go | `go-symbols` | `go-import-map` | `go-package-graph` | `go` |
| C | `c-symbols` | `c-include-map` | `c-include-graph` | `gcc` / `clang` / `cc` |
| C++ | `cpp-symbols` | `cpp-include-map` | `cpp-include-graph` | `g++` / `clang++` / `c++` |
| GDScript | `gdscript-symbols` | `gdscript-dependency-map` | `godot-scene-graph` | `godot4` / `godot` |

環境が無ければ、その言語固有toolは自動導入しません。Common toolsだけで運用できます。

## Method mapping

```text
Search-first / Read-second
  -> search / find / tree / doc-index / slice

Exploration Stop Condition
  -> acceptance-extractor / exploration-stop-check

Remote Delta First
  -> remote-delta / compact-diff

Responsibility Map
  -> responsibility-candidates

Change Routing Map
  -> change-router / architecture-boundary-router

Architecture boundary routing
  -> architecture-boundary-router + optional profile

Change / Test Impact Routing
  -> affected-tests / external Nx or Pants

Policy Routing
  -> policy-index / external ast-grep etc.

Validation Routing
  -> validation-plan / compact-log

Context Pack
  -> context-pack-builder

Source Structure Index
  -> language-specific symbols / dependency / graph tools

Context Priority
  -> context-manifest / context-budget / hotspot-report

Information responsibility
  -> source-of-truth-candidates / doc-duplicate-hints
```

## 基本方針

- full source / full logs / full docs を再出力しない
- bounded / truncated output を明示する
- 解析結果は索引であり、必要なら原典へ戻る
- Python / native / external tool のどれか1つに必須依存しない
- Python版はbuildを要求しない
- Go版toolは可能な限り `build.bat` / `build.sh` で一発build可能にする
- `.bat` を作る場合は可能なら `.sh` も用意する
- missing runtime / SDKを自動インストールしない
- Small repoへLarge解析を持ち込まない
- toolの維持コストが削減効果を上回る場合は導入しない
