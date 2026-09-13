# context-budget

Candidate textがagent contextへ入った場合のコストをcompactに見積もります。

## Development routing

```text
CLI / scan flow        -> script/context_budget.py
filesystem / text read -> script/messenger.py
cost estimation/output -> script/processing.py
```

`fast` / `accurate` の算定式変更なら `processing.py` を先に読みます。対象拡張子、ignore、text read変更なら `messenger.py` だけを先に読みます。

## Context Reducer self-application

- tool内部は必要ならscope全体を読んでよい
- agentへはtotal / largest candidates等へ圧縮して返す
- Task Routingにより変更理由から対象moduleへ直接進む
- Source of Truthを重複させない
- unrelated moduleを読まなくてもtargeted validationできる構造を維持する

`--mode fast` はmetadata中心、`--mode accurate` は実際のtextを読みます。内部I/O削減よりagent contextの削減と精度を優先します。
