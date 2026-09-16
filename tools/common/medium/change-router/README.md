# change-router

Changed files から、最初に確認する test / docs 候補を compact な自己説明的JSONで返します。

## Context-reduction behavior

- changed file ごとに repository を再走査しない
- repository index は1回だけ作る
- dependency / generated directory は traversal 前に除外する
- internal test/doc indexは既定で全候補をscanする
- `--max-index-files` は明示的なperformance/safety capで、既定0=unlimited
- changed files / agentへ返すtest/doc候補はboundedにできる
- 実際に返却されない候補がある場合だけ `*_truncated=true`
- `--changed` を使えば Git diff 取得も省略できる
- Git unavailable / Git query failure / filesystem walk warningを成功した空結果と混同しない

## Output contract

主なtop-level field:

```text
tool
status
root_path
changed_source
changed_files
changed_files_truncated
index_candidates
index_truncated
index_walk_error_count
routes
```

各route:

```text
changed_file
candidate_tests
candidate_tests_truncated
candidate_docs
candidate_docs_truncated
```

`candidate_*_truncated` があるため、agentはREADMEを読み直さなくても候補がcompleteか判断できます。

## Internal architecture

```text
change_router.py -> CLI / input validation / JSON output
commander.py     -> orchestration
messenger.py     -> Git / filesystem boundary I/O
processing.py    -> candidate matching
```

この分割は変更時のagent working setを狭めるためのものです。形式的なlayeringを目的にしません。

## Usage

Python:

```text
python script/change_router.py <repo-root>
python script/change_router.py <repo-root> --base origin/main
python script/change_router.py <repo-root> --changed src/foo.py --changed src/bar.py
```

Native:

```text
acr-toolbox change-router --base origin/main <repo-root>
acr-toolbox change-router --changed src/foo.py --changed src/bar.py <repo-root>
```

Go標準flag parserを使うnative版ではoptionをrootより前に置きます。

主なlimit:

- `--max-changed`: routed changed file数。0=unlimited
- `--max-index-files`: internal test/doc indexのoptional safety cap。0=unlimited
- `--per-kind`: changed fileごとの返却test/doc候補数。0=unlimited

## Validation

```text
python -m unittest discover -s tests
cd ../../native/acr-toolbox && go test ./...
```
