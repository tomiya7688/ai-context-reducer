# Responsibility Map / Policy Check

この文書は、ソース全体を読む前に「各ファイルが何を担当するか」を短い責務表から判断し、機械判定できる規約は compact checker output へ移すための標準方針です。

重要なのは、責務の索引と機械判定可能な規約を分け、現在タスクに関係する実装候補へ短い経路で到達できるようにすることです。

## 1. Responsibility Map

大きなリポジトリでは、ファイル名だけで責務を推測させず、必要に応じて短い責務表を持ちます。

例:

```text
File / module            Responsibility
src/lexer.*              source -> token stream
src/parser.*             token stream -> syntax tree
src/diagnostic.*         diagnostic representation
```

責務は短く書き、helper 関数の一覧にはしません。

AI はこの表を使って、現在タスクに関係するファイル候補を先に絞ります。詳細実装が必要になった場合だけ原典を読みます。

## 2. Responsibility Map as architecture check

責務表は索引だけでなく、構造の肥大化を見つける補助にも使えます。

1レコードを短い1文で説明できず、`A and B and C` のように複数責務を並べる必要が出た場合は、ファイル / class / module が広がりすぎていないか確認します。

これは自動的な分割命令ではありません。責務境界を再確認する signal として扱います。

## 3. Keep the map current

責務表を採用する場合は、次の変更で同じ change set 内の更新を推奨します。

- 新しい主要ファイル / module を追加する
- 責務を別ファイルへ移動する
- ファイルを分割・統合する
- public architecture 上の所有者を変更する

古い責務表は誤ったルーティングを生むため、維持できない場合は正式な routing source として扱いません。

## 4. Mechanical policy checks

coding rules のうち機械判定できるものは、毎回規約全文を AI に読ませる代わりに checker / lint / static analysis へ移せます。

例:

- size threshold
- forbidden placement
- naming pattern
- required documentation
- generated path exclusion

AI へ渡す通常出力は compact にします。

```text
OK policy-check
```

または問題がある場合だけ、

```text
W path:line RULE short message
E path:line RULE short message
NG policy-check: 2
```

のような finding を渡します。

## 5. Do not pretend architecture is fully machine-checkable

責務分離、semantic ownership、設計境界など、機械的に証明しにくい規約まで無理に checker へ押し込みません。

推奨分離:

```text
mechanically decidable rules
  -> checker / lint

architectural / semantic rules
  -> responsibility map + targeted review
```

これにより、誤検知を避けながら規約全文の常時投入を減らします。

## 6. Scoped exceptions

checker に例外機構が必要な場合は、規約そのものを曖昧にするのではなく、path / rule 単位で範囲を明示します。

例:

```text
path generated/**
rule DOC third_party/**
```

例外一覧も巨大化させず、legacy / generated / third-party など理由が明確なものに限定します。

## 7. Context routing with responsibility data

Responsibility Map は Change Routing Map や Source Structure Index と併用できます。

```text
Task / changed area
  -> Responsibility Map
  -> candidate files
  -> changed symbols / structure index
  -> matching tests
  -> source details only if needed
```

ファイル数が小さいプロジェクトでは専用表を作らず、`AI_CONTEXT.md` や既存 architecture doc の短い表で代用して構いません。

## 8. Implementation options

Responsibility Map の表現形式は固定しません。Markdown table、JSON、生成索引、既存architecture metadataなど、現在タスクから責務へ短く到達できれば構いません。

機械判定可能な規則についても、既存lint/static analysisで十分なら専用checkerを増やしません。専用checkerを作る場合は、確定できるfindingだけをcompactに返し、semantic ownershipのような推測を必要とする判断はtargeted reviewへ残します。

## 9. 標準推奨

- 大規模プロジェクトでは短い Responsibility Map を routing source として利用できる
- 責務記述が肥大化したら構造見直しの signal とする
- map を使うなら source 変更と同じ change set で更新する
- 機械判定可能な規約は compact checker output へ移す
- checker 成功時は長いログではなく結果だけを保持する
- architecture / semantic rules を無理に機械判定しない
- 例外は path / rule 単位で明示的に限定する
