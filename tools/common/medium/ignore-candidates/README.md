# ignore-candidates

Repository内の、agent contextへ入れる価値が低い可能性が高いpathを自己説明的JSONで候補提示します。手法そのものは [`Context Exclusion`](../../../../docs/jp/通常は読まないものを決める.md) を参照してください。

このtoolはignore ruleを自動適用しません。`review_required_before_ignoring=true` を返し、人間/agentがSource of Truthとvalidation用途を確認してからcontext exclusionを判断する前提です。`.gitignore` / `.ignore` 等の設定書換えやfile削除は行いません。

## Usage

Python:

```text
python script/ignore_candidates.py --limit 80 <repo-root>
```

Native:

```text
acr-toolbox ignore-candidates --limit 80 <repo-root>
```

`--limit 0` はunlimitedです。返却上限はagent-visible outputにだけ効きます。

候補directory（例: `node_modules`, `build`, `.venv`）を見つけた場合、そのdirectory自体を1件返してsubtreeはscanしません。これにより `node_modules/pkg/...` の大量fileを重複候補として列挙しません。

各candidateは `path / kind / matched_rule` を持つため、READMEを読まずJSONだけでも候補理由を確認できます。

missing root、non-directory、walk failureは成功した0件と区別します。

## Development routing

Python版は小さな単一責務toolなので分割しません。

```text
Python scan / rules / JSON -> script/ignore_candidates.py
Native scan / rules / JSON -> tools/common/native/acr-toolbox/ignore_candidates_command.go
```

候補判定とtraversalが密接で、分割すると変更時working setが広がるため1fileを維持します。

## Validation

```text
python -m unittest discover -s tests
cd ../../native/acr-toolbox && go test ./...
```
