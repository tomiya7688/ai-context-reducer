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
| context-size estimation | `context_budget_command.go` |
| large/deep file routing | `hotspot_command.go` |
| prioritized file manifest | `context_manifest_command.go` |
| Context Pack Markdown generation | `context_pack_command.go` |
| change -> test/doc routing | `change_router_command.go` |
| file -> validation-kind routing | `validation_plan_command.go` |
| Responsibility Map starter Markdown | `responsibility_candidates_command.go` |
| policy document discovery / CLI | `policy_index_command.go` |
| policy rule detection | `policy_index_detection.go` |
| duplicate documentation discovery / CLI | `doc_duplicate_command.go` |
| duplicate documentation normalization / detection | `doc_duplicate_detection.go` |
| low-value context path candidates | `ignore_candidates_command.go` |
| context analysis / generation validation | `context_analysis_commands_test.go` / `context_generation_commands_test.go` |
| change/validation routing validation | `change_validation_commands_test.go` |
| responsibility candidate validation | `responsibility_candidates_command_test.go` |
| policy validation | `policy_index_command_test.go` |
| duplicate documentation validation | `doc_duplicate_command_test.go` |
| ignore candidate validation | `ignore_candidates_command_test.go` |
| acceptance section extraction | `acceptance_command.go` |
| exploration-stop heuristic | `exploration_stop_command.go` |
| shared task-context term matching | `task_context_terms.go` |
| task-context validation | `task_context_commands_test.go` |
| source-structure build / query / expand | `structure_index_command.go` |
| source-structure affected scope | `structure_index_affected.go` |
| existing SCIP index adaptation / external SCIP boundary | `structure_scip_adapter.go` |
| existing Universal Ctags adaptation / external Ctags boundary | `structure_ctags_adapter.go` |
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

## Go flag ordering

Go標準 `flag` parserを使うcommandでは、optionをpositional pathより前に置きます。READMEの例もこの順序をSource of Truthにします。

## context-budget / hotspot-report

```text
acr-toolbox context-budget --mode fast --top 40 .
acr-toolbox context-budget --mode accurate --top 40 .
acr-toolbox hotspot-report --limit 30 .
```

`context-budget` のtoken数は常にrouting estimateです。`accurate` はfile内容を読むmodeですがtokenizer exactではなく、JSONの `token_estimate.approximate=true` と算定式で明示します。

両commandとも既定では内部file-count scan limitを持ちません。明示した `--max-files` はperformance/safety capで、実際に未走査候補が残った時だけ `scan_truncated=true` になります。

## context-manifest / context-pack-builder

```text
acr-toolbox context-manifest --limit 400 .
acr-toolbox context-pack-builder --goal "..." --acceptance "..." .
acr-toolbox context-pack-builder --output CONTEXT_PACK.md .
```

`context-manifest` はrepository全体をscanしてpriority順のbounded JSONだけ返します。scan errorは `stat_error_count / walk_error_count` と `ok_with_warnings` で明示し、missing rootを空manifestとして扱いません。

`context-pack-builder` は成果物そのものがMarkdownなのでJSON化しません。Git unavailable / query failure / clean state / truncated stateを本文で区別します。input/outputのoperational errorはstderr + non-zero exitです。

## change-router / validation-plan

```text
acr-toolbox change-router --base origin/main .
acr-toolbox change-router --changed src/core.py --changed src/schema.py .
acr-toolbox validation-plan src/core.py config/schema.json
```

`change-router` はinternal test/doc indexを既定で全scanし、agent-visible candidateだけをboundedにします。`--max-index-files` は明示的なsafety capです。Git failure、index walk warning、changed/index/per-route truncationをJSONで区別します。

`validation-plan` はpathをtokenizeしてvalidation種類を選び、`build` 内の `ui` や `latest` 内の `test` のようなsubstring false positiveを避けます。どちらもrepository固有build/test metadataがある場合は、そのSource of Truthを置き換えるものではありません。

## responsibility-candidates

```text
acr-toolbox responsibility-candidates --max 120 .
acr-toolbox responsibility-candidates --max 120 --max-scan-files 50000 .
```

Responsibility Map starterそのものが成果物なのでMarkdown-onlyです。内部code-file scanは既定unlimited、`--max` は返却table rowsだけをboundedにします。`--max-scan-files` は明示的なperformance/safety capです。

size metadata / filesystem walk failureはMarkdown commentで明示し、read errorをsize=0へ偽装しません。responsibility本文そのものは推測せずTODOのまま残します。

## policy-index / doc-duplicate-hints / ignore-candidates

