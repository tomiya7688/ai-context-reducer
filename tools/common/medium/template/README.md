# template

単純な canonical template + JSON variables を deterministic に展開するportable generatorです。

```text
acr-toolbox template --template templates/foo --vars vars.json --out generated/foo --template-id foo --template-version 1
python script/template.py --template templates/foo --vars vars.json --out generated/foo
```

placeholderは `{{name}}` だけを扱います。Jinja2の条件分岐・loop等は実装しません。

主な機能:
- file / directory template
- JSON scalar variables
- repeatable `--required`
- unresolved placeholder detection
- `--dry-run`
- `--check` によるdrift検出
- compact first-change hint
- template id/version
- exact variables file SHA-256
- generated metadata sidecar / directory metadata
- Copier / Cookiecutter availability reporting

高度なtemplate lifecycleが必要なら既存Copier/Cookiecutter等を利用し、このfallbackを完全互換engineにはしません。
