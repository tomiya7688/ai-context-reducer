# source-structure-index

既存のlanguage-specific analyzerが出したsymbol / dependency graph JSONを、再利用可能な共通IRへ束ねます。

目的は巨大なindexをagentへ毎回読ませることではありません。indexはfileへ保存し、agentには `query` / `expand` で必要な候補・周辺graphだけを返します。

このtoolは `docs/source-structure-index.md` の次の既存手法を最小実装します。

- language-specific parser と common IR の分離
- deterministic analysis result の再利用
- symbol / file / module index
- bounded graph traversal
- fan-in / fan-out
- cycle group detection

SCIPやTree-sitterそのものを再実装するものではありません。既存analyzer / IDE / indexerが利用可能なら、その出力をrouting用IRへ変換して再利用するための軽量層です。

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

`build` はfull indexをstdoutへ出しません。stdoutは `node_count` / `edge_count` / `input_truncated` などのcompact JSONだけです。

## Query

```sh
python tools/common/large/source-structure-index/script/source_structure_index.py query \
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

出力には各nodeの `distance` / `fan_in` / `fan_out`、選択範囲内の `cycle_groups`、`nodes_truncated` が含まれます。

曖昧なtargetでは勝手に1つを選ばず `status=target_ambiguous` と候補だけを返します。

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

## Development routing

変更理由から最初に読むfileを絞ります。

- CLI / command contract: `script/source_structure_index.py`
- JSON file I/O: `script/messenger.py`
- IR normalization / query / graph expansion / cycle detection: `script/processing.py`
- deterministic contract validation: `tests/test_processing.py`

この分割は形式上のlayeringではなく、Context Reducer自身の Task Routing / Responsibility Map / Exploration Stop をtool開発へ適用するためです。
