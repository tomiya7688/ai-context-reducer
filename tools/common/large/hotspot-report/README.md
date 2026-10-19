# hotspot-report

ファイルが多いプロジェクトで、大きいファイルや、フォルダーの奥にあるファイルを探す道具です。作業する場所が分からないときに候補を見つけ、検索する場所を決める手掛かりにします。

表示されたファイルが今回の作業に関係するとは限りません。作業の依頼を見て、関係するファイルだけを確認してください。[今回読むファイルを選ぶ](../../../../docs/jp/手法/今回読むファイルを選ぶ.md)も参照してください。

## Usage

Python:

```sh
python script/hotspot_report.py . --limit 30
```

Native:

```sh
acr-toolbox hotspot-report --limit 30 .
```

native版はGo標準flag parserを使うため、optionはrepository pathより前に置きます。

既定ではfile-count scan limitを設けません。tool内部の広いscanは許容し、agentへ返す `hotspots` だけを `--limit` でboundedにします。

performance / safety上必要な場合だけ `--max-files` を指定できます。実際に未走査fileが存在する場合だけ `scan_truncated=true` になります。

## Output contract

主なfield:

```text
scanned_file_count
stat_error_count
walk_error_count
scan_truncated
hotspot_count
hotspots[]
hotspots_truncated
```

`input_missing` / `input_not_directory` / `input_read_failed` と、成功した0件を混同しません。scan途中のfilesystem errorは `ok_with_warnings` とcountで示します。

各候補には、ファイルの場所 (`path`)、大きさ (`bytes`)、フォルダーの深さ (`depth`) が表示されます。これは、読むべき順番を決める評価ではありません。作業に関係するファイルが見つかったら、その中の必要な部分を検索してください。

## Development routing

Python版は小さな単一責務toolなので、形式的な分割はしません。

```text
Python scan / ranking / CLI -> script/hotspot_report.py
Native scan / ranking / CLI -> tools/common/native/acr-toolbox/hotspot_command.go
Shared native ignore policy -> tools/common/native/acr-toolbox/repo_commands.go
Native validation           -> tools/common/native/acr-toolbox/context_analysis_commands_test.go
```

分割によってagent working setが広がるため、Python版は1fileのまま維持します。
