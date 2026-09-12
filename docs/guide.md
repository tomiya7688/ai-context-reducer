# AI Context Reducer - 基本説明書

## 1. 目的

`ai-context-reducer` は、AIが毎回リポジトリ全体を読み直さず、必要な情報へ短い経路で到達するための共通方針です。

優先順位:

```text
正確性 > 作業対象への到達速度 > コンテキスト削減量 > 自動化の多さ
```

## 2. 基本原則

### Search first, read second

検索、索引、changed files、task metadata で候補を絞ってから原典を読みます。

### 要約は索引

要約、Current State、Context Pack、構造索引は source of truth の代替ではありません。必要なら source / tests / docs / diff へ戻ります。

### 探索停止条件

次が実装可能な粒度で揃ったら広い探索を止めます。

- Goal
- Required constraints
- Acceptance
- Working set

実装・検証中に具体的な不明点が出た場合だけ探索を再開します。

### unrelated work を混ぜない

現在タスクと無関係な refactor、legacy cleanup、将来作業を混ぜません。

## 3. 情報源の役割

```text
README -> 人間向け概要
AI_CONTEXT / agent guide -> AI向けrouting/index
Current State -> 現在の能力・制約
Detailed docs -> contracts / specification
Issues / tasks -> requirement / priority
Source / tests -> implementation / executable truth
Generated artifacts -> 必要な場合だけ参照
```

同じ詳細を複数箇所へコピーしないことを推奨します。

## 4. 最小コア

ほぼ全プロジェクトで使うのは次です。

- 小さいAI入口
- Search first, read second
- Source of Truth
- exploration stop condition
- targeted validation
- Unverified areas
- generated output / logs / history の通常除外

小規模repoではこれだけで終了して構いません。

## 5. 条件付きで追加するもの

必要な場合だけ追加します。

- Current State
- Task Routing
- Change Routing Map
- Responsibility Map
- Remote Delta First
- Source Structure Index
- changed-symbol routing
- Validation Routing
- Policy Routing / compact checker
- headless-first validation
- disposable validation workspace
- deterministic seam
- artifact validation
- Boilerplate Generation

導入優先度と対象プロジェクトの目安は [`adoption-priority.md`](adoption-priority.md) を参照してください。

## 6. Context Pack

現在タスク用の一時パケットです。

最小構成:

```text
Task
Out of Scope
Working Set
Required Constraints
Routed References
Validation
Change Summary
Exploration Status
```

長くなる場合は小ファイルへ分割して構いません。Context Pack 自体を長期の source of truth にしません。

## 7. Validation

変更種別から必要な evidence を選びます。

```text
change type -> smallest sufficient validation -> evidence validity check
```

例:

- pure logic -> targeted tests
- GUI / editor -> headless checks + 必要なら visual confirmation
- random / time dependent -> fixed input / deterministic seam
- packaged app -> artifact smoke
- export / conversion -> disposable workspace
- rule-heavy code -> compact policy checker

`0 tests` や空走査のように、対象を実際に確認していない成功は evidence として扱いません。

## 8. 大規模repo

対象箇所へ毎回広い探索が必要なら、Responsibility Map、Task / Change Routing、Current State を優先します。

さらに大きい場合だけ Source Structure Index、changed-symbol routing、split Context Pack を追加します。

複数AI・複数チャット・複数人が同じremoteを更新する場合は、規模に関係なく Remote Delta First を優先します。

## 9. AIによる自動導入

```text
README + adoption-priority + AI_CONTEXT template
        ↓
target repo shallow inspection
        ↓
project signals classification
        ↓
Core を導入
        ↓
効果が高い Optional だけ追加
        ↓
Adopted / Skipped / Why を報告
```

最初から全source・全docs・全Issuesを読みません。

## 10. 避けること

- repo全体の常時走査
- 巨大な単一AI文書
- 要約の再要約を何世代も続けること
- AI専用ファイルの大量追加
- 小規模repoへの過剰なrouting/index
- 効果を説明できない自動化
- unrelated refactor
- 未確認領域の推測補完

## 11. 導入判断

追加手法は次を満たす場合だけ使います。

```text
expected repeated context saving > adoption + maintenance cost
```

`ai-context-reducer` 自体も Core を小さく保ち、Optional を条件付きで追加できる構造を維持します。
