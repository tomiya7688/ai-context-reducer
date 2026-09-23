# Validation Routing

変更内容に応じて、必要な検証手段だけを選ぶ方針です。

重要なのは、変更の性質ごとに必要な evidence を明示し、最小十分な検証から始めることです。

## 目的

すべての変更に対して同じ検証を大量実行したり、逆に unit test だけで十分だと決めつけたりせず、変更の性質に合った証拠を選びます。

```text
Change type
  -> required evidence
  -> smallest sufficient validation
  -> evidence validity check
  -> additional evidence only if needed
```

## Evidence types

代表的な検証手段:

- static / syntax check
- targeted unit / regression test
- deterministic runtime / smoke test
- structured evaluation log
- generated-data consistency check
- distribution / packaged-artifact smoke test
- visual / interactive confirmation
- performance measurement

すべてを常に実行する必要はありません。

syntax / parser healthは、既存parserが利用可能ならfull build/testより先に使えるcheap evidenceです。ただしsyntax successはsemantic correctnessやtask completionを意味しないため、その後のtargeted tests / compiler / runtime validationを変更内容に応じて選びます。parserをこの目的だけで自動installしません。詳細は [`Syntax Health Validation`](syntax-health-validation.md) を参照してください。

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

配布・パッケージ変更
  -> build artifact + launch / required-files / initialization smoke

性能変更
  -> correctness tests + comparable measurement conditions
```

テスト成功だけでは確認できない性質を、テスト結果から推測して済ませないことを推奨します。

## Change Impact / Test Impact Routing

変更種別からevidence typeを選んだ後、test suiteが大きいrepoでは **changed file / symbol / packageから実行範囲を絞る** ことができます。

```text
changed files / symbols
        ↓
responsibility / dependency / ownership information
        ↓
likely affected tests
        ↓
smallest sufficient validation
        ↓
shared/public/unknown impactなら broader fallback
```

利用候補:

- source ↔ test の命名対応
- explicit mapping table
- Responsibility / Change Routing Map
- import / dependency relation
- changed-symbol routing
- 既存coverage data（補助信号）

専用coverage SaaSや巨大dependency graphは必須ではありません。

安全側fallbackを必ず持ちます。

- shared/core変更 -> subsystem-wide / broader tests
- public API / schema / config contract変更 -> producer + consumer / compatibility tests
- build/package変更 -> artifact-level validation
- dependency relation不明 -> subsystem/full tests または `Unverified`
- impact selectionの確信が低い -> broader validation

詳細は [`change-impact-routing.md`](change-impact-routing.md) を参照してください。

## Evidence validity

検証コマンドが終了コード 0 でも、実際に対象を検査していなければ十分な evidence ではありません。

例:

- `0 tests` を機能検証成功として扱わない
- 対象外パスだけを走査した checker を成功根拠にしない
- build が成功しても、配布物に必要ファイルが入っているとは推測しない
- smoke test が対象機能へ到達しているか確認する

Context Pack には、可能なら「何件・何対象を検証したか」を短く残します。大量のログ全文は不要です。

## Headless first

GUI / interactive application でも、まず GUI を起動せず確認できるロジック・保存形式・CLI・生成物を自動検証します。

```text
headless checks
  -> sufficientなら終了
  -> visual / interactive acceptance がある場合だけ GUI confirmation
```

GUI起動は重い実行ログ、画像、手動操作など追加コンテキストを生みやすいため、必要な変更だけに限定します。

ただし UI / visual correctness 自体が Acceptance の場合は headless 結果だけで完了扱いにしません。

## Disposable validation workspace

保存・変換・export・初期化など、ファイル生成を伴う検証は可能なら temporary directory / disposable workspace 内で行います。

これにより:

- 作業ツリーへ検証用ファイルを残さない
- generated file を通常差分へ混ぜない
- 毎回同じ初期状態から再現しやすくする
- AI が無関係な生成物を changed files として読むことを防ぐ

検証用成果物を長期保存する必要がある場合だけ明示的な保存先へ移します。

## Generated / distribution artifact boundary

最終成果物が source tree と異なる場合、source 側の検証だけで完了としないことがあります。

```text
source validation
  -> artifact generation
  -> artifact smoke
```

たとえば配布ビルドでは、生成後の実行物そのものに対して次を確認できます。

- 起動できる
- 必須ファイルが存在する
- 初期設定・UserData 等を正常に作成できる
- 開発環境固有の絶対パスや未同梱依存へ依存していない

これにより AI が packaging 実装全体を推測でレビューする代わりに、成果物境界で直接 evidence を取れます。

Generated artifactは通常contextでは除外候補ですが、artifact自体がAcceptance evidenceになるtaskでは一時的にvalidation対象へ戻します。Source of Truthまで除外せず、検証後もartifact全文を通常contextへ常駐させません。詳細は [`Context Exclusion`](context-exclusion.md) を参照してください。

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
- test suiteが大きい場合はchange/test impact routingで実行範囲を絞る
- impactがshared/public/unknownならbroader fallbackする
- smallest sufficient validation を先に使う
- syntax healthは利用可能な場合のcheap evidenceとして使い、syntax successだけでcompletion判定しない
- GUI / interactive validation は必要な変更だけに限定し、可能なら headless checks を先に使う
- ファイル生成を伴う検証は disposable workspace を優先する
- evidence が実際に対象を検査したか確認する
- `0 tests` や空検査を成功根拠にしない
- source と成果物が異なる場合は必要に応じて生成成果物を直接 smoke test する
- ランダム挙動は固定条件 + structured observation を優先する
- 成功ログ全文を保持しない
- visual correctness は必要な変更だけ実画面で確認する
- unit test で確認できない性質を推測で補完しない
- 複数入口が同じデータを扱う場合は source of truth を増やさない
