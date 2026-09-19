# scoped-guides

対象pathに適用候補となるAI guideを、repository rootからtargetまでのancestor path上だけで解決します。

```text
acr-toolbox scoped-guides path/to/target .
python script/scoped_guides.py path/to/target .
```

既定候補:
- `AI_CONTEXT.md`
- `AI_CONTEXT.local.md`
- `AGENTS.md`
- `CLAUDE.md`

独自名は `--name` を繰り返して指定できます。

このtoolはfilesystem scopeだけを解決します。特定agentのinstruction precedenceは推測・標準化しません。本文全文も既定では返さず、path / scope / reasonだけをcompact JSONで返します。
