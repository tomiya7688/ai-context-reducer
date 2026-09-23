# context-manifest

Repository filesをagent向けpriority manifestへ圧縮します。manifestはrouting hintであり、原典ファイルの代替ではありません。手法そのものは [`docs/jp/参照先の目録.md`](../../../../docs/jp/参照先の目録.md) を参照してください。

## Usage

Python:

```sh
python script/context_manifest.py . --limit 400
```

Native:

```sh
acr-toolbox context-manifest --limit 400 .
```

既定ではrepository全体をscanし、agentへ返す `files` だけを `--limit` でboundedにします。`--limit 0` はscanを省略する指定ではなく、full scanした上でfile rowsを返さない指定です。

## Output contract

自己説明的JSONだけをstdoutへ返します。

主なfield:

```text
tool
status
root_path
total_files
returned_files
stat_error_count
walk_error_count
files_truncated
files[]
```

各fileは `context_priority / path / bytes` を持ちます。priorityは `P0..P4` のrouting hintです。

`input_missing` / `input_not_directory` / `input_read_failed` と成功した空repositoryを混同しません。scan途中のerrorは `ok_with_warnings` とcountで示します。

## Priority

```text
P0: README / AI_CONTEXT / AGENTS / CLAUDE / primary package manifests
P1: source files
P2: tests
P3: docs
P4: other files
```

priorityは設計良否や重要度の絶対評価ではなく、最初に読む候補を絞るrouting順です。

## Development routing

変更内容から最初に読むfileを限定します。

```text
Python CLI / JSON output      -> script/context_manifest.py
Python filesystem collection -> script/messenger.py
Python priority rules         -> script/processing.py
Python contract validation    -> tests/test_processing.py
Native command / priority     -> tools/common/native/acr-toolbox/context_manifest_command.go
Native validation             -> tools/common/native/acr-toolbox/context_generation_commands_test.go
```

priority rule変更でfilesystem traversalを読む必要はありません。収集対象変更でpriority logicを読む必要もありません。

## Context Reducer self-application

- Responsibility Map: collectionとpriority classificationを分離
- Task Routing: 変更理由から対象fileへ直接進む
- Hierarchical Context: このREADME -> 対象moduleの順に読む
- Exploration Stop: target moduleと入出力契約が分かれば他module探索を止める
- Source of Truth: priority規則は `processing.py` / native command、収集規則は `messenger.py` / native repository walker
