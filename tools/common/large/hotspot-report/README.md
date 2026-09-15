# hotspot-report

Repository内部で大きい / 深いfileを探索し、agentが最初に読む候補をbounded JSONへ圧縮します。

## Usage

Python:

```sh
python script/hotspot_report.py . --limit 30
```

Native:

```sh
acr-toolbox hotspot-report . --limit 30
```

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

各hotspotは `path / bytes / depth` を返します。これは設計良否を断定するscoreではなく、読む優先順位を決めるrouting hintです。

## Development routing

Python版は小さな単一責務toolなので、形式的な分割はしません。

```text
Python scan / ranking / CLI -> script/hotspot_report.py
Native scan / ranking / CLI -> tools/common/native/acr-toolbox/hotspot_command.go
Shared native ignore policy -> tools/common/native/acr-toolbox/repo_commands.go
Native validation           -> tools/common/native/acr-toolbox/context_analysis_commands_test.go
```

分割によってagent working setが広がるため、Python版は1fileのまま維持します。
