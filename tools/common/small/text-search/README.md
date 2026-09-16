# text-search

Search-first / Read-second 用のbounded text searchです。既に `rg` が使える場合は外部backendを利用し、使えない環境ではstdlib / native fallbackで動作します。外部toolを自動installしません。

## Use

Python:

```sh
python tools/common/small/text-search/script/text_search.py Service src
python tools/common/small/text-search/script/text_search.py -F "exact text" .
python tools/common/small/text-search/script/text_search.py --context 2 error src
```

Native:

```sh
acr-toolbox search Service src
acr-toolbox search -F "exact text" .
acr-toolbox search --context 2 error src
```

Go標準flag parserを使うnative版ではoptionをpositional argumentより前へ置きます。

通常は `--backend` を指定しません。`auto` が既定で、compatibleなqueryなら `ripgrep`、それ以外は `portable` を使います。明示的な検証時だけ `--backend portable` / `--backend ripgrep` を使います。

## Output

stdoutはself-describing JSONだけです。human textとJSONを重複出力しません。

主要field:

- `tool`: `text-search`
- `status`: `ok`, `partial`, input/backend error等
- `root_path`: 実際に検索したscope
- `query`: pattern / mode / case / glob / context
- `backend`: `ripgrep` または `portable`
- `matches[]`: `path / line / text`。context指定時だけ `before / after`
- `matches_truncated`: agent-visible result limitで未返却matchがあるか
- `*_error_count`: portable scan中のfilesystem/read warning
- `backend_fallback`: auto選択したexternal backendが失敗してportableへ戻った場合だけ存在

成功した0件は `status=ok` + `matches=[]` です。入力不在・invalid regex・backend failureを空結果へ偽装しません。

`--max-results 0` は返却件数unlimited、`--max-file-bytes 0` はfile size limitなしです。

## Scan / context policy

- tool内部のsearchはagentの代わりに広く実行してよい
- agentへ返すmatchだけを `--max-results` でboundedにする
- generated / dependency / cache directoryは既定でpruneする
- `--context` は必要な場合だけ使い、同じfile全文を返さない
- external backendの巨大stderrはbounded diagnosticへ変換する

## Development routing

```text
Python CLI + portable/rg boundary -> script/text_search.py
Python contract tests             -> tests/test_text_search.py
Native search implementation      -> tools/common/native/acr-toolbox/search_command.go
Native contract tests             -> search_find_commands_test.go
```

小さい単一責務toolなのでPython版は形式的に分割しません。native版は従来の複数browse command fileからsearchだけを分離し、backend/検索契約変更時のworking setを狭めています。
