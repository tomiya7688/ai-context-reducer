# Boilerplate Generation / Canonical Templates

定型文・通知文・ライセンス案内・ヘッダー・設定断片など、内容の大部分が毎回同じ文書は、AI に全文を毎回生成・比較させず、canonical template と少数の変数から生成することを推奨します。

重要なのは、繰り返し使う文章や設定を毎回生成し直すのではなく、原典となる template と変更可能な入力値を分離することです。

## 目的

```text
canonical template
  + project-specific variables
  ↓
generated artifact
  ↓
AI は変数・差分・検証結果だけ確認
```

定型文の全文を毎回 AI が書き直すと、コンテキスト消費だけでなく、表現ゆれ・項目欠落・意図しない文面変更が発生しやすくなります。

## Canonical source

生成物とは別に、原典となる template / policy / clause set を持ちます。

例:

- license template
- copyright notice
- attribution block
- generated README section
- release notice
- configuration header
- standard disclaimer

生成物を source of truth にせず、template と入力値へ戻れる構造を保ちます。

## Variable-first context

AI に渡す情報は可能なら全文ではなく、変更可能部分を中心にします。

例:

```text
Template: character-license-v1
Name: Example Character
Version: 1.2
Repository: owner/repo
Credit required: no
Redistribution: allowed with conditions
```

template 自体に変更がない場合、生成済み全文を通常コンテキストへ含める必要はありません。

## Versioned template

法務・規約・公開文書など意味の変更が重要な定型文は、template version を明示します。

生成時には少なくとも次を追跡できることを推奨します。

- template identifier
- template version
- input variables
- output path
- generated / checked status

必要なら hash や commit reference を使って、どの原典から生成されたか確認できるようにします。

## Generated artifact validation

生成コマンドが成功しただけで正しいとは限りません。

最低限、用途に応じて次を確認します。

- 必須変数が空でない
- placeholder が残っていない
- expected sections が存在する
- output encoding / line ending
- generated artifact が current template と一致する

法的妥当性やプロジェクトへの適合性は、生成ツールだけでは保証できません。ツールは既に採用された template を一貫して展開するための補助として扱います。

## Context reduction rule

通常作業では generated boilerplate を全文読ませません。

```text
current template version
+ changed variables
+ generated diff / validation result
```

を先に使い、template 本文や生成物全文は template 自体を変更する場合、法的・契約上の判断が必要な場合、生成差分に異常がある場合だけ読みます。

## 将来の共通ツール候補

`tools/<tool-name>/script/` 配下へ、共通 generator を追加できます。

例:

```text
tools/boilerplate-generator/script/
```

候補機能:

- template 一覧
- variables file / CLI input
- preview / dry-run
- output generation
- unresolved placeholder check
- template version / source metadata
- generated diff
- check-only mode

ライセンス生成を扱う場合も、ツールが独自に法的条件を設計するのではなく、承認済み template を選択・展開する方式を基本とします。

## 既存ツールの利用

外部ツールでは **Copier** が有力です。Jinja2ベースのtemplateと変数からproject scaffoldを生成できるだけでなく、template自体が更新された後に既存projectへ更新を適用するlifecycle managementも主目的としているため、単発生成より長期運用が必要なcanonical templateと相性があります。

単純な初期scaffoldだけで十分なら Cookiecutter 等の既存template generatorも候補です。重要なのは製品名ではなく、既存ツールで `template + variables -> generated artifact` が十分実現できるなら、自前generatorを追加しないことです。

特にproject skeleton、CI設定、共通README、設定ファイル群などはCopier等へ任せ、AI Context Reducer側は「生成物全文ではなくtemplate version・入力差分・validation結果を見る」というcontext運用に集中できます。

## 標準推奨

- 定型文は canonical template + variables へ分離する
- generated artifact を source of truth にしない
- AI には全文より changed variables / generated diff を優先して渡す
- template version と生成元を追跡可能にする
- placeholder / required section など機械検査できる項目は generator 側で確認する
- 法的内容の妥当性そのものを generator の責務にしない
- 成熟したtemplate generatorで十分なら自前generatorより再利用を優先する
- 共通 generator を作る場合も特定ライセンスや外部リポジトリへの必須依存を避ける
