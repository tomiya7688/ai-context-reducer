# context-pack-builder

Context Pack の生成toolです。成果物そのものがMarkdownなので、このtoolは無理にJSON化しません。

## Output contract

- 正常時はContext Pack Markdownをstdout、または `--output` 先へ出力します。
- Gitが利用できない場合とclean状態を区別します。
- changed/statusが上限で切られた場合は本文中にtruncatedを明示します。
- Markdown生成toolなので `tools/JSON_CONTRACT.md` の「成果物形式自体が目的のtool」の例外に該当します。
- input root missing / non-directory / output write failureはstderrへ短いdiagnosticを出してnon-zero exitにします。

## Usage

Python:

```text
python script/context_pack_builder.py <repo-root> --goal "..." --required "..." --acceptance "..."
python script/context_pack_builder.py <repo-root> --output CONTEXT_PACK.md
```

Native:

```text
acr-toolbox context-pack-builder --goal "..." --required "..." --acceptance "..." <repo-root>
acr-toolbox context-pack-builder --output CONTEXT_PACK.md <repo-root>
```

`--max-state-lines` はagent-visibleなGit状態だけをboundedにします。0はchanged/status rowsを返さない指定です。負値は0へ正規化します。

## Development routing

- Python CLI / output file変更: `script/context_pack_builder.py`
- Git状態取得変更: `script/messenger.py`
- Git結果からstateを組み立てるflow変更: `script/commander.py`
- Context Pack本文・項目変更: `script/processing.py`
- Python Markdown contract変更: `tests/test_processing.py`
- Native CLI / Git state / Markdown rendering: `tools/common/native/acr-toolbox/context_pack_command.go`
- Native contract validation: `tools/common/native/acr-toolbox/context_generation_commands_test.go`

分割は、ai-context-reducer自身の Task Routing / Responsibility Map / Targeted Validation をtool開発へ適用するために行います。小変更で無関係な責務を読ませないことを優先します。

## Targeted validation

```text
python -m unittest discover -s tests
python -m py_compile script/*.py
```

Native:

```text
cd ../../native/acr-toolbox
go test ./...
```
