# syntax-health

既存 Tree-sitter parser / grammar が利用できる環境で、parse tree全文ではなく syntax health だけを自己説明的JSONへ圧縮します。これは [`Syntax Health Validation`](../../../../docs/jp/構文チェックを軽い検証に使う.md) の補助実装であり、syntax successだけでsemantic correctnessやtask completionを判定しません。

```text
python script/syntax_health.py src/app.py src/lib.py
python script/syntax_health.py --json-input tree-sitter-summary.json
```

`tree-sitter parse --json-summary` をexternal backendとして利用します。Tree-sitterやgrammarを自動installしません。未導入時は `external_backend_unavailable` を返し、利用可能なcompiler / tests等のvalidationへfallbackします。

出力は `files_seen / files_with_syntax_issues / syntax_issue_files / syntax_issue_files_truncated` を持ち、問題の無いfileを大量列挙しません。`--max-files` はagent-visible failing filesだけをboundedにし、問題file総数の計算自体は打ち切りません。0はunlimitedです。

保存済みsummaryを `--json-input` で渡せるため、CIや別工程で生成したTree-sitter結果も同じcontractへ正規化できます。

Native counterpart:

```text
acr-toolbox syntax-health --max-files 80 src/app.py src/lib.py
acr-toolbox syntax-health --json-input tree-sitter-summary.json
```
