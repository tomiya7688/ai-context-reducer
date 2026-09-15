# structural-search

AST形状でsourceを探すためのbounded searchです。

外部 `ast-grep` が既に利用可能なら、その高品質なparser / pattern matcherをbackendとして再利用します。追加installは行いません。

`ast-grep` が無い場合は、Python sourceに限って標準library `ast` を使う軽量fallbackを使えます。

目的はast-grepを再実装することではなく、**text searchでは広すぎる探索を構文形状で絞り、agentへ返す候補だけを小さくすること**です。

## Examples

```sh
python script/structural_search.py 'print($ARG)' .
```

外部ast-grepがあれば自動利用します。

```json
{
  "tool": "structural-search",
  "status": "ok",
  "backend": "ast-grep",
  "match_semantics": "ast-grep-pattern",
  "matches_truncated": false,
  "matches": []
}
```

Python fallbackを明示する場合:

```sh
python script/structural_search.py 'client.send($ARG)' src --lang python --backend fallback
```

## Backend policy

### ast-grep

利用可能なら `ast-grep run --pattern ... --json=compact` を使います。

- multi-language
- ast-grep pattern / metavariable semantics
- repository ignore rules等はast-grep側の実装を利用
- full raw JSONはそのままagentへ流さず、このtoolのbounded JSONへ正規化

`sg` という実行名は、`--version` がast-grepだと確認できた場合だけ利用します。別OS commandを誤って呼ばないためです。

### Python AST fallback

追加dependencyなしで次を扱います。

- Python source only
- 1 statement / expression pattern
- `$ARG` のようなsingle-node metavariable
- 同じmetavariableを複数回書いた場合の構造一致

例:

```text
print($ARG)
same($X, $X)
client.send($VALUE)
x = $VALUE
```

扱わないもの:

- `$$$ARGS` のようなvariadic metavariable
- ast-grepのrule YAML / relational rule / rewrite
- Python以外のfallback parsing

対応外の場合は近似結果を黙って返さず、`status=invalid_pattern` または `status=backend_unavailable_for_language` を返します。

## Output contract

主なfield:

```text
backend
match_semantics
match_count
matches_returned
matches_truncated
matches[].path
matches[].start_line_1_based
matches[].start_column_0_based
matches[].end_line_1_based
matches[].end_column_0_based
matches[].matched_text
matches[].matched_text_truncated
matches[].captures
```

fallbackではさらに:

```text
files_scanned
parse_error_count
parse_error_paths
parse_error_paths_truncated
fallback_limitations
```

source snippet / capture textはboundedです。full sourceは返しません。

## Development routing

変更理由から最初に読むfileを絞ります。

- CLI / JSON output: `script/structural_search.py`
- backend selection / status semantics: `script/commander.py`
- external ast-grep process boundary: `script/messenger.py`
- Python AST matching / ast-grep JSON normalization: `script/processing.py`
- deterministic contract tests: `tests/test_processing.py`

この分割は一般的なlayeringのためではなく、backend変更・fallback matcher変更・CLI変更でagentのworking setを分けるためです。
