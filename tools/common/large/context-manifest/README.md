# context-manifest

Repository filesをagent向けpriority manifestへ圧縮します。

## Development routing

変更内容から最初に読むfileを限定します。

```text
CLI / JSON output      -> script/context_manifest.py
filesystem collection -> script/messenger.py
priority rules         -> script/processing.py
```

priority rule変更でfilesystem traversalを読む必要はありません。収集対象変更でpriority logicを読む必要もありません。

## Context Reducer self-application

- Responsibility Map: collectionとpriority classificationを分離
- Task Routing: 変更理由から対象fileへ直接進む
- Hierarchical Context: このREADME -> 対象moduleの順に読む
- Exploration Stop: target moduleと入出力契約が分かれば他module探索を止める
- Source of Truth: priority規則は `processing.py`、収集規則は `messenger.py`

manifestはrouting hintであり、原典ファイルの代替ではありません。
