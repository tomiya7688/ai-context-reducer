# Language Tool Setup

言語固有toolは、対象プロジェクトで既に使われている標準環境を優先し、追加インストールを前提にしません。

## セットアップ入口

```text
Windows: tools/setup.bat <project-root>
Linux/macOS: tools/setup.sh <project-root>
```

入口は native `acr-toolbox` を優先し、無ければ Python 版へ fallback します。`setup.bat/.sh` は `language-setup` も実行し、repositoryの実言語・規模・利用可能runtime/compilerから有効化候補を絞ります。

## 自動検出

| Language | Existing environment signal | Tool policy |
|---|---|---|
| Python | `python3` / `python` | Python固有toolを利用可能 |
| C# | `dotnet` | csproj / project map系を利用可能 |
| Go | `go` | package / import解析を利用可能 |
| C | `gcc` / `clang` / `cc` | include / compile-context系を利用可能 |
| C++ | `g++` / `clang++` / `c++` | include / project解析を利用可能 |
| GDScript | `godot4` / `godot` | Godot scene/resource関連を利用可能 |

Smallのshallow symbol解析は `acr-toolbox` 内蔵fallbackで実行できるため、runtime/compilerが無くても利用できます。Medium/Largeのdependency/project/graph解析は既存runtime/compilerがある場合だけ候補化します。セットアップ処理が package manager を呼び出したり、ランタイム・SDKを自動インストールしたりしません。

## 選択原則

```text
repoで使われている言語
  -> Small symbol analyzer: acr-toolbox native fallback
  -> Medium/Largeが必要か
  -> yes: 対応runtime/compilerが既にあれば候補化
  -> no: Small + Common toolsで運用
```

外部toolも同様で、`rg` / `fd` / `ctags` / `ast-grep` 等が既にあれば利用し、無ければ同梱fallbackへ戻ります。

## 規模との組み合わせ

- Small: symbols / shallow structureだけを優先
- Medium: import/include/project dependencyを追加
- Large: bounded graph / source structure indexを必要な場合だけ追加

言語環境が存在しても、Small repoへLarge解析を自動導入しません。

## 配布方針

Common機能は prebuilt `acr-toolbox` を Windows / Linux / macOS 向けに配布します。Goで独立実装している `affected-tests` / `go-symbols` / `go-import-map` / `go-package-graph` も同じplatform bundleへ含めます。その他の言語固有解析は、既存runtime/compilerを利用できる範囲を優先し、別SDKやparserの必須依存を増やさないことを基本とします。


## language-setup

```text
acr-toolbox language-setup <project-root>
python tools/common/small/language-setup/script/language_setup.py <project-root>
```

出力は `enabled_tools` / `skipped_languages` / `runtime_commands` を持ちます。Small / Medium / Large の段階をrepository規模から選びますが、Medium/Large解析をセットアップ時に無条件実行しません。`--run-small` は低コストなSmall解析を次の実行候補として明示するrouting flagです。


## language-run

`setup.bat/.sh` は選択後にSmall analyzerだけを自動実行します。

```text
acr-toolbox language-run <project-root>
python tools/common/small/language-run/script/language_run.py --acr-root /path/to/ai-context-reducer <project-root>
```

解析結果全文は既定で `<project-root>/.acr/language/` に保存し、stdoutにはstatus / backend / output path / skip理由だけを返します。Medium/Large toolは自動実行しません。

`acr-toolbox` native版は Python / C# / Go / C / C++ / GDScript のSmall symbol抽出をすべて内蔵fallbackで実行します。これはrouting用の近似解析であり、完全なparser代替ではありません。Medium/Large精度が必要な場合だけ既存SDK/compiler/parserを利用します。


## Medium portable fallback

```text
acr-toolbox language-medium-run <project-root>
```

Python import、C# ProjectReference、Go import、C/C++ include、GDScript load/preload/extends をportable native fallbackで抽出します。結果全文は `<project-root>/.acr/language-medium/` に保存し、stdoutはcompact summaryです。

Medium結果はrouting用の近似情報です。型解決・compile条件・MSBuild評価・Godot runtime semanticsなどが必要な場合だけ、既存SDK/compiler/parserへ進みます。


## Large high-precision routing

```text
acr-toolbox language-large-plan <project-root>
acr-toolbox language-large-run --allow-heavy <project-root>
```

`language-large-plan` は実行せず、既存SCIP index、Universal Ctags、dotnet、Go、C/C++ compiler、Godot等のavailabilityと推奨経路だけを返します。重い解析は自動では走りません。

`language-large-run` は `--allow-heavy` を必須にし、現時点では既存SCIP indexまたはUniversal Ctagsをsource-structure-indexへ取り込みます。利用可能な高精度backendが無ければMedium fallbackで止めます。
