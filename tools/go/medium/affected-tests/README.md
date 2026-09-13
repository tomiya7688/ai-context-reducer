# affected-tests (Go)

Python版とは共有コードを持たない独立実装です。changed filesからtest候補、confidence、fallback理由をcompactに出します。

## Build

```text
Windows: build.bat
Linux/macOS: ./build.sh
```

`build.*` は `go test ./...` を先に実行し、成功時に `dist/affected-tests(.exe)` を生成します。

## Usage

```text
affected-tests --root .
affected-tests --root . --base origin/main...HEAD
affected-tests --changed src/parser/lexer.py --changed src/parser/parser.py
affected-tests --config affected-tests.json --json
affected-tests --dependency-map import-map.json --changed pkg/parser/lexer.py
```

`--changed` は複数回指定できます。省略時は `git diff --name-only [base]` を利用します。

`--dependency-map` には `python-import-map` / `go-import-map` と同じ `files: [{file, imports}]` 形式のJSONを渡せます。直接importしているconsumerを補助信号として拾い、そのconsumerのtest候補も追加します。

## Config

```json
{
  "mappings": [
    {
      "source": "src/parser/*",
      "tests": ["tests/parser/test_parser.py"],
      "broader": false
    }
  ],
  "broader_patterns": [
    "**/core/**",
    "**/shared/**",
    "**/schema.*",
    "**/api/**"
  ]
}
```

## Output policy

- explicit mapping hit: `high`
- naming/default candidate: `medium`
- dependency-map consumer: 補助候補としてtestを追加
- broad-impact path: `medium` + `broader`
- no reliable candidate: `low` + `subsystem-or-full`

Nx/Pants等の既存project graph toolが利用できる場合は、そちらを高精度backendとして優先して構いません。このtoolはportable fallbackです。
