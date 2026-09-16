# repo-stats

Repositoryのlanguage / line statisticsをcompactなself-describing JSONで返します。

PATH上に `scc` が既にあればaggregate JSONを再利用し、無ければPython / native Goのportable implementationで集計します。外部toolを自動installしません。

## Use

Python:

```sh
python tools/common/small/repo-stats/script/repo_stats.py .
python tools/common/small/repo-stats/script/repo_stats.py --backend portable .
```

Native:

```sh
acr-toolbox stats .
acr-toolbox stats --backend portable .
```

Go標準flag parserを使うnative版ではoptionをpositional pathより前へ置きます。

通常は `--backend auto` のままで構いません。

- sccが利用可能: language aggregateをsccで取得
- sccが無い: portable backendで正常終了
- 見つかったsccが失敗: portableへfallbackし、その事実だけをJSONへ記録
- `--backend scc`: external backendを必須にしたい検証用

## Output

stdoutはJSONだけです。Python/nativeとも次の意味を共有します。

- `tool`: `repo-stats`
- `status`
- `project_root`
- `backend`: `scc` / `portable`
- `recognized_files_seen`
- `analyzed_file_count`
- `analyzed_line_count`
- `oversized_file_count`
- `read_error_count` / `walk_error_count`
- `binary_like_file_count`
- `max_file_bytes`
- `languages.<name>`
  - `file_count`
  - `line_count`
  - `byte_count`
  - `code_count`
  - `comment_count`
  - `blank_count`
  - `complexity`

portable backendで算出しないcode/comment/blank/complexityは `null` です。sccのper-file detailはagent contextへ流さずaggregateだけを保持します。

## Limits

`--max-file-bytes 0` が既定で、内部解析はfile sizeによるsilent capを持ちません。明示的なpositive valueだけをperformance/safety capとして使い、その場合はsccではなくportable backendを使います。

Generated / dependency / cache directoryは通常対象から外します。

## Development routing

```text
Python implementation / scc adapter -> script/repo_stats.py
Python contract tests               -> tests/test_repo_stats.py
Native implementation / scc adapter -> tools/common/native/acr-toolbox/stats_command.go
Native contract tests               -> stats_command_test.go
```

Nativeではstatsを `browse_commands.go` から分離し、statistics/backend変更時にtree/doc-index implementationを読む必要をなくしています。
