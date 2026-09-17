# Language Tool Setup

言語固有toolは、対象プロジェクトで既に使われている標準環境を優先し、追加インストールを前提にしません。

## セットアップ入口

```text
Windows: tools/setup.bat <project-root>
Linux/macOS: tools/setup.sh <project-root>
```

入口は native `acr-toolbox` を優先し、無ければ Python 版へ fallback します。

## 自動検出

| Language | Existing environment signal | Tool policy |
|---|---|---|
| Python | `python3` / `python` | Python固有toolを利用可能 |
| C# | `dotnet` | csproj / project map系を利用可能 |
| Go | `go` | package / import解析を利用可能 |
| C | `gcc` / `clang` / `cc` | include / compile-context系を利用可能 |
| C++ | `g++` / `clang++` / `c++` | include / project解析を利用可能 |
| GDScript | `godot4` / `godot` | Godot scene/resource関連を利用可能 |

環境が無ければ、その言語固有toolはスキップします。セットアップ処理が package manager を呼び出したり、ランタイム・SDKを自動インストールしたりしません。

## 選択原則

```text
repoで使われている言語
  -> 対応runtime/compilerが既にあるか
  -> yes: language-specific toolsを候補化
  -> no: Common toolsだけで運用
```

外部toolも同様で、`rg` / `fd` / `ctags` / `ast-grep` 等が既にあれば利用し、無ければ同梱fallbackへ戻ります。

## 規模との組み合わせ

- Small: symbols / shallow structureだけを優先
- Medium: import/include/project dependencyを追加
- Large: bounded graph / source structure indexを必要な場合だけ追加

言語環境が存在しても、Small repoへLarge解析を自動導入しません。

## 配布方針

Common機能は prebuilt `acr-toolbox` を Windows / Linux / macOS 向けに配布します。Goで独立実装している `affected-tests` / `go-symbols` / `go-import-map` / `go-package-graph` も同じplatform bundleへ含めます。その他の言語固有解析は、既存runtime/compilerを利用できる範囲を優先し、別SDKやparserの必須依存を増やさないことを基本とします。
