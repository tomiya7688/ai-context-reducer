# acr-hub

v1.1.0 Full Bundle の GUI Hub 実装領域です。

GUIは外部frameworkや追加runtimeを必須にせず、`acr-hub` 単体binaryが localhost に埋め込みUIを配信します。default browserの自動起動はbest-effortで、失敗しても表示URLをstdoutへ残してserverを継続します。

## Screen routing

利用者はtool名ではなく次のカテゴリから目的を選びます。

- Project Analysis
- Context Reduction
- Search / Structure
- Change / Validation
- Policy / Maintenance
- Templates

各actionは必要な入力だけを表示します。project rootは共通入力です。

実行結果は success / unavailable / failure / confirmation required / timeout / cancelled を区別し、最初はtop-level scalarだけのcompact summaryを表示します。raw JSON / text とstderrは折りたたみ詳細へ分けます。

Large / heavy解析は画面上の明示確認とbackendの `AllowHeavy` の両方を通らない限りprocessを起動しません。

## Backend

`backend/` は GUI から既存CLIを呼ぶ共通境界です。分析ロジックは持ちません。

~~~text
GUI
  -> backend.Invoke
  -> acr-toolbox / standalone binary
  -> existing stdout JSON / text
  -> GUI
~~~

主な境界:

- 実行可能なのは Full Bundle で配布する `acr-toolbox`, `go-symbols`, `go-import-map`, `go-package-graph`, `affected-tests` のみ
- shellを介さずbinaryを直接起動する
- JSON stdoutは再構築せず `json.RawMessage` として保持する
- `status` はGUI表示用に success / unavailable / failure / confirmation_required へ分類するが、CLI JSON自体は変更しない
- stdout / stderr / exit codeを別々に保持する
- stdout / stderrはmemory上でboundedに保持し、残りはdrainする
- JSONが上限を超えて切れた場合は不完全JSONを成功扱いしない
- timeoutとcaller cancellationを区別する
- `language-large-run` はGUI側の明示確認 (`AllowHeavy`) がない限り起動しない
- external backendやruntimeをinstallしない

## Local security boundary

HTTP serverは既定で `127.0.0.1:0` にだけbindします。CLI実行APIは起動ごとのrandom session tokenを要求し、他originからの単純POSTではCLIを起動しません。

## Development

~~~text
go test ./...
go vet ./...
go test -race ./...
go run . --bundle-root /path/to/full-bundle --project /path/to/project
~~~

画面カテゴリとaction入力は `ui/catalog.go`、compact resultは `ui/summary.go`、HTTP/APIは `ui/server.go`、CLI process境界は `backend/` がSource of Truthです。

## One-click Project Analysis

`Analyze project` は1操作で既存 `acr-toolbox analyze` と `acr-toolbox select` だけを順に実行します。

```text
Analyze
  -> Select
  -> recommended / conditional / unavailable
  -> user chooses Run
```

selectorが返していないLarge機能をGUI側から追加しません。Small repoにはSmall向けの候補だけを表示します。

各候補の `Run` は既存GUI actionへ接続します。追加入力が不要なactionはその場で実行し、入力やheavy確認が必要なactionは既存フォームへ移動します。Python-only等でGUI native backendが持たない候補は `unavailable` として明示し、別processへ勝手にfallbackしません。

Project Analysis中に推奨された機能そのものを自動実行することはありません。
