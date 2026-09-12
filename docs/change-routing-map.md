# Change Routing Map

変更内容から、最初に読む実装・最初に走らせる検証・必要な詳細資料を直接引ける対応表を持つことを推奨します。

この考え方は `kadocacio` の AI 向けコード地図を参考にしています。

## 目的

AI に「どのファイルとテストが関係するか」を毎回リポジトリ全体から探索させず、変更カテゴリから最初の working set を機械的・半機械的に決めます。

例:

```text
変更対象 | 主な実装 | 先に走らせるテスト | 必要時に読む資料
起動/UI   | src/app/* | test_app_*          | docs/ui.md
保存      | src/data/*| test_save_*         | docs/data.md
AI判断    | src/ai/*  | test_ai_*           | docs/ai.md
```

## Source + Test routing

Task Routing は文書だけでなく、実装と検証にも使います。

推奨順:

```text
Task type / changed area
  -> target source
  -> matching targeted tests
  -> direct dependencies
  -> detailed docs only if needed
  -> full test suite before completion when appropriate
```

小変更ではまず targeted tests を実行し、問題がなければ完了前の標準検証へ進みます。

## 大きな文書は見出し検索から入る

README / SPEC / design docs が巨大な場合、最初から全文を読まず、見出し・キーワード検索で対象節を特定してから読むことを推奨します。

```text
search headings / keywords
  -> relevant section
  -> surrounding section only if needed
```

## Baseline invariants

変更で破ってはいけない既知の振る舞い・互換性・性能条件がある場合、短い invariant として AI 向け入口へ置きます。

詳細仕様そのものを複製するのではなく、今回の変更判断に必要な不変条件だけを保持します。

## Sensitive / generated data routing

実測ログ、評価出力、セーブデータ、バックアップ、参考データなどは通常の実装変更から除外します。

必要な場合のみ読み、明示指示なしに書き換えない領域をプロジェクト側で指定できます。

## Reproducible transformations

大量データや機械変換を伴う変更では、手作業の一括編集より再実行可能な変換手段を優先します。

可能なら次を用意します。

- dry-run
- 対象範囲の明示
- 変換前後の検証
- 再実行しても壊れにくい処理

これにより AI が巨大データを直接読み書きする必要を減らします。

## Validation trust

テスト件数やログ量ではなく、終了コード・明確な pass/fail・必要な実測条件を優先します。

性能や高速化の変更では、必要に応じて同一 seed / 固定 timestep / 同一入力など、比較可能な条件で結果傾向が維持されることを確認します。

## 最終報告

完了報告は長い作業履歴ではなく、次を短くまとめます。

- changed files
- compatibility / behavior impact
- validation performed
- unverified areas

未確認事項がある場合、全体を追加探索して埋めるより明示して引き継ぐことを許容します。

## 標準推奨

- 変更カテゴリから source / tests / docs を直接ルーティングする
- 大きな文書は全文より見出し検索を先に使う
- 重要 invariant は短く入口へ置く
- 実測出力・セーブ・バックアップ等を通常コンテキストから外す
- 大量変換は再実行可能 + dry-run を優先する
- targeted tests -> standard completion validation の順を使う
- 最終報告は changed files / impact / validation / unverified に圧縮する
