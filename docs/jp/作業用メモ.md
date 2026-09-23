# Context Pack

Context Pack は、AI が現在タスクを進めるために必要な情報だけをまとめた一時パケットです。

固定された巨大文書ではなく、原典から必要部分だけ再構築します。

## 最小構成

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

標準テンプレートは `templates/CONTEXT_PACK.md` を参照してください。

## 最優先項目

Task では最初に次を揃えます。

- Goal
- Required
- Acceptance

さらに対象source / tests と Out of Scope が分かれば、探索停止条件として使えます。

## Working Set

可能なら changed files だけでなく changed symbols まで絞ります。

読む順序は原則として次です。

```text
target source
  -> matching tests
  -> direct dependencies
  -> detailed docs only if needed
```

## Validation

すべての検証項目を埋める必要はありません。

変更種別に応じて smallest sufficient evidence を選び、未確認領域は `Unverified areas` として明示します。

`0 tests`、空走査、対象外のみの検査は成功根拠にしません。

## Optional Extensions

必要な場合だけ追加します。

- Current State reference
- Remote Delta
- Policy Context / active exception
- Relevant Architecture
- headless / deterministic / visual validation
- disposable workspace
- structured runtime observation
- artifact validation
- performance measurement
- Source Excerpts

プロジェクト固有の項目も、Coreを壊さない範囲で追加できます。

## Split Packet

長くなる場合は1ファイルへ詰め込まず、再生成可能な小さい構成要素へ分離できます。

```text
task.md
files.txt
symbols.txt
constraints.md
diff.patch
```

名前や配置は標準ではありません。

## Source of Truth ではない

Context Pack は作業用スナップショットです。

長期保存する設計判断・仕様・未完了作業は、正式な docs、Issue、source、tests 等へ反映します。

古い Context Pack を何世代も継ぎ足したり、再要約して原典から離れたりしません。

## 判断原則

Context Pack 自体が大きくなった場合は、まず情報を追加するのではなく削れる項目を確認します。

```text
current task に必要か?
  yes -> keep
  no  -> omit / reference only
```

正確性を保ったまま、今回の判断に必要な情報だけを入れることを優先します。
