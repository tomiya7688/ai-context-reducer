# acr-toolbox

Common tools の portable Go implementation です。

## Code routing

変更対象に対応するfileだけを先に読みます。

| Concern | File |
|---|---|
| CLI subcommand dispatch | `main.go` |
| repository walk / ignore / language metadata | `repo_commands.go` |
| repository analysis / recommendation | `analyze_command.go` |
| search / find / tree / stats / docs index | `browse_commands.go` |
| bounded excerpt / compact log | `text_commands.go` |
| Git diff / remote delta | `git_commands.go` |
| source-structure build / query / expand | `structure_index_command.go` |
| source-structure affected scope | `structure_index_affected.go` |
| source-structure subcommand routing | `structure_index_router.go` |
| materialize CLI / apply orchestration | `materialize_command.go` |
| materialize selection / hash / plan / manifest model | `materialize_plan.go` |
| materialize temporary writes | `materialize_write.go` |
| materialize replace / restore fallback | `safe_replace.go` |
| runtime / language environment detection | `env_commands.go` |
| build | `build.bat` / `build.sh` |

別concernのfileは、interface変更や共有helper変更が必要な場合だけ追加で読みます。

## Context rules

- `main.go` を巨大な実装置き場へ戻さない
- subcommand固有処理は責務に対応するfileへ置く
- outputはbounded / compactを既定にする
- repository walkではgenerated / dependency directoryを通常対象から外す
- full sourceやfull logを再出力しない
- 新しい共有abstractionは、2箇所以上で明確に重複を減らす場合だけ作る
- 成功時はcompact result、失敗時だけ必要なdiagnosticを増やす

## structure-index

Python common implementationと同じ `acr-source-structure-index-v1` を読み書きします。実装コードは共有せず、JSON contractだけを合わせます。

```text
acr-toolbox structure-index build --symbols symbols.json --graph graph.json --output index.json
acr-toolbox structure-index query --max-results 40 index.json Service
acr-toolbox structure-index expand --depth 2 --max-nodes 80 index.json module:pkg.service
acr-toolbox structure-index affected --changed pkg/a.py index.json
```

`build` はfull indexをstdoutへ出さずfileへ保存します。`query` / `expand` / `affected` はagentへ必要な範囲だけ返します。

`affected` は内部dependency closureを出力上限で打ち切りません。まず全closureを計算し、stdoutだけをboundedにします。index truncation / changed-file mapping failure / returned-scope truncationがある場合は `impact_uncertain=true` とbroader validation fallbackを返します。

## materialize

Python版 `materialize-tools` と共有コードを持たないnative implementationです。

```text
acr-toolbox materialize /path/to/ai-context-reducer --out ./portable-tools
acr-toolbox materialize /path/to/ai-context-reducer --out ./portable-tools --apply
```

既定はpreview onlyです。既存fileが異なる場合はconflictにし、`--overwrite` を明示しない限り置換しません。apply成功時は `.acr-materialized-tools.json` にsource revision / path / role / source path / SHA-256を残します。

Windowsでは既存destinationへ直接truncateせず、temporary fileとbackup/restore fallbackを使います。

## Validation

```text
Windows: build.bat
Linux/macOS: ./build.sh
```

build scriptは `go test ./...` 成功後にbinaryを生成します。

GitHub Actionsではnative testsをLinuxとWindowsの両方で実行し、その後Windows / Linux / macOS向け amd64 / arm64 binaryをcross buildします。
