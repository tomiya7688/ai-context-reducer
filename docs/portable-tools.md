# Portable Tools / Runtime Selection

このリポジトリの補助ツールは、対象環境への追加インストールをできるだけ要求しない方針とします。

## 基本方針

実行実装の優先順位:

```text
prebuilt native binary
  -> available Python implementation
  -> available shell / batch wrapper
  -> external optional tool
```

ただし `rg` など高品質な外部ツールが既に存在する場合は、同等用途の内蔵実装より優先してよいものとします。

## 配布単位

頻繁に使う Common tool は可能なら次を用意します。

```text
tool/
├─ script/       # Python reference implementation
├─ native/       # Go/C++ source
├─ bin/          # optional local build output; normally gitignored
├─ run.sh
└─ run.bat
```

バイナリはソース管理へ大量に直接コミットせず、GitHub Actions / Release artifact で生成することを推奨します。

## Native implementation

第一候補は Go とします。

理由:

- cross compile が容易
- 単一バイナリ化しやすい
- Windows / Linux / macOS を同一コードから生成しやすい
- file walking / text processing / JSON CLI と相性がよい

C / C++ は parser や既存ライブラリ利用など、Go より適する場合に使います。

## Python implementation

Python版は次の用途を持ちます。

- 仕様の参照実装
- 修正しやすい fallback
- AI がロジックを確認・変更しやすい実装

Pythonが無い環境では native binary を使います。

## Shell wrappers

`.bat` を置く場合、可能なら同等の `.sh` も置きます。

wrapper は次だけを担当します。

- OSに合うbinaryの選択
- binaryが無ければPython fallback
- 引数の透過

wrapper内へ本処理を大量実装しません。

## Environment-aware adoption

対象repoへ導入するときは全実装をコピーしません。

```text
environment probe
  -> OS / architecture / Python / Git / optional tools
  -> usable implementationを選択
  -> selected tools only
  -> unused variants are not materialized
```

すでに導入済みのtool setを整理する場合も、削除は対象tool directory内だけに限定し、dry-runを標準とします。

## 推奨 native 化対象

優先度 High:

- text-search
- path-find
- tree-view
- repo-stats
- analyze-and-recommend

優先度 Medium:

- compact-log
- target-slice
- doc-index
- file-role-map
- context-budget

言語固有parser系は、まずPython / lightweight実装を維持し、利用頻度と効果が確認できてからnative化します。
