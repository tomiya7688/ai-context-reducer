# acr-hub

v1.1.0 Full Bundle の GUI Hub 実装領域です。

## Backend

`backend/` は GUI から既存CLIを呼ぶ共通境界です。分析ロジックは持ちません。

```text
GUI
  -> backend.Invoke
  -> acr-toolbox / standalone binary
  -> existing stdout JSON / text
  -> GUI
```

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

画面と利用者向け操作は #26、ワンクリック分析導線は #27 で実装します。
