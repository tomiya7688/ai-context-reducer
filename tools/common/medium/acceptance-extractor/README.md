# acceptance-extractor

Markdown task/context fileから `goal / required / acceptance / deferred` sectionを抽出し、自己説明的JSONで返します。

## Usage

Python:

```sh
python script/acceptance_extractor.py task.md --max-lines-per-section 40
```

Native:

```sh
acr-toolbox acceptance-extractor --max-lines-per-section 40 task.md
```

各sectionはheading名から判定します。英語termはword boundaryで判定するため、`Goalkeeper` を `Goal` と誤認しません。日本語termは通常のsubstring matchです。

`--max-lines-per-section` はagentへ返すcontext量だけを制限します。内容が上限を超えた場合は `section_truncated.<name>=true` になります。

主なJSON field:

```text
status
input_file
sections.goal
sections.required
sections.acceptance
sections.deferred
section_truncated
```

`input_missing / input_not_file / read_failed` は成功した空sectionと区別します。

## Development routing

```text
Python implementation -> script/acceptance_extractor.py
Python validation     -> tests/test_acceptance_extractor.py
Native implementation -> tools/common/native/acr-toolbox/acceptance_command.go
Shared native term matching -> tools/common/native/acr-toolbox/task_context_terms.go
Native validation -> tools/common/native/acr-toolbox/task_context_commands_test.go
```
