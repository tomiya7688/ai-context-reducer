# repo-profile

Repositoryの規模・language mix・top-level構造をcompactなJSONへまとめ、最初のtool/routing選択に使います。

全file数・size class・top-level directoriesはrepository walkをSource of Truthにします。PATH上に `scc` が既にあれば、language別のline/code/comment/blank/complexityだけを補助情報として取り込みます。外部toolは自動installしません。

## Use

```sh
python tools/common/small/repo-profile/script/repo_profile.py .
python tools/common/small/repo-profile/script/repo_profile.py --backend portable .
python tools/common/small/repo-profile/script/repo_profile.py --max-files 50000 .
```

通常は `--backend auto` のままで構いません。

- `scc` が利用可能: language metricsをsccで補強
- `scc` が無い: portable scanのみで正常終了
- sccが見つかったが実行失敗: portableへ戻り `backend_fallback` を明示
- `--backend scc`: sccを必須にしたい検証用

`--max-files 0` は内部file scan unlimitedです。明示capはperformance/safety用途で、実際に未走査fileがある場合だけ `scan_truncated=true` になります。

## Output

stdoutはself-describing JSONだけです。

主なfield:

- `tool`: `repo-profile`
- `status`
- `project_root`
- `backend`: language metricsに使った `portable` / `scc`
- `project_size_class`
- `files_scanned` / `scan_truncated`
- `recognized_source_files_scanned`
- `language_file_counts`
- `language_metrics[]`: `language/files/lines/code/comment/blank/complexity`
- `top_level_directories`
- `walk_error_count`

portable backendではscc固有のLOC/complexity値を推測せず `null` にします。

## Responsibility boundary

`repo-profile` はrouting用の浅いrepository profileです。詳細なlanguage/line statisticsは `repo-stats` を使います。

```text
repository size / top dirs / language mix -> repo-profile
language / line / code metrics            -> repo-stats
```

## Development routing

```text
implementation + external scc boundary -> script/repo_profile.py
contract / backend normalization tests  -> tests/test_repo_profile.py
```

このtoolは小さい単一責務なので形式的には分割せず、targeted testで外部backendとの契約を固定します。
