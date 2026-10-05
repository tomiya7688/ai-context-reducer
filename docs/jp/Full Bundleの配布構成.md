# Full Bundleの配布構成

この文書は、通常版とFull Bundleの違いと、Full Bundleに含めるものを説明します。配布物の追加や更新時に、利用者が実行に必要な環境を別途調べて組み立てずに済むよう、含有物と動作の境界を定めています。

## 例: CLIだけ使うか、画面からも使うか

`acr-toolbox`をコマンドから使う人には、軽量な通常版で足ります。GUI Hubや言語別の補助ツール、テンプレートもまとめて使いたい人にはFull Bundleを選べます。Full Bundleは通常版の機能を保ち、追加のファイルを同じ配布物に収めたものです。

Full Bundleに含まれるツールは、すべてが自動で動くわけではありません。画面から浅い情報を調べて利用候補を示し、重い解析やファイルを書き換える処理は、利用者が実行を選んだ後に動かします。この境界により、展開しただけで時間のかかる処理や環境変更が始まることを防ぎます。

## 通常版との違い

| 配布物 | 主な内容 | 向いている使い方 |
|---|---|---|
| 通常版 | `acr-toolbox`と共通の補助CLI | コマンドから必要な機能を使う |
| Full Bundle | 通常版と同じCLIに、GUI Hub、言語別ツール、Python版の代替実装、セットアップ用スクリプト、プロファイル、テンプレート、利用者向け文書を追加 | GUIや複数の補助機能をまとめて使う |

Full Bundleのルートには、通常版と同じファイル名で次のCLIと文書を置きます。通常版で使っていたコマンドや機械出力は、Full Bundleでも同じように使えます。

```text
acr-toolbox(.exe)
go-symbols(.exe)
go-import-map(.exe)
go-package-graph(.exe)
affected-tests(.exe)
README.md
TOOLS_README.md
LICENSE
RELEASE_MANIFEST.json
```

Full Bundle固有の構成は[`FULL_BUNDLE_MANIFEST.json`](../../release/FULL_BUNDLE_MANIFEST.json)で管理します。GUIや代替実装の情報を通常版の一覧へ混ぜないため、通常版だけを使う利用者にも余分な依存関係を要求しません。

## Full Bundleに含めるもの

- **ビルド済みCLI:** 対応する各OS向けに実行形式で同梱します。利用者がGoの開発環境を用意したり、ソースからビルドしたりする必要はありません。
- **GUI Hub:** 既存のCLIを画面から呼び出し、結果を表示します。GUI専用の解析処理を別に持たず、CLIの出力と動作を共通の根拠にします。
- **Python版の代替実装:** native版を使えない場合など、明示して使うために同梱します。通常のGUIとCLIの利用にはPythonを要求しません。代替実装を実行する場合だけ、環境に既にあるPythonを使います。
- **セットアップ・解析スクリプト:** `setup.sh` / `setup.bat` と `analyze.sh` / `analyze.bat` をルートに置きます。スクリプトは同梱CLIを優先し、分析処理そのものは重複実装しません。
- **プロファイルとテンプレート:** プロジェクトの種類に応じた任意の補助情報や、AI向け案内のひな形を含みます。プロファイルは必須ではありません。
- **利用者向け文書:** 日本語の原文書を`docs/jp/`、その英訳を`docs/en/`に置きます。リリース内部記録やテスト用ファイルは含めません。

配布物の中身は次の構成です。

```text
ai-context-reducer-full-v1.1.0-<platform>/
├─ acr-toolbox(.exe) と共通CLI
├─ README.md / TOOLS_README.md / LICENSE
├─ RELEASE_MANIFEST.json
├─ FULL_BUNDLE_MANIFEST.json
├─ setup.sh / setup.bat / analyze.sh / analyze.bat
├─ gui/acr-hub(.exe)
├─ fallback/python/
│  ├─ common/
│  └─ languages/ (python / c / cpp / csharp / gdscript)
├─ profiles/
├─ templates/
└─ docs/ (jp / en)
```

## 追加インストールと自動実行

Full Bundleは、Go、Python、.NET、C/C++の開発環境や外部ツールを勝手にインストールしません。既に利用できる外部解析器があれば使うことがあります。見つからない場合は、同梱のCLIや利用可能な代替手段へ戻ります。

含まれている機能は、次のように段階を分けて使います。

```text
プロジェクトの基本情報を調べる
  -> 使えそうな機能を表示する
  -> 利用者が実行を選ぶ
```

実行時間の長い解析、外部SDKやコンパイラーを使う処理、ファイルへ書き込む処理は、画面を開いただけでは実行しません。GUIの「分析」も全ツールを一括で動かす操作ではありません。

## AIに構成変更や確認を依頼する

Full Bundleの変更では、この文書と[`FULL_BUNDLE_MANIFEST.json`](../../release/FULL_BUNDLE_MANIFEST.json)のパスをAIへ渡し、通常版との互換性を保つ範囲を明記します。AIには、最初に変更候補と関連する配布・検査手順を挙げさせ、マニフェストと実際のファイルを照合させます。ソースだけを見て、完成したアーカイブまで確認したとは扱いません。

```text
Full Bundleの変更・確認をしてください：[作業内容]
この文書とFULL_BUNDLE_MANIFEST.jsonを基準に、通常版CLIの名前・引数・出力を保ってください。
最初に関係するファイルと検査を理由付きで示してください。完了時は実際に確認した配布物、検査結果、未確認範囲を報告してください。
```

## 互換性と配布確認

Full Bundleの追加後も、通常版のCLI名、サブコマンド、引数、終了コード、機械向け出力形式を維持します。通常版は別配布物として引き続き提供し、Full Bundleだけの補助ファイルを通常版の必須条件にしません。

配布対象の一覧はマニフェストから展開し、完成したアーカイブの内容と照合します。これにより、設計上含めると決めたファイルが配布物に入っているか確認できます。各OSでの実行確認は[リリース手順](リリースを確認して公開する.md)に記載します。
