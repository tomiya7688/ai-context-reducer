# doc-duplicate-hints

Documentationの重複候補をagentへcompactな自己説明的JSONで返します。これは [`Documentation Duplication Control`](../../../../docs/jp/文書の重複を管理する.md) のhint toolであり、候補を自動削除・自動統合したり、Source of Truthを自動決定したりしません。

## Usage

Python:

```text
python script/doc_duplicate_hints.py --max-groups 80 --max-occurrences-per-group 10 <repo-root>
```

Native:

```text
acr-toolbox doc-duplicate-hints --max-groups 80 --max-occurrences-per-group 10 <repo-root>
```

`--max-groups 0` と `--max-occurrences-per-group 0` はunlimitedです。内部document scanは返却上限で打ち切らず、全duplicate groupを検出してからagent-visible outputだけをboundedにします。

`node_modules` / `vendor` / generated / build output等のdependency・generated directoryは既定で探索対象から外します。missing root、non-directory、read failure、walk failureは成功した0件と区別します。

各groupは重複本文を1回だけ持ち、`occurrence_count_total` とboundedな `occurrences` を返します。同じ本文を各occurrenceへ複製しません。

## Development routing

```text
CLI / output            -> script/doc_duplicate_hints.py
document discovery/read -> script/messenger.py
normalization/detection -> script/processing.py
native CLI / discovery  -> tools/common/native/acr-toolbox/doc_duplicate_command.go
native detection        -> tools/common/native/acr-toolbox/doc_duplicate_detection.go
```

重複判定ロジックを変えるときにfilesystem処理を読む必要はありません。文書対象や読込方法を変えるときはdiscovery側だけを先に読みます。

この構造はTask Routing / Responsibility Map / Hierarchical Contextをtool開発自身へ適用するためのものです。

## Validation

```text
python -m unittest discover -s tests
cd ../../native/acr-toolbox && go test ./...
```
