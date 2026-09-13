# remote-delta

Local/remote Git差分をagent向けにcompactな自己説明的JSONへ変換します。

## Output contract

`tools/JSON_CONTRACT.md` に従います。通常結果はJSONのみです。`status` により成功、remote unavailable、Git利用不可、query失敗を区別し、unknown値は `null` にします。

主なfield:

```text
tool
status
base
remote
dirty
ahead
behind
diff_stat
changed_files
changed_files_truncated
remote_commits
```

## Development routing

- CLI option / JSON serialization変更: `script/remote_delta.py`
- Git command / external I/O変更: `script/messenger.py`
- 取得順序・status判定変更: `script/commander.py`
- compact field / truncation変更: `script/processing.py`
- output contract変更: `tests/test_processing.py` も確認

この分割は、Task Routing / Responsibility Map / Targeted Validationをtool開発自身へ適用するためのものです。

## Usage

```text
python script/remote_delta.py <repo-root>
python script/remote_delta.py <repo-root> --base HEAD --remote origin/main
```

## Targeted validation

```text
python -m unittest discover -s tests
python -m py_compile script/*.py
```
