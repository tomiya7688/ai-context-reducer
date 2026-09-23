# affected-tests (Python)

changed filesから、まず実行するtest候補と安全側fallbackを選ぶportable implementationです。

```text
python script/affected_tests.py --root .
python script/affected_tests.py --base origin/main...HEAD
python script/affected_tests.py --changed src/parser/lexer.py src/parser/parser.py
python script/affected_tests.py --dependency-map import-map.json --changed pkg/parser/lexer.py
```

出力は常にself-describing JSONです。旧 `--json` は互換性のため受理しますが、出力modeは変わりません。

`--dependency-map` には `python-import-map` / `go-import-map` 等の `files: [{file, imports}]` JSONを渡せます。consumerを補助候補として追加します。

dependency mapに `scan_truncated=true`、parse/read/walk errorがある場合、見えていないconsumerが存在し得ます。その場合は:

```text
status=ok_with_warnings
impact_uncertain=true
fallback=broader-or-full
```

として安全側へ倒します。

explicit mappingが完全に分かっている場合でも、不完全dependency mapを併用した結果から「影響はここまで」と断定しません。
