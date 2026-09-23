# Documentation Duplication Control

この文書は、AI向け文書・README・guide・summary等へ同じ規則や説明を何度も複製し、context増加と更新driftを起こすことを防ぐための方針です。

目的は「似た文章をすべて削除すること」ではありません。

> **同じ詳細情報を複数のSource of Truthとして持たず、原典 + 必要最小限のpointer / summaryを優先する。**

可読性のために必要な短い重複と、更新漏れを生む危険な重複を区別します。

## 1. なぜ重複を制御するか

同じ規則・仕様・説明を複数docsへコピーすると、AIが読む量が増えるだけでなく、内容がずれたときにどれを信じるべきか分からなくなります。

~~~text
same rule
  -> README
  -> AI_CONTEXT
  -> setup guide
  -> architecture doc
  -> tool README
~~~

この状態では、1か所の変更で複数fileを同期する必要があります。

重複制御の主目的はcontext削減より先に**情報責務を明確にすること**です。

## 2. Source of Truth + pointer

詳細情報には可能な限り1つの原典を決めます。

~~~text
Source of Truth
  -> full rule / contract / specification

Other documents
  -> short purpose
  -> pointer to Source of Truth
~~~

例:

~~~text
docs/api-contract.md
  -> full API contract

README
  -> API contractの概要 + link

AI_CONTEXT
  -> API変更時に読む場所 + link
~~~

READMEやAI入口へ詳細契約を再掲せず、「いつ・なぜ読むか」を短く残します。

## 3. summary / indexは原典の代替ではない

summary、Context Pack、Context Manifest、手法一覧、AI_CONTEXT等は、必要な原典へ到達するための入口です。

~~~text
summary / index / pointer
  -> locate authoritative source
  -> read original when needed
~~~

summaryだけへ新しい仕様を追加し、正式docやsourceへ反映しない状態を作りません。

要約と原典が矛盾した場合は原典を優先し、要約側を更新または削除します。

## 4. drift riskの高い重複

次のような重複は特にdriftしやすいため避けます。

- normative ruleを複数docsへ全文コピー
- version / supported platform / compatibility表を複数箇所で独立管理
- 同じCLI contractをREADMEと別guideへ詳細再掲
- architecture boundaryを複数fileで別々に説明
- generated outputを手書きdocへ再転記
- current stateをREADME / Issue / AI guideで独立更新

「どこを変えたら他も変える必要があるか」が曖昧な重複は、Source of Truthを決め直すsignalです。

## 5. intentional duplication

すべての重複が悪いわけではありません。

次のような短い重複は、可読性や安全性のために合理的な場合があります。

- 初見ユーザーが迷わない1〜2文の概要
- AI入口に必要な短いinvariant
- safety / destructive operationに関する短い警告
- standalone artifact内で最低限必要な利用条件
- table of contentsやnavigation label
- その場で理解できないと誤操作しやすい短い説明

ただし、intentional duplicationは次を守ります。

- 詳細を複製しない
- 原典へのpointerを残す
- 原典と独立した新しい仕様にしない
- 維持できない量へ増やさない

~~~text
short duplicate for readability
  + authoritative pointer
  != second Source of Truth
~~~

## 6. 可読性とのtradeoff

重複削減をやりすぎると、文書がlinkだけになり、人間にもAIにも読みづらくなることがあります。

悪い例:

~~~text
See A.
See B.
See C.
~~~

何を読むべきか、なぜ必要かが分かりません。

良いpointerは短いcontextを持ちます。

~~~text
API互換性を変更する場合は docs/api-contract.md のversioning節を確認する。
~~~

必要な意味まで削ってnavigation costを増やさないことが重要です。

判断基準:

~~~text
duplicate detail maintenance cost
  vs
local readability / safety benefit
~~~

短い説明で十分なら残し、詳細だけ原典へ寄せます。

## 7. 文書ごとの責務を分ける

同じ情報を複製しないため、文書種別ごとの役割を決めます。

例:

- README: 人間向け概要・導入・入口
- AI_CONTEXT: AI向けrouting・読む順番・重要な短い制約
- Current State: 現在の能力・制約
- detailed docs: specification / design contract
- Issue: task requirement / discussion / priority
- source / tests: implementation / executable truth
- generated artifact: 派生結果

役割が重なる場合は、どちらが原典かを明示します。

## 8. 重複候補を見つけたときの手順

類似または同一の文章を見つけても、機械的に削除しません。

~~~text
duplicate candidate
  -> identify document roles
  -> identify Source of Truth
  -> decide intentional vs drift risk
  -> replace detail with short pointer if useful
  -> verify no required meaning was lost
~~~

確認すること:

1. 両方が同じ意味を意図しているか
2. 片方がsummary / example / warningではないか
3. どちらがauthoritativeか
4. standaloneで読む必要がある文書か
5. 削除で利用者が原典へ到達できなくならないか
6. wording差が本当にdriftなのか、scope差なのか

## 9. 自動削除しない

duplicate detectionの結果だけで文書を削除・統合・書き換えません。

似た文章でも、次の可能性があります。

- scopeが異なる
- 同じ用語を定義しているだけ
- safety warningを意図的に再掲している
- templateやgenerated fileである
- exampleとして必要
- standalone distributionに必要

そのため、自動化は**candidate detectionとpointer提示まで**を基本にします。

applyは人間またはtaskを担当するagentが文書責務を確認してから行います。

## 10. 同期が必要な重複

どうしても同じ内容を複数artifactへ含める必要がある場合は、可能なら手書き同期より生成を検討します。

~~~text
canonical data
  -> generated copies
~~~

ただし、生成仕組みの維持costが高い小規模文書では無理に自動化しません。

生成物もSource of Truthにはせず、canonical inputを明示します。

## 11. Small repoでの扱い

docsが少なく、同じ情報のdriftが問題になっていないprojectでは専用のduplicate scanは不要です。

最低限、次だけで十分です。

- 詳細仕様の原典を決める
- 他文書は必要な短い説明 + pointerにする
- 同じ規則を増やす前に既存原典を確認する

## 12. 補助実装

このrepositoryには tools/common/medium/doc-duplicate-hints があります。

このtoolはdocumentation内の同一・類似候補をcompactに示す**hint tool**です。

- duplicate candidateを見つけるだけ
- どちらが正しいか決めない
- intentional duplicationかdrift riskか決めない
- fileを自動削除しない
- textを自動統合しない
- Source of Truthを自動決定しない

tool outputはreview対象を絞るために使い、最終判断は文書の責務と原典を確認して行います。

## 13. 標準推奨

- 同じ詳細規則・仕様を複数のSource of Truthへしない
- Source of Truth + short pointerを優先する
- summary / indexを原典の代替にしない
- readability / safetyに必要な短いintentional duplicationは許容する
- intentional duplicationにも原典pointerを残す
- 類似文章を機械的に削除しない
- duplicate candidateごとに文書責務とscopeを確認する
- standalone artifactに必要な情報を無理に削らない
- 同期必須の複製は必要ならcanonical dataから生成する
- doc-duplicate-hintsを自動cleanup toolとして使わない