```text
acr-toolbox policy-index --max-findings 120 AI_CONTEXT.md docs
acr-toolbox doc-duplicate-hints --max-groups 80 --max-occurrences-per-group 10 .
acr-toolbox ignore-candidates --limit 80 .
```

`policy-index` はpolicy全文をagentへ入れず、path / line / heading / rule_textへ圧縮します。dependency/generated docsを除外し、英語rule語はword boundaryで判定します。`--max-findings 0` はunlimitedで、内部finding検出を返却上限で打ち切りません。

`doc-duplicate-hints` はdocumentationを内部で全scanしてからduplicate group / occurrenceだけをboundedにします。重複本文はgroupごとに1回だけ返し、`occurrence_count_total` と `occurrences_truncated` で省略を明示します。`--max-groups 0` と `--max-occurrences-per-group 0` はunlimitedです。

`ignore-candidates` は候補directory自体を1件返した時点でそのsubtreeをpruneします。各candidateは `path / kind / matched_rule` を持ち、候補理由をJSONだけで判断できます。自動ignoreはせず `review_required_before_ignoring=true` を返します。

3 commandともmissing/read/walk errorを成功した0件と区別し、Python版とは共有コードを持たずJSON contractとtargeted testで意味を合わせます。

## acceptance-extractor / exploration-stop-check

```text
acr-toolbox acceptance-extractor --max-lines-per-section 40 task.md
acr-toolbox exploration-stop-check context.md
```

Python版とは実装を共有せず、JSON fieldとheuristic semanticsを合わせます。英語termはword boundaryで判定し、`goalkeeper` / `latest` のようなsubstring false positiveを避けます。日本語termも対応します。

`acceptance-extractor` は `goal / required / acceptance / deferred` heading sectionをboundedに返します。`exploration-stop-check` は `goal / required / acceptance / source / tests` が揃った時だけ `stop_broad_exploration=true` にします。

## structure-index

Python common implementationと同じ `acr-source-structure-index-v1` を読み書きします。実装コードは共有せず、JSON contractだけを合わせます。

```text
acr-toolbox structure-index build --symbols symbols.json --graph graph.json --output index.json
acr-toolbox structure-index query --max-results 40 index.json Service
acr-toolbox structure-index expand --depth 2 --max-nodes 80 index.json module:pkg.service
acr-toolbox structure-index affected --changed pkg/a.py index.json
```

`build` はfull indexをstdoutへ出さずfileへ保存します。`query` / `expand` / `affected` はagentへ必要な範囲だけ返します。

### Existing SCIP index reuse

既存 `index.scip` と `scip` CLIがある場合は、SCIP protobuf parserをtoolbox内へ複製せず、external boundaryとして `scip print --json` を利用します。

```text
acr-toolbox structure-index build --scip index.scip --output index.json
acr-toolbox structure-index build --scip-json index.scip.json --output index.json
```

`scip` がPATHに無ければ自動installせず `external_backend_unavailable` を返します。external commandの失敗出力もboundedにして、巨大ログをagent contextへ流しません。

SCIP documentを `module:scip:<relative_path>` routing unitへ変換し、cross-document reference / relationshipを `depends_on`、nested symbolを `owns` として保持します。そのため変換後は通常の `query / expand / affected` を再利用できます。

### Existing Universal Ctags reuse

既存Universal CtagsのJSON Lines出力、またはPATH上のJSON対応Universal Ctagsを再利用できます。

```text
acr-toolbox structure-index build --ctags-json tags.jsonl --root . --output index.json
acr-toolbox structure-index build --ctags-source . --root . --output index.json
```

`--ctags-source` は `ctags --list-output-formats` でJSON対応を確認し、未導入またはJSON非対応なら自動installせず `external_backend_unavailable` を返します。full Ctags JSONをstdoutへ返さず、file / symbol / definition line / kind / scope ownershipを共通IRへ変換します。

Ctagsはsymbol indexでありcross-file dependency graphを必ず持つわけではないため、`affected` を高精度に使う場合は既存dependency/package graphやSCIP入力と併用します。SCIPとCtagsは同じ `build` invocationへ混在できます。

`affected` は内部dependency closureを出力上限で打ち切りません。まず全closureを計算し、stdoutだけをboundedにします。index truncation / changed-file mapping failure / returned-scope truncationがある場合は `impact_uncertain=true` とbroader validation fallbackを返します。

## materialize

Python版 `materialize-tools` と共有コードを持たないnative implementationです。

```text
acr-toolbox materialize --out ./portable-tools /path/to/ai-context-reducer
acr-toolbox materialize --out ./portable-tools --apply /path/to/ai-context-reducer
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
