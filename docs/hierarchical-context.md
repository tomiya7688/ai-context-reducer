# Hierarchical Context / Scoped AI Instructions

大規模repo・monorepo・複数アプリ構成では、AI向けの全ルールをroot文書へ集約しません。

> 共通ルールはrootへ、局所ルールは対象subtreeの近くへ置き、現在の作業に最も近い必要な指示だけを追加で読む。

これは特定のAI製品や特定ファイル名の仕様ではなく、**progressive disclosure / nearest relevant instruction** の一般原則です。

## 目的

rootのAI入口を小さく保ちながら、subsystem固有のbuild / test / architecture / ownership情報へ正確に到達できるようにします。

```text
repository-wide guide
        ↓
current task / target subtree
        ↓
nearest relevant local guide
        ↓
target source / tests / docs
```

無関係なsubsystemの規約を毎回コンテキストへ入れないことが目的です。

## Scopeごとの責務

### Root / Repository-wide

root側には、原則としてrepo全体で常に成り立つ情報だけを置きます。

例:

- repository purpose
- Source of Truth
- 全体共通の安全性・互換性ルール
- 全体共通のrouting入口
- local guide が存在する場合の探索方針
- repo全体で共通する最小validation原則

subsystem固有の詳細なbuild command、ローカル設計規約、個別fixture等はrootへ集約しません。

### Subsystem / Local

subsystem側には、そのsubtreeでのみ必要な情報を置きます。

例:

- package / app 固有のbuild・test command
- local architecture constraints
- local ownership / responsibility map
- subsystem固有のSource of Truth
- generated fileの扱い
- local validation / smoke test
- compatibility制約

上位文書の内容をコピーせず、**差分だけ**を書きます。

### Current Task

Issue / Context Pack等のtask情報には、その変更で必要なGoal / Required / Acceptanceだけを置きます。

長期的なsubsystem規約をtask文へ複製しません。

## Nearest Relevant Instruction

作業対象が決まった後、現在のpath / subsystemに適用される最も近い指示を必要な範囲だけ確認します。

概念例:

```text
repo/
  AI_CONTEXT.md          # repo-wide only
  apps/
    editor/
      LOCAL_GUIDE.md     # editor固有
      src/
    server/
      LOCAL_GUIDE.md     # server固有
      src/
```

`apps/editor/src/...` を変更する場合:

1. rootの共通ルールを確認する
2. editor subtreeのlocal guideを確認する
3. server側のlocal guideは読まない

local guideのファイル名は `AGENTS.md`、`CLAUDE.md`、独自名など任意です。利用するagentがネイティブに階層指示を解決できる場合はその機能を利用してよく、できない場合はroot index / routingから明示的に辿ります。

## Precedence

この標準は特定agentの厳密なinstruction precedenceを定義しません。

一般原則として:

- repository-wide invariant はlocal guideから無断で打ち消さない
- local guideはそのscope固有の追加条件を与える
- taskの明示要件は現在作業のAcceptanceを定義する
- 矛盾がある場合は推測で上書きせず、Source of Truthへ戻る

agent固有の優先順位仕様がある場合は、その仕様に従います。

## 重複を避ける

悪い例:

```text
root guide: 300行
editor guide: root 300行をコピー + 20行
server guide: root 300行をコピー + 15行
```

推奨:

```text
root guide: 共通50行
editor guide: editor固有20行
server guide: server固有15行
```

同じ規約を複数scopeへコピーすると、更新漏れ・矛盾・コンテキスト増大を招きます。

## Task Routing / Policy Routingとの関係

### Task Routing

**どこを読むか**を案内します。

### Policy Routing

**どの規約がRequired / Recommended / Advisoryか**を整理します。

### Hierarchical Context

**指示そのものをどのscopeへ配置し、どのscopeだけ読むか**を整理します。

責務を混ぜず、local guideを新しい巨大routing tableにしません。

## 導入するとよい兆候

- monorepo
- 複数app / package / pluginを含む
- subsystemごとにbuild / testが異なる
- subsystemごとに設計規約が異なる
- root AI guideが肥大化している
- 無関係なlocal ruleを毎回AIへ読ませている
- rootから対象subsystemへ到達した後も大量の共通説明が残る

## 導入しない方がよい場合

小規模repoで主要source / tests / docsが少なく、rootの小さいAI入口だけで迷わず作業できる場合は導入不要です。

各directoryへ機械的にlocal guideを作ることはしません。

```text
expected repeated context saving
    > adoption + maintenance cost
```

を満たすscopeだけ追加します。

## Monorepo例

```text
repo/
  AI_CONTEXT.md
  docs/
    architecture.md
  apps/
    desktop/
      AI_CONTEXT.local.md
      src/
      tests/
    web/
      AI_CONTEXT.local.md
      src/
      tests/
  packages/
    core/
      AI_CONTEXT.local.md
      src/
      tests/
```

root:

```text
- Source of Truth
- shared compatibility rules
- task routing
- "target subtreeにlocal guideがあれば読む"
```

`apps/desktop/AI_CONTEXT.local.md`:

```text
- desktop固有build
- desktop固有smoke test
- GUI/headless validation
- desktop固有architecture constraint
```

`packages/core/AI_CONTEXT.local.md`:

```text
- public API compatibility
- core unit tests
- downstream impact時のbroader validation
```

## 最小導入例

root AI入口へ、必要なら次だけ追加します。

```text
## Local Instructions
作業対象のsubtreeにlocal AI guideが存在する場合だけ読む。
上位文書を複製したlocal guideは作らず、そのscope固有の差分だけを記載する。
```

local guideを列挙するrouting mapが既にある場合は、重複して一覧を増やさずそこから辿ります。

## 完了条件

Hierarchical Contextが有効に機能している状態は次です。

- root AI guideがrepository-wide情報に集中している
- subsystem固有情報が必要なscopeの近くにある
- 現在taskと無関係なlocal guideを読まずに済む
- 上位規約のコピーが増えていない
- local guideのSource of Truthが明確
- 特定agentやファイル名へ標準全体が依存していない
