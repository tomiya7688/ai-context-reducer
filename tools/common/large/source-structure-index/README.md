# source-structure-index

既存のlanguage-specific analyzer / semantic indexが持つ構造情報を、再利用可能な `acr-source-structure-index-v1` へ束ねます。

目的はfull indexをagentへ読ませることではありません。indexはfileへ保存し、agentには `query` / `expand` / `affected` で必要な候補と周辺graphだけを返します。

## Implementations

共有コードを持たない2実装です。

- Python: `script/source_structure_index.py`
- native Go: `acr-toolbox structure-index`

片方でbuildした `acr-source-structure-index-v1` を、もう片方の `query` / `expand` / `affected` で読めます。

## Input priority

既に高品質な解析結果がある場合は、独自parserを増やすより再利用します。

```text
existing build / semantic index
  -> existing analyzer JSON
  -> repository-owned lightweight analyzer
```

対応入力:

- Python / Go等のrepository-owned symbol JSON
- dependency / package graph JSON
- `ast-grep outline --json=compact` JSON（Python adapter）
- `scip print --json` JSON（Python / native）
- existing `index.scip` + already-installed `scip` CLI（Python / native）
- Universal Ctags JSON Lines（Python / native）
- source path + already-installed Universal Ctags JSON backend（Python / native）

外部runtime / package / CLIは自動installしません。

## Build

### Repository analyzers

```sh
python tools/python/small/python-symbols/script/python_symbols.py src > /tmp/symbols.json
python tools/python/large/python-module-graph/script/python_module_graph.py . > /tmp/graph.json
python tools/common/large/source-structure-index/script/source_structure_index.py build \
  --symbols /tmp/symbols.json \
  --graph /tmp/graph.json \
  --root . \
  --output .acr/source-structure-index.json
```

Native:

```sh
acr-toolbox structure-index build \
  --symbols /tmp/symbols.json \
  --graph /tmp/graph.json \
  --root . \
  --output .acr/source-structure-index.json
```

### ast-grep outline

```sh
ast-grep outline src --json=compact > /tmp/outline.json
python tools/common/large/source-structure-index/script/source_structure_index.py build \
  --symbols /tmp/outline.json \
  --root . \
  --output .acr/source-structure-index.json
```

outline adapterはnested `members` をflattenしつつ `owner_qualified_name` を `owns` edgeへ変換します。

### SCIP

既存 `index.scip` と `scip` CLIがある場合:

```sh
python tools/common/large/source-structure-index/script/source_structure_index.py build \
  --scip index.scip \
  --output .acr/source-structure-index.json

acr-toolbox structure-index build \
  --scip index.scip \
  --output .acr/source-structure-index.json
```

既に `scip print --json` の結果を持つ場合はSCIP CLIも不要です。

```sh
python tools/common/large/source-structure-index/script/source_structure_index.py build \
  --scip-json /tmp/index.scip.json \
  --output .acr/source-structure-index.json

acr-toolbox structure-index build \
  --scip-json /tmp/index.scip.json \
  --output .acr/source-structure-index.json
```

`scip` が無い場合は自動installせず、raw `--scip` 入力は `external_backend_unavailable` になります。

SCIP adapterはroutingに必要な次を抽出します。

- document / file
- symbol / definition location
- enclosing symbol ownership
- cross-document reference / relationship dependency
- Python版ではbounded signature metadataも保持

各SCIP documentを `module:scip:<relative_path>` routing unitとして扱うため、package graphが無い言語でも `affected` に利用できます。native版もnested symbolを明示node + `owns` edgeへ変換し、generic builderで平坦化しません。

### Universal Ctags

Universal Ctagsを既に利用できる場合は、そのmulti-language symbol indexを再利用します。Ctags parserそのものはrepository内へ再実装しません。

Source pathから直接build:

```sh
python tools/common/large/source-structure-index/script/source_structure_index.py build \
  --ctags-source . \
  --root . \
  --output .acr/source-structure-index.json

acr-toolbox structure-index build \
  --ctags-source . \
  --root . \
  --output .acr/source-structure-index.json
```

既にUniversal Ctags JSON Lines出力を持つ場合はCtags CLIも不要です。

```sh
ctags --output-format=json --fields=+nSlesp --recurse=yes -o - . > /tmp/tags.jsonl

python tools/common/large/source-structure-index/script/source_structure_index.py build \
  --ctags-json /tmp/tags.jsonl \
  --root . \
  --output .acr/source-structure-index.json

acr-toolbox structure-index build \
  --ctags-json /tmp/tags.jsonl \
  --root . \
  --output .acr/source-structure-index.json
```

