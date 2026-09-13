# Evidence Budget / Context Budget

AIが「念のため」で検索・readを広げ続けることを防ぐため、現在taskで必要な証拠カテゴリを先に決める補助手法です。

これはtoken数を厳密に数える仕組みではありません。

> 追加探索を行う前に「そのread/searchが何の不足を埋めるか」を説明できる状態にする。

Exploration Controlの停止条件を、実運用で判定しやすくするための **bounded evidence collection** です。

## 基本原則

タスク開始時、必要なら次のように証拠を分けます。

```text
Required evidence:
- current task / issue requirements
- target implementation
- matching tests
- authoritative design / policy source

Optional evidence:
- adjacent modules
- history
- broad documentation
- unrelated integration details
```

Required evidenceが揃い、矛盾がなく、Acceptanceを判断できるなら探索停止を優先します。

## 数値token budgetではない

この手法の目的は、例えば「最大8000 tokensまで読む」と固定することではありません。

厳密なtoken上限は:

- modelごとに異なる
- task complexityを反映しにくい
- 正確性よりhard capを優先する危険がある

ため、標準必須にしません。

代わりに **証拠カテゴリと追加探索条件** を管理します。

## 追加探索を許可する条件

新しいread / search / fetchは、原則として次のどれかを満たす場合に行います。

1. Required evidence の欠落を埋める
2. 既存証拠どうしの矛盾を解消する
3. Acceptance / validation判断に必要
4. 実装中に新しい依存・影響範囲が判明した
5. failure原因の特定に必要
6. security / compatibility等の重要条件で未確認領域が残る

どれにも該当しない「念のため」の横展開は止めます。

## Required / Optional evidence

### Required

このtaskを正確に実装・検証するために欠かせないものです。

例:

- Goal / Required / Acceptance
- target source
- matching regression tests
- current interface / schema
- applicable architecture policy
- changed diff

### Optional

役立つ可能性はあるが、現在taskの判断に必須ではないものです。

例:

- commit history
- neighboring subsystem docs
- broad architecture overview
- historical design discussion
- unrelated issues

Optional evidenceは、Required側で疑問が生じた時だけ昇格させます。

## Evidence Ledger

複雑なtaskだけ、短い一時メモを持てます。

```text
Known:
- implementation: src/foo.py
- tests: tests/test_foo.py
- policy: docs/foo-policy.md

Missing:
- error contract for FooError

Unverified:
- Windows packaging
```

長い要約は作りません。pointer / file / symbol / Issue ID中心にします。

### Known

確認済みで、現在判断の根拠になっている原典へのpointerです。

### Missing

Required evidenceのうち、まだ不足しているものです。

`Missing: none` になったら、追加探索を止められない理由が本当にあるか再確認します。

### Unverified

現在taskの完了を必ずしも妨げないが、確認していない範囲です。

全repoを読んでUnverifiedをゼロにする必要はありません。

## Stop conditionとの接続

Exploration Controlの停止条件:

- Goal understood
- Required known
- Acceptance known
- Working set identified
- Deferred scope known

に加え、Evidence Budgetを使うtaskでは次を確認します。

```text
Required evidence missing: none
Evidence conflicts: none / resolved
Acceptance evidence: sufficient
Unverified areas: explicit
```

ここまで揃えば実装・検証へ進みます。

## 再探索のトリガー

一度探索を止めても、実装中に新しい事実が出たら再開して構いません。

例:

- target functionがshared public APIだった
- test failureで別module依存が判明した
- config schema変更がdistribution artifactにも影響した
- design docとsourceが矛盾していた

この場合も、発生した不明点に必要な範囲だけ追加取得します。

```text
new unknown
  -> one evidence gap
  -> targeted search/read
  -> gap resolved
  -> stop again
```

## Evidence escalation

最初から最大範囲を読みません。

```text
current source + matching tests
        ↓ insufficient
one direct dependency / authoritative doc
        ↓ insufficient
subsystem context
        ↓ only if still required
broader repo/history
```

探索範囲を広げるたびに理由を持ちます。

## Context Packとの関係

Context Packは成果物として巨大な調査ノートにしません。

Evidence Ledgerを残す場合も、次程度で十分です。

```text
Evidence
- Known: src/foo.py, tests/test_foo.py, docs/foo.md
- Missing: none
- Unverified: macOS packaging
```

原典全文をContext Packへコピーしないでください。

## Search result / summaryの扱い

検索結果・要約・structure indexは、Required evidenceの原典そのものではない場合があります。

```text
index/search
  -> candidate selection
  -> authoritative source/test/doc
```

重要な判断は必要に応じて原典へ戻ります。

## 例: 小さいbug fix

```text
Required:
- issue reproduction
- target function
- matching regression test

Optional:
- module history
- sibling modules
- full architecture docs
```

3つが揃えば履歴や全architecture docを読まずに実装へ進めます。

## 例: schema変更

```text
Required:
- schema source
- producer
- direct consumers
- compatibility tests
- migration / versioning policy

Optional:
- unrelated package docs
```

consumer影響が広いと判明した場合だけEvidence Budgetを拡張します。

## 例: package build failure

```text
Required:
- build metadata
- failing command/error excerpt
- generated artifact contents
- artifact smoke requirement

Optional:
- application runtime internals
```

runtime internalsを先に広く読むより、artifact boundaryの証拠を優先します。

## 導入するとよい兆候

- coding taskなのに探索が長い
- AIが同じ周辺fileを何度も読む
- history / broad docsへ横展開しやすい
- Context Packが調査ノート化している
- 「念のためfull repo inspection」が頻発する
- required evidenceが揃っているのに検索が続く

## 導入不要な場合

小さいtaskでは形式的なledgerを作る必要はありません。

例えばtarget fileとtestが明白な1行修正なら、通常の探索停止ルールだけで十分です。

Evidence Budget自体が追加コンテキストにならないようにします。

## Safety

Evidence Budgetは正確性を犠牲にするhard capではありません。

- security上重要な不明点
- public contractの影響
- migration / data loss risk
- user-requested comprehensive review

などでは、必要な証拠が増えることを許容します。

```text
correctness
    > evidence completeness for the task
    > context reduction
```

## 最小ルール

Evidence Budgetを正式導入しなくても、次の1問だけで効果があります。

> 次のread/searchは、どの不足・矛盾・Acceptance確認のために必要か？

答えられなければ探索停止を優先します。
