# Tools

AIへ渡す情報量を減らすための前処理・routing・validation補助ツール群です。

## Entry

```text
Windows: tools/setup.bat <project-root>
Linux/macOS: tools/setup.sh <project-root>
```

不足runtime / SDKは自動installしません。利用可能なnative / Python / external toolだけを候補化します。

## Development routing

`tools/` 自体にもContext Reducerを適用します。

```text
tools/README.md
  -> tools/AI_CONTEXT.md
  -> target subtree local guide
  -> target tool README / source / tests / run-or-build script
  -> direct dependency only if needed
```

Goal・入出力契約・変更対象・validationが揃ったら探索を止めます。

## Output policy

- summary / index first
- bounded / truncated output
- full source / full log / full treeを既定出力にしない
- uncertainty / fallback / truncationを明示する
- 原典へ戻れるpath / symbol / reasonを残す
- targeted validationを優先する

## Python / Go

Python版とGo版は独立実装です。

- Python: build不要。stdlib中心。必要なら `run.bat` / `run.sh`
- Go: stdlib中心。`build.bat` / `build.sh` で test + build
- generic toolは合理的なら両方へ実装する
- 共有コードではなくCLI契約・fixture・testで整合を取る

## Native toolbox

`tools/common/native/acr-toolbox` はCommon機能のportable Go binaryです。

主なsubcommand:

```text
analyze search find tree stats doc-index slice
compact-log compact-diff remote-delta language-env env
```

## Categories

```text
common/small   shallow profile / cheap search
common/medium  routing / direct dependency / task context
common/large   bounded graph / context-cost analysis
python         Python-specific analysis
go             Go-specific analysis
csharp/c/cpp/gdscript
profiles       optional project-type / routing input
```

## Main routing tools

```text
Search-first             -> search / find / tree / doc-index / slice
Exploration stop         -> acceptance-extractor / exploration-stop-check
Remote delta             -> remote-delta / compact-diff
Responsibility           -> responsibility-candidates
Change routing           -> change-router
Architecture hints       -> architecture-boundary-router + project-provided profile
Affected tests           -> affected-tests
Policy routing           -> policy-index
Validation               -> validation-plan / compact-log
Context pack             -> context-pack-builder
Source structure         -> language-specific symbols / dependency / graph tools
Context priority         -> context-manifest / context-budget / hotspot-report
```

`architecture-boundary-router` は特定architectureへの適合checkerではありません。対象projectが既に持つ責務・境界情報を任意profileとして渡した場合だけ、最初のworking set選択に使います。

UPD Commanderを含む外部設計手法は、tools内部の責務分離や実装構造の参考にできますが、ai-context-reducerの機能要件・適合条件・標準architectureにはしません。

## Core rules

- full source / logs / docsを再出力しない
- generated outputをSource of Truthにしない
- runtime / SDK / packageを勝手にinstallしない
- Small repoへLarge解析を持ち込まない
- external toolが既にある場合は高品質backendとして使ってよい
- toolの維持コストが削減効果を上回るなら追加しない

詳細は各tool README、`tools/AI_CONTEXT.md`、`tools/NATIVE_COVERAGE.md`、`docs/portable-tools.md` を参照してください。