`--ctags-source` はPATH上の既存 `ctags` を使い、`--list-output-formats` でJSON対応を確認します。Ctagsが無い、またはJSON対応Universal Ctagsでない場合は自動installせず `external_backend_unavailable` を返します。

Ctags JSON Linesからroutingに必要な次だけを共通IRへ変換します。

- file / symbol
- definition line / end line（backendが返す場合）
- language / kind
- scopeから得られるnested ownership
- bounded signature metadata（Python adapter）

full Ctags outputをagent stdoutへ流さず、build後は通常の `query / expand` を使います。Ctagsはsymbol indexでありcross-file dependency graphを必ず提供するものではないため、`affected` を高精度に使う場合は既存package/dependency graphやSCIP等のdependency inputと併用します。

`build` はfull indexをstdoutへ出しません。stdoutはstatus / counts / truncation / compact input metadataだけです。

## Query

```sh
python tools/common/large/source-structure-index/script/source_structure_index.py query \
  .acr/source-structure-index.json Service

acr-toolbox structure-index query --max-results 40 \
  .acr/source-structure-index.json Service
```

`id` / `name` / `qualified_name` / `path` を検索します。既定では40件まで返します。

## Expansion

```sh
python tools/common/large/source-structure-index/script/source_structure_index.py expand \
  .acr/source-structure-index.json module:pkg.service \
  --depth 2 --max-nodes 80 --direction both

acr-toolbox structure-index expand --depth 2 --max-nodes 80 --direction both \
  .acr/source-structure-index.json module:pkg.service
```

出力には `distance` / `fan_in` / `fan_out` / selected edges / `cycle_groups` / `nodes_truncated` を含みます。

曖昧なtargetでは勝手に1件を選ばず `target_ambiguous` と候補を返します。

## Dependency-based affected scope

Nx / Pants等の「changed targetからdependentを求める」考え方のportable fallbackです。既存build graphがある場合はそちらをSource of Truthとして優先します。

```sh
python tools/common/large/source-structure-index/script/source_structure_index.py affected \
  .acr/source-structure-index.json \
  --changed src/core.py --max-results 80

acr-toolbox structure-index affected \
  --changed src/core.go --max-results 80 \
  .acr/source-structure-index.json
```

内部ではchanged fileのowner module/packageを `contains_file` から特定し、`depends_on` を逆向きに**全transitive closure**まで辿ります。

`--max-results` はagentへ返す件数だけを制限します。内部impact計算は途中で打ち切りません。

次の場合は `impact_uncertain=true` とし、`recommended_validation_scope=broader_or_full` へ倒します。

- source structure inputがtruncated
- changed fileがindexに無い
- module ownerが取れない
- dependency relationが無い
- affected outputを返却上限でtruncateした

false negative回避を削減率より優先します。

## Development routing

変更理由から最初に読むfileを絞ります。

Python:

- CLI / command contract: `script/source_structure_index.py`
- JSON I/O / external SCIP/Ctags process: `script/messenger.py`
- ast-grep outline adaptation: `script/outline_adapter.py`
- SCIP JSON adaptation: `script/scip_adapter.py`
- Universal Ctags JSON adaptation: `script/ctags_adapter.py`
- common IR / query / expansion / cycles: `script/processing.py`
- affected scope: `script/impact.py`

Native:

- build / query / expand: `tools/common/native/acr-toolbox/structure_index_command.go`
- affected scope: `structure_index_affected.go`
- SCIP adaptation / external process: `structure_scip_adapter.go`
- Universal Ctags adaptation / external process: `structure_ctags_adapter.go`
- subcommand routing: `structure_index_router.go`

Tests:

- Python adapter/processing/CLI: `tests/`
- Python Ctags adapter: `tests/test_ctags_adapter.py`
- native common contract: `structure_index_command_test.go`
- native affected: `structure_affected_command_test.go`
- native SCIP: `structure_scip_adapter_test.go`
- native Ctags: `structure_ctags_adapter_test.go`

この分割は形式上のlayeringではなく、Context Reducer自身の Task Routing / Responsibility Map / Exploration Stop / Targeted Validation をtool開発へ適用するためです。

## Validation

```sh
python -m unittest discover tools/common/large/source-structure-index/tests

cd tools/common/native/acr-toolbox
go test ./...
```

native CIはLinux / Windowsでtestし、Windows / Linux / macOSのamd64 / arm64をbuildします。
