# git-history-health

`git-sizer` のmachine-readable出力を、そのままagentへ渡さず concernのあるGit履歴指標だけへ圧縮します。

通常は既にインストール済みの `git-sizer` を利用します。自動インストールはしません。

```text
python script/git_history_health.py .
python script/git_history_health.py --min-concern 2 --max-findings 20 .
```

保存済みのgit-sizer JSONも利用できます。

```text
python script/git_history_health.py --json-input git-sizer.json .
```

native counterpart:

```text
acr-toolbox git-history-health .
acr-toolbox git-history-health --json-input git-sizer.json .
```

## Output contract

JSON-onlyです。主要field:

- `status`: `ok`, `external_backend_unavailable`, `external_backend_failed`, input error
- `backend`: `git-sizer` または `git-sizer-json-input`
- `metric_count_total`: 認識したgit-sizer metric総数
- `concern_count_total`: `min_level_of_concern` 以上のmetric総数
- `findings`: level of concern降順のbounded findings
- `findings_truncated`: 返却上限で省略したか

各findingは `metric / value / level_of_concern` を必須とし、利用可能なら `unit / description / object_description` を持ちます。

`--max-findings 0` は返却unlimitedです。解析自体を返却上限で打ち切りません。

`git-sizer` が無い場合に独自Git object graph analyzerへfallbackしません。履歴解析を低品質に複製せず、external backend unavailableを明示します。
