# Python Tools Local Context

この文書は `tools/python/` にだけ適用する差分ルールです。共通方針は `tools/AI_CONTEXT.md` を参照してください。

## Read first

対象toolについて次だけ読む。

1. 対象directoryの `README.md` があればそれ
2. 対象 `.py` source
3. `run.sh` / `run.bat` があればそれ
4. fixture / targeted test があればそれ

他のPython toolやGo版は、入出力契約や互換性確認が必要な場合だけ読む。

## Implementation

- buildを要求しない
- 標準ライブラリで十分なら外部packageを追加しない
- 1-fileまたは小さいmodule構成を優先する
- import時に重い全repo scanを開始しない
- CLI実行時もtarget / limit / scopeを指定できる構造を優先する

## Output

- full source / full tree / full logを既定で出さない
- path / symbol / relation / reason等の索引情報を優先する
- `--limit` 等でboundedにできる処理は上限を持つ
- JSON outputは機械処理用、通常textはcompactにする
- parse failureやtruncationを無言で隠さない

## Validation

通常は対象scriptだけを確認する。

```text
python -m py_compile <target.py>
small fixture smoke
```

共通CLI契約やJSON schemaを変えた場合だけ対応するGo版またはconsumerを追加確認する。
