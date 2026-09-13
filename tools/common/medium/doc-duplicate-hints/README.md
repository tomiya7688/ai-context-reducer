# doc-duplicate-hints

Documentationの重複候補をagentへcompactに返します。

## Development routing

```text
CLI / output           -> script/doc_duplicate_hints.py
document discovery/read -> script/messenger.py
normalization/detection -> script/processing.py
```

重複判定ロジックを変えるときにfilesystem処理を読む必要はありません。文書対象や読込方法を変えるときは `messenger.py` を先に読みます。

この構造はTask Routing / Responsibility Map / Hierarchical Contextをtool開発自身へ適用するためのものです。
