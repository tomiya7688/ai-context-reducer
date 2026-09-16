# path-find

Repository内のpath候補をagentへcompactに返すfinderです。既に `fd` が使える場合は外部backendを利用し、無い環境ではstdlib / native fallbackで動作します。外部toolを自動installしません。

## Use

Python:

```sh
python tools/common/small/path-find/script/path_find.py '*.py' src
python tools/common/small/path-find/script/path_find.py --type dir '*test*' .
```

Native:

```sh
acr-toolbox find '*.py' src
acr-toolbox find --type dir '*test*' .
```

Go標準flag parserを使うnative版ではoptionをpositional argumentより前へ置きます。

通常は `--backend` を指定しません。`auto` が既定で、compatibleなqueryなら `fd`、それ以外は `portable` を使います。明示的な検証時だけ `--backend portable` / `--backend fd` を使います。

## Output

stdoutはself-describing JSONだけです。

- `tool`: `path-find`
- `status`: `ok`, `partial`, input/backend error等
- `root_path`: 実際に探索したscope
- `query`: pattern / type / max depth
- `backend`: `fd` または `portable`
- `results[]`: `path / kind`
- `results_truncated`: agent-visible result上限で未返却候補があるか
- `scan_truncated`: 明示的なportable scan safety capで探索自体が不完全か
- `walk_error_count`: filesystem warning数
- `backend_fallback`: auto external backendが失敗しportableへ戻った場合だけ存在

成功した0件と入力/scan failureを区別します。

## Limits

- `--max-results 0`: output unlimited
- `--max-depth 0`: traversal depth unlimited
- `--max-visited 0`: portable internal scan unlimited

以前の既定 `max-depth=20 / max-visited=20000` は深いrepositoryでrouting候補を黙って落とすため廃止しました。performance/safety capが必要な場合だけ明示します。

Generated / dependency / cache directoryは既定でpruneします。

## Development routing

```text
Python CLI + portable/fd boundary -> script/path_find.py
Python contract tests             -> tests/test_path_find.py
Native finder implementation      -> tools/common/native/acr-toolbox/find_command.go
Native contract tests             -> search_find_commands_test.go
```

小さい単一責務toolなのでPython版は1fileを維持します。native版は従来の複数browse command fileからfinderだけを分離し、path探索変更時にtree/stats/doc-indexを読む必要をなくしています。
