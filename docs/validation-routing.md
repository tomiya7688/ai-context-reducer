# Validation Routing

変更内容に応じて、必要な検証手段だけを選ぶ方針です。

この考え方は `obake-no-sumika` の実運用を参考にしています。外部プロジェクトは実装例であり、標準仕様そのものは依存しません。

## 目的

すべての変更に対して同じ検証を大量実行したり、逆に unit test だけで十分だと決めつけたりせず、変更の性質に合った証拠を選びます。

```text
Change type
  -> required evidence
  -> smallest sufficient validation
  -> additional evidence only if needed
```

## Evidence types

代表的な検証手段:

- static / syntax check
- targeted unit / regression test
- deterministic runtime / smoke test
- structured evaluation log
- generated-data consistency check
- visual / interactive confirmation
- performance measurement

すべてを常に実行する必要はありません。

## Route by change type

例:

```text
純粋なロジック変更
  -> targeted tests

確率的・時間依存の挙動
  -> fixed seed / bounded runtime + structured log

UI / drawing / layout
  -> automated smoke + visual confirmation

データ契約変更
  -> schema / parser tests + representative data validation

性能変更
  -> correctness tests + comparable measurement conditions
```

テスト成功だけでは確認できない性質を、テスト結果から推測して済ませないことを推奨します。

## Structured observation before broad code reading

実行時の挙動調査では、可能なら座標・状態・イベント・判断結果などを bounded / structured log として記録します。

巨大な通常ログや全ソースを先に読む代わりに、再現条件と必要な観測値だけを確認します。

成功時のログ全文は Context Pack に保持せず、結果要約だけ残します。失敗時だけ関連範囲を追加します。

## Deterministic reproduction

ランダム性や時間依存がある場合、可能なら次を固定します。

- seed
- input
- timestep / frame count
- configuration
- target scenario

これにより、AI が大量の実行履歴を比較する必要を減らします。

## Visual truth

画面配置、描画、画像、アニメーションなどは、unit test が通っていても視覚的に正しいとは限りません。

視覚的な正しさが Acceptance に含まれる場合は visual confirmation を Completion Gate として明示します。

逆に、視覚確認が不要な変更に毎回スクリーンショットや手動確認を追加しません。

## Shared source of truth

エディタと実行系など複数の入口が同じデータを扱う場合、不透明な中間コピーを増やさず、可能なら共通の正式データ契約を参照します。

これにより AI が「どの表現が最新か」を追加探索するコストを減らします。

## 標準推奨

- 変更種別から必要な検証 evidence をルーティングする
- smallest sufficient validation を先に使う
- ランダム挙動は固定条件 + structured observation を優先する
- 成功ログ全文を保持しない
- visual correctness は必要な変更だけ実画面で確認する
- unit test で確認できない性質を推測で補完しない
- 複数入口が同じデータを扱う場合は source of truth を増やさない
