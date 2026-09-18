# language-run

`language-setup` が選ぶlanguage-specific Small analyzerを実行します。

```text
acr-toolbox language-run /path/to/project
python script/language_run.py --acr-root /path/to/ai-context-reducer /path/to/project
```

## Output policy

full analyzer resultはstdoutへ再出力せず、既定では対象projectの `.acr/language/` に保存します。stdoutにはtool、status、backend、output path、skip/failure理由だけを返します。

## Native backend

`acr-toolbox language-run` は次のSmall symbol analyzerをexe内蔵fallbackとして持ちます。

- Python
- C#
- Go
- C
- C++
- GDScript

そのためSmall symbol indexにはPython / .NET / Go / compiler / Godot runtimeを必須としません。

内蔵parserはshallow routing用の近似解析です。完全な構文・型・dependency解析が必要な場合はMedium/Large toolと既存SDK/compiler/parserへ進みます。

Python fallback版はsource tree内の各scriptを利用するため、`--acr-root` が必要です。

setup時に自動実行するのはSmall analyzerだけです。Medium/Large analyzerはrouting候補に留め、current taskで必要になった時だけ実行します。
