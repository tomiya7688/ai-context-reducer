# policy-index

Policy文書をagentへ全文投入せず、rule候補をpath / line / heading付きで索引化します。

## Development routing

```text
CLI / output       -> script/policy_index.py
document discovery -> script/messenger.py
rule detection     -> script/processing.py
```

rule wordやheading判定を変える場合は `processing.py` を先に読みます。対象文書形式や読込方法を変える場合は `messenger.py` を先に読みます。

この分離はTask Routing / Responsibility Map / Hierarchical Contextをtool開発自身へ適用するためのものです。索引は原典policyの代替ではありません。
