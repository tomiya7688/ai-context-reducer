# policy-index

Policy文書をagentへ全文投入せず、rule候補を `path / line / heading / rule_text` 付きで索引化します。索引は原典policyの代替ではありません。

## Usage

Python:

```text
python script/policy_index.py README.md docs/ --max-findings 120
```

Native:

```text
acr-toolbox policy-index --max-findings 120 README.md docs/
```

Go標準flag parserを使うnative版ではoptionをinput pathより前に置きます。

`--max-findings 0` はunlimitedです。内部ではpolicy findingを全件検出し、agentへ返すfindingだけをboundedにするため、返却上限が解析精度を変えません。

## Discovery semantics

- `.md / .txt / .rst` をpolicy document候補にする
- `.git / node_modules / vendor / build / dist / generated` 等はdirectory scanから除外する
- overlapping file/directory inputは同じfileを1回だけscanする
- missing inputとexisting-but-unsupported inputを分ける
- filesystem walk/read errorを成功した空結果と混同しない

## Rule detection

英語のrule termはword boundaryで判定します。

```text
must
must not
should
should not
required
recommended
```

そのため `mustard` を `must`、`shoulder` を `should` と誤検出しません。日本語では `禁止 / 必須 / 推奨 / してはならない / すること` をrule候補として扱います。

これはruleの法的/設計上の強さを判定するものではなく、読むべき原典行へroutingするheuristicです。

## Output contract

```text
tool
status
discovered_policy_files
scanned_policy_files
finding_count_total
findings[]
findings_truncated
missing_inputs
unsupported_inputs
read_error_paths
walk_error_count
```

`status` は `ok / partial / no_policy_documents / input_unavailable` を区別します。findingが0件であることとinputを読めなかったことを混同しません。

## Development routing

```text
Python CLI / output        -> script/policy_index.py
Python document discovery  -> script/messenger.py
Python rule detection      -> script/processing.py
Python validation          -> tests/
Native discovery / CLI     -> tools/common/native/acr-toolbox/policy_index_command.go
Native rule detection      -> tools/common/native/acr-toolbox/policy_index_detection.go
Native validation          -> tools/common/native/acr-toolbox/policy_index_command_test.go
```

rule termやheading判定を変える場合はdetection fileだけを先に読みます。対象文書形式・ignore・I/Oを変える場合はdiscovery/CLI側だけを先に読みます。
