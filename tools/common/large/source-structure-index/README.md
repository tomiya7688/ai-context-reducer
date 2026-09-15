# source-structure-index

既存のlanguage-specific analyzerが出したsymbol / dependency graph JSONを、再利用可能な共通IRへ束ねます。

目的は巨大なindexをagentへ毎回読ませることではありません。indexはfileへ保存し、agentには `query` / `expand` / `affected` で必要な候補・周辺graphだけを返します。

このtoolは `docs/source-structure-index.md` と `docs/change-impact-routing.md` の次の既存手法を最小実装します。

- language-specific parser と common IR の分離
- deterministic analysis result の再利用
- symbol / file / module index
- bounded graph traversal
- fan-in / fan-out
- cycle group detection
- changed fileからのdependency-based affected scope

SCIPやTree-sitterそのもの、Nx/Pantsのbuild graphそのものを再実装するものではありません。既存analyzer / IDE / indexer / build graphが利用可能なら、その結果を再利用することを優先します。

## Implementations

同じ `acr-source-structure-index-v1` を、共有コードなしで2実装します。

- Python: `script/source_structure_index.py`
- native Go: `tools/common/native/acr-toolbox structure-index`

片方でbuildしたindexを、もう片方の `query` / `expand` / `affected` で読める契約です。

Python版は追加のinput adapterとして `ast-grep outline` JSONを直接受けられます。これはindex format自体を変えるものではなく、既存external analyzerの結果を共通IRへ入れるためのboundary adapterです。

## Build

Python symbols + Python module graph:

```sh
python tools/python/small/python-symbols/script/python_symbols.py src > /tmp/symbols.json
python tools/python/large/python-module-graph/script/python_module_graph.py . > /tmp/graph.json
python tools/common/large/source-structure-index/script/source_structure_index.py build \
  --symbols /tmp/symbols.json \
  --graph /tmp/graph.json \
  --root . \
  --output .acr/source-structure-index.json
```

Go analyzer outputも同じ入力契約で利用できます。

```sh
go run ./tools/go/small/go-symbols ./src > /tmp/go-symbols.json
go run ./tools/go/large/go-package-graph . > /tmp/go-graph.json
python tools/common/large/source-structure-index/script/source_structure_index.py build \
  --symbols /tmp/go-symbols.json \
  --graph /tmp/go-graph.json \
  --root . \
  --output .acr/source-structure-index.json
```

既に `ast-grep` が利用可能な環境では、そのoutlineを再利用できます。追加installは行いません。

```sh
ast-grep outline src --json=compact > /tmp/outline.json
python tools/common/large/source-structure-index/script/source_structure_index.py build \
  --symbols /tmp/outline.json \
  --root . \
  --output .acr/source-structure-index.json
```

adapterはoutlineのnested `members` をflattenしつつ、`owner_qualified_name` を共通IRの `owns` edgeへ変換します。そのため class / method等のownershipを失わずbounded expansionできます。line numberは共通IRでは1-basedです。signatureはbounded metadataとして保持します。

native版:

```sh
acr-toolbox structure-index build \
  --symbols /tmp/symbols.json \
  --graph /tmp/graph.json \
  --root . \
  --output .acr/source-structure-index.json
```

`build` はfull indexをstdoutへ出しません。stdoutは `node_count` / `edge_count` / `input_truncated` などのcompact JSONだけです。

## Query

```sh
python tools/common/large/source-structure-index/script/source_structure_index.py query \
  .acr/source-structure-index.json Service
```

native版ではflagをpositional引数より前に置きます。

```sh
acr-toolbox structure-index query --max-results 40 \
  .acr/source-structure-index.json Service
```

`id` / `name` / `qualified_name` / `path` を検索します。既定では40件まで返します。

## Bounded expansion

```sh
python tools/common/large/source-structure-index/script/source_structure_index.py expand \
  .acr/source-structure-index.json module:pkg.service \
  --depth 2 \
  --max-nodes 80 \
  --direction both
```

native版:

```sh
acr-toolbox structure-index expand --depth 2 --max-nodes 80 --direction both \
  .acr/source-structure-index.json module:pkg.service
```

出力には各nodeの `distance` / `fan_in` / `fan_out`、選択範囲内の `cycle_groups`、`nodes_truncated` が含まれます。

曖昧なtargetでは勝手に1つを選ばず `status=target_ambiguous` と候補だけを返します。

## Dependency-based affected scope

Nx / Pants等で使われる「changed targetからdependentを求める」考え方の軽量fallbackです。既存のbuild graphがある場合はそちらをSource of Truthとして優先します。

Python:

```sh
python tools/common/large/source-structure-index/script/source_structure_index.py affected \
  .acr/source-structure-index.json \
  --changed src/core.py \
  --changed src/schema.py \
  --max-results 80
```

native:

```sh
acr-toolbox structure-index affected \
  --changed src/core.go \
  --max-results 80 \
  .acr/source-structure-index.json
```

内部では `contains_file` からchanged fileのmodule/packageを特定し、`depends_on` edgeを逆向きに**全transitive closure**まで辿ります。`--max-results` はagentへ返す件数だけを制限し、内部のimpact計算自体は途中で打ち切りません。

返却上限を超えた、changed fileがindexに無い、module ownershipが無い、index自体がtruncated、dependency edgeが無い場合は `impact_uncertain=true` とし、`recommended_validation_scope=broader_or_full` へ倒します。削減率よりfalse negative回避を優先します。

## Input contract

### Symbol analyzer

既存のPython / Go symbols形式を受けます。

```json
[
  {
    "file": "src/example.py",
    "symbols": [
      {"kind": "ClassDef", "name": "Example", "line": 10}
    ]
  }
]
```

Python版では `ast-grep outline --json=compact` のfile/item形式も自動判定します。通常のsymbol payloadは変換せずそのまま扱います。

### Graph analyzer

既存module/package graph形式を受けます。`kind` が無いedgeは `depends_on` として扱います。

```json
{
  "edges": [
    {"from": "pkg.a", "to": "pkg.b"}
  ],
  "truncated": false
}
```

将来のcall graph等は、明示的な `nodes` と `edges[].kind` を持つJSONを入力できます。

## Validation

Python:

```sh
python -m unittest discover tools/common/large/source-structure-index/tests
```

native Go:

```sh
cd tools/common/native/acr-toolbox
go test ./...
```

## Development routing

変更理由から最初に読むfileを絞ります。

- Python CLI / command contract: `script/source_structure_index.py`
- Python JSON file I/O: `script/messenger.py`
- external outline input adaptation: `script/outline_adapter.py`
- IR normalization / query / graph expansion / cycle detection: `script/processing.py`
- affected-scope logic: `script/impact.py`
- outline adapter validation: `tests/test_outline_adapter.py`
- affected-scope validation: `tests/test_impact.py`
- Python deterministic contract validation: `tests/test_processing.py`
- Python end-to-end CLI smoke: `tests/test_cli.py`
- native build/query/expand: `tools/common/native/acr-toolbox/structure_index_command.go`
- native affected scope: `tools/common/native/acr-toolbox/structure_affected_command.go`
- native structure command routing: `tools/common/native/acr-toolbox/structure_index_router.go`
- native affected validation: `tools/common/native/acr-toolbox/structure_affected_command_test.go`

この分割は形式上のlayeringではなく、Context Reducer自身の Task Routing / Responsibility Map / Exploration Stop をtool開発へ適用するためです。
