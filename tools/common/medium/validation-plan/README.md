# validation-plan

Changed file pathから、最小限のtargeted validation候補を自己説明的JSONで返します。

これはbuild/test systemのSource of Truthではなく、最初に検証すべき種類を絞るrouting hintです。repository固有のtest commandが分かる場合はそちらを優先します。

## Usage

Python:

```text
python script/validation_plan.py src/parser.py config/schema.json
```

Native:

```text
acr-toolbox validation-plan src/parser.py config/schema.json
```

## Matching semantics

短いtermをpath全体のsubstringでは判定しません。path / filenameをtokenizeして判定するため、`build/core.py` の `ui` や `latest.py` の `test` のような偶然のsubstringで別カテゴリへ誤routingしないようにします。

主な分類:

- UI / scene / layout -> headless smoke + 必要時visual confirmation
- package / installer / release -> artifact generation + artifact smoke
- parser / lexer / validator / protocol -> targeted regression + contract/spec check
- random / simulation / physics / agent -> deterministic seam/fixed seed + bounded runtime
- structured data -> schema/parser validation + representative data check
- source file -> targeted tests + syntax/build check

該当しないfileは `targeted validation` を返します。

## Output contract

```text
tool
status
validation_by_file[]
  changed_file
  recommended_validation[]
```

同じ意味のvalidationは重複して返しません。

## Development routing

Python版は小さな単一責務toolなので形式的に分割しません。

```text
Python classification / CLI -> script/validation_plan.py
Python validation           -> tests/test_validation_plan.py
Native classification / CLI -> tools/common/native/acr-toolbox/validation_plan_command.go
Native validation           -> tools/common/native/acr-toolbox/change_validation_commands_test.go
```
