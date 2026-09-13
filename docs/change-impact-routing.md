# Change Impact / Test Impact Routing

変更したfile / symbol / packageから、必要な検証範囲を絞るための方針です。

> 最小テストを選ぶこと自体を目的にせず、必要な検証を落とさない範囲で full suite と巨大ログを避ける。

Test Impact Analysis / affected tests selection の既存考え方を、特定CI製品やcoverage製品へ依存しない軽量なroutingとして扱います。

## 基本フロー

```text
changed files / symbols
        ↓
responsibility / dependency / ownership information
        ↓
likely affected tests
        ↓
smallest sufficient validation
        ↓
impact uncertainty / shared contract check
        ↓
必要なら broader / full validation
```

`Validation Routing` が「変更の性質から evidence type を選ぶ」のに対し、この手法は **そのevidenceをどのtest範囲へ適用するか** を扱います。

## Level 1: Static / Explicit Mapping

最も低コストです。

例:

```text
src/parser/*      -> tests/parser/*
src/save/*        -> tests/save/*
apps/editor/*     -> tests/editor/*
package metadata  -> build + artifact smoke
```

sourceとtestの命名規則、directory構造、既存routing tableを利用します。

小〜中規模repoでは、これだけで十分なことがあります。

### 利用候補

- source ↔ test naming convention
- Change Routing Map
- Responsibility Map
- package / module ownership
- explicit test command table

## Level 2: Dependency / Symbol Based

静的mappingだけでは曖昧な場合、import / call / dependency / public contract情報を利用します。

例:

```text
changed symbol
  -> direct consumers
  -> tests covering those consumers
```

ただし巨大な完全call graphを必須にしません。既存のSource Structure Indexや言語標準toolで十分ならそれを利用します。

### bounded traversal

影響探索は無制限に広げません。

- direct consumerを優先
- public/shared contractならbroader validationへ切り替える
- traversal上限を超えたら「影響が広い」と判断し、full/subsystem suiteへfallbackする

## Level 3: Coverage-assisted

既に信頼できるcoverageデータがある場合は補助信号として利用できます。

```text
changed line / symbol
  -> tests that previously executed it
  -> targeted test candidates
```

ただしcoverageは「通った経路」を示すだけであり、未計測pathや間接影響を保証しません。

したがって:

- coverageを唯一の判定根拠にしない
- public contract / shared core変更ではbroader fallbackを残す
- coverage取得自体が高コストなら無理に導入しない

専用CI SaaSや独自coverage engineは必須ではありません。

## Fallback rules

影響分析はfalse negativeが最も危険です。

次のような変更では、targeted testだけで完了しない方を既定にします。

### Shared / Core

- 共通library
- shared utility
- cross-package abstraction
- central parser / serializer
- authentication / persistence等の横断基盤

→ subsystem-wideまたはbroader tests

### Public Contract / Schema

- public API
- DTO / schema
- config format
- protocol / wire format
- plugin interface

→ producer + consumer tests、必要ならintegration / compatibility test

### Build / Package / Distribution

- dependency metadata
- build scripts
- packaging config
- generated manifest

→ source testsに加えてartifact-level validation

### Unknown Dependency

- dependency relationが取れない
- dynamic import / reflection / code generationが強い
- test mappingの信頼度が低い

→ subsystem/full tests または `Unverified` を明示

## Confidenceを使う場合

厳密な数値scoreは不要です。

例:

```text
high:
  direct file-to-test mappingがある

medium:
  dependency relationから候補を推定した

low:
  dynamic behaviorが多く影響範囲が不明
```

`low` なら broader validationへ倒します。

## file -> test 例

```text
changed:
  src/data/save.py

route:
  tests/data/test_save.py
  tests/data/test_load_roundtrip.py
```

同時に `src/data/schema.py` も変更されていれば、schema consumerを含むbroader data testsへ拡張します。

## symbol -> test 例

```text
changed:
  Parser.parse_config

route:
  symbol references
    -> ConfigLoader
    -> ProjectLoader

likely tests:
  test_parser.py
  test_config_loader.py
  test_project_loader.py
```

reference探索が大きくなりすぎる場合は、package test suiteへ切り替えます。

## package -> test 例

```text
changed:
  packages/core/*

route:
  core unit tests
  direct downstream integration tests
```

coreがpublic APIを変更した場合は、downstream package全体またはconformance testsへ広げます。

## Validation escalation

最初のtargeted validationが失敗した場合、無関係なfull suiteへ即座に広げるのではなく、失敗原因に沿って範囲を拡張します。

```text
targeted failure
  -> direct dependency tests
  -> subsystem tests
  -> full suite if impact is broad / unclear
```

逆にtargeted testが成功しても、fallback条件に該当するならbroader validationを省略しません。

## Context削減との関係

目的はtest実行時間だけではありません。

- 不要なtest logをAIへ渡さない
- failure候補を狭く保つ
- unrelated flaky testを現在taskへ混ぜない
- full suite実行理由を明確にする

成功時は「何を何件検証したか」を短く残し、ログ全文は保持しません。

## 導入するとよい兆候

- test suiteが大きい / 遅い
- monorepo / multiple packages
- sourceとtestsの対応がある程度安定している
- 同じ小変更でも毎回full suiteを実行している
- CIログが大きくAI contextを消費する
- changed-symbol routingやdependency情報が既にある

## 導入不要な場合

- test suiteが十分小さくfull runが安価
- sourceとtestsの対応が単純で迷わない
- impact mappingの保守コストが削減効果を上回る

小規模repoへ専用impact analyzerを追加する必要はありません。

## 完了報告の最小形式

```text
Validation:
- targeted: tests/save (18 passed)
- broader: data package tests (42 passed; schema changed)
- artifact: not required
- unverified: none
```

なぜbroader validationを追加/省略したかを1行で説明できれば十分です。

## 原則

```text
correctness / false-negative avoidance
    > minimal test count
    > log reduction
```

影響範囲に確信がない場合、削減率より安全側fallbackを優先します。
