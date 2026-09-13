# change-router

Changed files から、最初に確認する test / docs 候補を compact に返します。

## Context-reduction behavior

- changed file ごとに repository を再走査しない
- repository index は1回だけ作る
- dependency / generated directory は traversal 前に除外する
- changed files / index candidates / output candidates に上限を持つ
- 上限へ到達した場合は `truncated` を明示する
- `--changed` を使えば Git diff 取得も省略できる

## Internal architecture

このtoolは複数の責務境界を持つため、内部実装だけUPD Commanderの責務分離を参考にしています。

```text
change_router.py
  -> CLI entrypoint / argument parsing / output

commander.py
  -> orchestration only

messenger.py
  -> Git / filesystem boundary I/O

processing.py
  -> candidate matching / pure-ish processing
```

これはUPD適合checkerではありません。UPD固有のlayer名や命名規則を対象repositoryへ要求しません。

## Usage

```text
python script/change_router.py <repo-root>
python script/change_router.py <repo-root> --base origin/main
python script/change_router.py <repo-root> --changed src/foo.py --changed src/bar.py
python script/change_router.py <repo-root> --json
```

主なbudget:

- `--max-changed`: changed file数
- `--max-index-files`: test/doc index候補数
- `--per-kind`: changed fileごとのtest/doc候補数

budgetを上げる前に、rootやchanged setを狭められないか確認してください。
