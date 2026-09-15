# Source Structure Index

この文書は、ソースコード全文を読む前に、構造化された解析結果を使って必要箇所へ到達するための標準方針を定義します。

この考え方は `kadoka_code_atlas` など外部プロジェクトの設計・実装を参考にしています。AI Context Reducer の標準自体は特定ツールへ依存しません。

## 1. Source Structure Index

大きなコードベースでは、AI が最初から全ファイルを読むのではなく、まずコード構造の索引を使います。

索引に含める候補:

- module / file
- class
- function / method
- qualified name
- source line range
- parameters
- parent / ownership
- calls / called-by
- import / dependency
- responsibility summary

目的はコードを要約文へ置き換えることではなく、必要な原典へ到達するための機械的な地図を作ることです。

## 2. Language-specific parser と共通 IR を分ける

```text
Source Code
    ↓
Language Parser / AST Adapter
    ↓
Common Intermediate Representation
    ↓
Relationship / Flow Analysis
    ↓
Context Routing / Diagram / Evaluation
```

AI Context Reducer 自体が全言語パーサを抱える必要はありません。解析方法はプロジェクト内ツール、別ツール、IDE、静的解析器など何を使っても構いません。

既にsemantic indexが存在する場合は、sourceを再parseするよりそのindexを再利用します。たとえばSCIPが既に生成されているrepoでは、SCIP protobuf parserをContext Reducer側へ複製するのではなく、利用可能な公式CLIや既存exportをboundary adapterとして使い、routingに必要な情報だけ共通IRへ変換します。

```text
existing semantic index
    ↓
small boundary adapter
    ↓
Common IR
    ↓
query / expand / affected
```

ここでもexternal index全文をagentへ渡すことは目的ではありません。tool内部では広く読んでよく、agent-visible resultだけを必要範囲へ削減します。

## 3. 解析結果を再利用する

共通 IR や構造インデックスから、必要に応じて次を生成できます。

- call graph
- dependency graph
- class / module relationships
- responsibility table
- sequence candidates
- fan-in / fan-out
- cycle detection
- task-specific working set
- changed fileからのaffected scope

同じコードを AI が繰り返し読み直す代わりに、解析結果を索引として再利用します。

## 4. Graph-based context expansion

```text
Target symbol
  -> direct callers / callees
  -> directly dependent modules
  -> matching tests
  -> deeper relationships only if needed
```

探索深度を制限できる場合は bounded traversal を優先します。

ただし変更影響を判定する内部closureをagent-visible output上限と混同しません。false negative回避に必要ならtool内部では全transitive dependentsを計算し、返却件数だけをboundedにします。

## 5. Fan-in / Fan-out

fan-in / fan-out は変更影響、Context Packへ追加すべき依存候補、高リスク変更、中心ノードの検出に使えます。数値だけで設計良否を断定せず、読む優先順位の補助情報として使います。

## 6. Cycle detection

循環を含む変更では、対象ファイル単体だけで判断せず、循環に含まれる要素を一つの working set として扱うことを推奨します。

## 7. Generated diagrams は索引の派生物

図そのものより元になった構造データを優先します。

```text
Common IR / Structure Index
  -> compact relationships
  -> diagrams when useful
```

## 8. Deterministic analysis を優先する

AST、シンボル、呼び出し関係、依存関係など機械的に取得できる情報は、可能なら決定論的な解析を優先します。LLM 補助解析を使う場合は、決定論的解析結果と区別します。

## 9. 実装例・参考実装

`kadoka_code_atlas` は、Source Structure Index、共通 IR、call graph、bounded traversal などを実装する参考例の一つです。

外部ツールでは次を具体例として扱えます。

- [SCIP](https://github.com/scip-code/scip): language-agnosticなcode intelligence index protocol / CLI。対応indexerがある言語ではdefinition / reference等の索引を再利用しやすい。
- [Tree-sitter](https://github.com/tree-sitter/tree-sitter): 多数の言語を扱えるincremental parsing library。軽量な構文構造抽出や独自language adapterの基盤として使える。

既存のIDE / language server / build systemが同等情報を既に持つなら、そちらを再利用する方を優先します。

### Repository-owned minimal implementation

このrepositoryでは `tools/common/large/source-structure-index` を軽量な共通IR / routing層として提供します。

これはSCIPやTree-sitterそのものを再実装するものではありません。既存のlanguage-specific analyzerが生成したsymbol / dependency graph JSON、`ast-grep outline`、既存SCIP index等を共通IRへ正規化し、full indexはfileへ保存します。agentへは `query` / `expand` / `affected` で必要な部分だけを返します。

現在の最小実装では次を扱います。

- file / module / symbol node
- ownership / dependency edge
- exact / partial node query
- bounded in/out/both traversal
- fan-in / fan-out
- traversal範囲内のcycle group
- changed fileからのreverse dependency affected scope
- input側のtruncation伝播
- external backend unavailable / malformed outputの明示

Pythonでは `python-symbols` と `python-module-graph`、Goでは `go-symbols` と `go-package-graph` の出力をそのまま材料にできます。既存SCIP indexは、SCIP CLIが利用可能なら外部boundary経由で読みます。CLIやindexerを自動installしません。

外部ツールリンクは [`external-tool-reference-policy.md`](external-tool-reference-policy.md) の掲載条件を満たすものだけに限定します。

この位置付けでは次を守ります。

- 標準仕様の成立条件にはしない
- 特定CLIやファイル形式を標準にしない
- 外部側が進化しても自動追従しない
- 有効な新手法だけ改めて一般化する
- 同じ標準を別実装でも満たせるようにする

## 10. 標準推奨

- ソース全文を読む前に構造インデックスを利用できるなら利用する
- 言語固有 parser と共通 IR を分離する
- 既存semantic indexがある場合は再parseより再利用を優先する
- 同じ解析結果を複数用途で再利用する
- 対象シンボルから bounded graph traversal で周辺情報を広げる
- impact correctnessに必要な内部closureとagent-visible output上限を分離する
- fan-in / fan-out / cycle を読む優先順位の補助情報として使う
- generated diagrams を原典や IR の代替にしない
- 機械取得可能な情報は deterministic analysis を優先する
- 既存の高品質なcode intelligence / parserが使える場合は独自実装より再利用を優先する
