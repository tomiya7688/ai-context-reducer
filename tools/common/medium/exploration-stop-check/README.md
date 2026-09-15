# exploration-stop-check

Task contextに broad explorationを止めるための最低情報が揃っているかを、軽量heuristicで確認します。

## Usage

Python:

```sh
python script/exploration_stop_check.py context.md
```

Native:

```sh
acr-toolbox exploration-stop-check context.md
```

必須checkは次です。

```text
goal
required
acceptance
source
tests
```

`deferred` は補助checkで、stop判定の必須条件ではありません。

出力の `checks` / `missing_required_checks` / `stop_broad_exploration` を見れば、READMEを読まずにAIが判定理由を理解できます。

これは内容の妥当性を証明するcheckerではなく、「必要な情報カテゴリが存在するか」のrouting heuristicです。英語termはword boundaryで判定するため、`latest` 内の `test` のようなsubstringではcheckを満たしません。日本語termも利用できます。

`input_missing / input_not_file / read_failed` は不十分なcontextとは別のoperational stateとして返します。

## Development routing

```text
Python implementation -> script/exploration_stop_check.py
Python validation -> tests/test_exploration_stop_check.py
Native implementation -> tools/common/native/acr-toolbox/exploration_stop_command.go
Shared native term matching -> tools/common/native/acr-toolbox/task_context_terms.go
Native validation -> tools/common/native/acr-toolbox/task_context_commands_test.go
```
