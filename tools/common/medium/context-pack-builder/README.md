# context-pack-builder

Context Pack の生成toolです。成果物そのものがMarkdownなので、このtoolは無理にJSON化しません。

## Output contract

- 正常時はContext Pack Markdownをstdout、または `--output` 先へ出力します。
- Gitが利用できない場合とclean状態を区別します。
- changed/statusが上限で切られた場合は本文中にtruncatedを明示します。
- Markdown生成toolなので `tools/JSON_CONTRACT.md` の「成果物形式自体が目的のtool」の例外に該当します。

## Development routing

- CLI / output file変更: `script/context_pack_builder.py`
- Git状態取得変更: `script/messenger.py`
- Git結果からstateを組み立てるflow変更: `script/commander.py`
- Context Pack本文・項目変更: `script/processing.py`
- Markdown contract変更: `tests/test_processing.py` も確認

分割は、ai-context-reducer自身の Task Routing / Responsibility Map / Targeted Validation をtool開発へ適用するために行います。小変更で無関係な責務を読ませないことを優先します。

## Usage

```text
python script/context_pack_builder.py <repo-root> --goal "..." --required "..." --acceptance "..."
python script/context_pack_builder.py <repo-root> --output CONTEXT_PACK.md
```

## Targeted validation

```text
python -m unittest discover -s tests
python -m py_compile script/*.py
```
