# language-run

`language-setup` が選ぶlanguage-specific Small analyzerを、利用可能なlauncherだけで実行します。

```text
acr-toolbox language-run --acr-root /path/to/ai-context-reducer /path/to/project
python script/language_run.py --acr-root /path/to/ai-context-reducer /path/to/project
```

## Output policy

full analyzer resultはstdoutへ再出力せず、既定では対象projectの `.acr/language/` に保存します。stdoutにはtool、status、backend、output path、skip/failure理由だけを返します。

## Backend selection

- Python: Python stdlib AST analyzer
- Go: bundled `go-symbols` binary、無ければ既存Go runtimeで `go run`
- C# / C / C++ / GDScript: 現在はbundled Python analyzerを利用
- launcher/runtimeが無ければ自動installせずskip

setup時に自動実行するのはSmall analyzerだけです。Medium/Large analyzerはrouting候補に留め、current taskで必要になった時だけ実行します。
