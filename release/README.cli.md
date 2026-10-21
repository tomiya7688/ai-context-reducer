# AI Context Reducer — 配布候補 / Release candidate

このアーカイブは検証用です。公開版v1.0.0は2026年10月22日に取り下げました。
This archive is a validation candidate. The previous v1.0.0 was withdrawn on October 22, 2026.

## 最初に試す / First operation

Windowsは `acr-toolbox.exe version`、Linux・macOSは `./acr-toolbox version` を実行し、版とコミットを確認します。
Run `acr-toolbox.exe version` on Windows or `./acr-toolbox version` on Linux/macOS to inspect the version and commit.

プロジェクトの概要は `acr-toolbox analyze <プロジェクトのパス>` で調べます。
Use `acr-toolbox analyze <project-path>` for a project overview (use `./acr-toolbox` on Unix).

基本の概要表示にPythonやGoの追加インストールは不要です。Gitや各言語の詳細解析など、個別機能は別の環境を必要とする場合があります。不足した環境を自動インストールしません。
Basic overview operations need no additional Python or Go installation. Features such as Git inspection or detailed language analysis may require existing external tools; missing dependencies are not installed automatically.

## GUI同梱版 / Full Bundle

Full Bundleだけに `gui/acr-hub.exe`（Windows）、`gui/acr-hub`（Linux・macOS）があります。同梱版のルートを保持したまま起動してください。
Only the Full Bundle includes `gui/acr-hub.exe` (Windows) or `gui/acr-hub` (Linux/macOS). Keep the bundle layout intact.

同梱の `setup` は利用可能な浅い解析のみを行います。重い解析を自動実行する入口ではありません。
Bundled setup runs compatible shallow analysis, not automatic heavy analysis.

## 説明 / Documentation

- [手法と導入の説明 / Methods and adoption](https://github.com/tomiya7688/ai-context-reducer#readme)
- [CLIの説明 / CLI reference](https://github.com/tomiya7688/ai-context-reducer/blob/main/tools/common/native/acr-toolbox/README.md)
- Full Bundleの `docs/jp/`・`docs/en/` には日英文書も含まれます。実装の参照先などはリポジトリで確認してください。
- The Full Bundle includes Japanese/English documentation in `docs/jp/` and `docs/en/`. Consult the repository for implementation references.
