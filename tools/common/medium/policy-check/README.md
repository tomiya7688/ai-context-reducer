# policy-check

regex / literalで安全に表現できるproject policyを、path scope付きで検査するportable fallbackです。

```text
acr-toolbox policy-check --rules policy-rules.json .
python script/policy_check.py --rules policy-rules.json .
```

## Rule format

```json
{
  "rules": [
    {
      "id": "POL001",
      "paths": ["src/ui/**"],
      "exclude": ["src/ui/generated/**"],
      "severity": "error",
      "mode": "literal",
      "forbid": "Path.write_text(",
      "message": "UI layer must not write files directly"
    },
    {
      "id": "POL002",
      "paths": ["src/config/**"],
      "severity": "warning",
      "mode": "regex",
      "require": "^# policy:",
      "message": "Config files should declare their policy marker"
    }
  ]
}
```

各ruleは `forbid` または `require` のどちらか1つを持ちます。 `severity` は `error` / `warning`、`mode` は `literal` / `regex` です。

## Suppression

lineまたは直前lineへ理由付きで記録します。

```text
# acr-ignore POL001: generated compatibility shim
Path.write_text(...)
```

理由が空のsuppressionは有効化せず、`invalid_suppressions` に記録します。

## Semantic rules

AST / dataflow / architecture semanticsが必要なruleは `"semantic": true` として設定できます。portable checkerは違反判定せず `unsupported_rules` へ出し、ast-grep / Semgrep / project固有checker等の高精度backendへ委譲します。

## Exit code

- `0`: error severity violationなし
- `1`: error severity violationあり
- `2`: invalid rule/config/input

warningはexit code 1にしません。
