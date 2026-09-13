# Go Tools Local Context

この文書は `tools/go/` にだけ適用する差分ルールです。共通方針は `tools/AI_CONTEXT.md` を参照してください。

## Read first

対象toolについて次だけ読む。

1. 対象directoryの `README.md`
2. `main.go` / 同等source
3. `*_test.go`
4. `build.sh` / `build.bat`

他のGo toolは共通helperや入出力契約を確認する必要がある場合だけ読む。
Python版は互換fixtureまたはCLI契約比較が必要な場合だけ読む。

## Implementation

- Go標準ライブラリで十分なら外部moduleを追加しない
- parserが標準ライブラリにある言語/形式はregex再実装よりparserを優先する
- 単一binary化しやすい構造を保つ
- `dist/` は生成物であり読解対象・Source of Truthにしない
- build scriptは原則 `go test` 成功後にbinaryを生成する

## Output

既定出力はcompactにする。

- list件数に上限を設けられるtoolは上限を持つ
- full sourceを出さず path / symbol / relation / reasonを優先する
- JSON outputは機械処理用、text outputは短い人間向けsummaryとする
- truncation / uncertainty / fallbackを隠さない

## Validation

通常は対象tool directoryだけで十分。

```text
go test ./...
build.sh または build.bat 相当の go build
small fixture smoke
```

共有JSON契約を変更した場合だけ対応するPython版またはconsumerを追加確認する。
