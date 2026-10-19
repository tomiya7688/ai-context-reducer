# context-budget

候補のファイルが多く、どれを先に読むか迷うときに、文章量の多いファイルを見つける道具です。文章量が多いファイルは、読む前に検索などで必要な部分を探すと、作業しやすくなります。

この道具は文章量の目安を出すだけです。どのファイルが作業に必要かは選びません。また、文章量が多いことを理由に、必要なファイルを読まないでよいとは判断しません。[今回読むファイルを選ぶ](../../../../docs/jp/手法/今回読むファイルを選ぶ.md)も参照してください。

結果の数字は、実際の単語数ではなく概算です。`token_estimate.approximate=true` であることを示します。

## Usage

Python:

```sh
python script/context_budget.py . --mode fast --top 40
python script/context_budget.py . --mode accurate --top 40
```

Native:

```sh
acr-toolbox context-budget --mode fast --top 40 .
acr-toolbox context-budget --mode accurate --top 40 .
```

native版はGo標準flag parserを使うため、optionはrepository pathより前に置きます。

`fast` はファイルの大きさから概算し、ファイルの文章は読みません。`accurate` は文章を読んで概算するため、`fast` より時間がかかります。どちらも実際の単語数を数えるものではありません。

JSONの `token_estimate` に算定式と `reads_file_contents` を入れるため、READMEを再読しなくても結果の確度を判断できます。

`--max-files 0` が既定で、内部scanにfile-count制限はありません。正しさを落とさないことを優先します。明示的な `--max-files` はperformance/safety capであり、実際に未走査候補が存在した場合だけ `scan_truncated=true` になります。

read / walk failureは成功した空結果と混同せず、`estimation_error_count` / `walk_error_count` と `status=ok_with_warnings` で示します。

## Development routing

```text
CLI / scan flow        -> script/context_budget.py
filesystem / text read -> script/messenger.py
cost estimation/output -> script/processing.py
```

`fast` / `accurate` の算定式変更なら `processing.py` を先に読みます。対象拡張子、ignore、text read変更なら `messenger.py` だけを先に読みます。

Native counterpartでは `context_budget_command.go` がcommand固有実装、`repo_commands.go` が共通repository walkを担当します。

## Context Reducer self-application

- tool内部は必要ならscope全体を読んでよい
- agentへはtotal / largest candidates等へ圧縮して返す
- 変更理由から、関係するmoduleへ直接進む
- Source of Truthを重複させない
- unrelated moduleを読まなくてもtargeted validationできる構造を維持する

## Validation

Python contract:

```sh
python -m unittest discover tests
```

Native contract:

```sh
cd ../../native/acr-toolbox
go test ./...
```
