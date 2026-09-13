# remote-delta

Local/remote Git差分をagent向けにcompact化します。

## Development routing

- CLI option変更: `script/remote_delta.py`
- Git command / external I/O変更: `script/messenger.py`
- 取得順序・flow変更: `script/commander.py`
- compact表示・truncation変更: `script/processing.py`

この分割は、Task Routing / Responsibility Map / Targeted Validationをtool開発自身へ適用するためのものです。出力形式だけの変更でGit実行コードを読む必要がない状態を維持します。
