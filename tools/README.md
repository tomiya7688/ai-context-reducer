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
- `acceptance-extractor`, `exploration-stop-check`
- `validation-plan`, `compact-log`
- `context-pack-builder`
- `policy-index`, `responsibility-candidates`
- `doc-duplicate-hints`, `ignore-candidates`

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
  -> change-router

Policy Routing
  -> policy-index / external Semgrep etc.

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
- `.bat` を作る場合は可能なら `.sh` も用意する
- missing runtime / SDKを自動インストールしない
- Small repoへLarge解析を持ち込まない
- toolの維持コストが削減効果を上回る場合は導入しない
