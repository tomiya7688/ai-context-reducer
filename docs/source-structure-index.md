# Source Structure Index

この文書は、ソースコード全文を読む前に、構造化された解析結果を使って必要箇所へ到達するための標準方針を定義します。

この考え方は `kadoka_code_atlas` など外部プロジェクトの設計・実装を参考にしていますが、AI Context Reducer は特定の外部ツールや外部リポジトリへ依存しません。外部プロジェクトは実例・参考元として扱い、標準へ取り込むのは再利用可能な手法だけです。

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

言語ごとの AST / parser は異なっていても、後段で必要な情報は共通化できる場合があります。

推奨構造:

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

AI Context Reducer 自体が全言語パーサを抱える必要はありません。

解析方法はプロジェクト内ツール、別ツール、IDE、静的解析器など何を使っても構いません。標準側では「どのような構造情報を Context Routing に利用するか」だけを定義します。

## 3. 解析結果を再利用する

同じソースを用途ごとに何度も解析しないことを推奨します。

共通 IR や構造インデックスから、必要に応じて次を生成できます。

- call graph
- dependency graph
- class / module relationships
- responsibility table
- sequence candidates
- fan-in / fan-out
- cycle detection
- task-specific working set

コンテキスト削減の観点では、同じコードを AI が繰り返し読み直す代わりに、解析結果を索引として再利用することが重要です。

## 4. Graph-based context expansion

現在タスクの対象シンボルが分かっている場合、周辺コードを無制限に読むのではなく、グラフ上の近傍から段階的に広げます。

例:

```text
Target symbol
  -> direct callers / callees
  -> directly dependent modules
  -> matching tests
  -> deeper relationships only if needed
```

探索深度を制限できる場合は bounded traversal を優先します。

## 5. Fan-in / Fan-out を読む優先度に使う

多数から参照される要素は変更影響が大きい可能性があります。

逆に、多数を呼び出す要素は責務集中や orchestration の中心である可能性があります。

そのため、fan-in / fan-out は次の用途に利用できます。

- 変更影響の推定
- Context Pack に追加すべき依存候補の選定
- 高リスク変更の検出
- 専用の追加確認が必要な中心ノードの検出

数値だけで設計良否を断定せず、読む優先順位を決めるヒントとして使います。

## 6. Cycle detection

循環依存や呼び出し循環が検出できる場合、通常より広いコンテキストが必要になる可能性があります。

循環を含む変更では、対象ファイル単体だけで判断せず、循環に含まれる要素を一つの working set として扱うことを推奨します。

## 7. Generated diagrams は索引の派生物

Mermaid などの図は有用ですが、Context Pack に常時入れる必要はありません。

図そのものより、元になった構造データを優先します。

```text
Common IR / Structure Index
  -> compact relationships
  -> diagrams when useful
```

図は人間向け理解、レビュー、複雑性確認には有効ですが、AI の通常作業では必要な関係だけをテキストで取得できる方がコンテキスト効率が高い場合があります。

## 8. Deterministic analysis を優先する

AST、シンボル、呼び出し関係、依存関係など機械的に取得できる情報は、可能なら決定論的な解析を優先します。

LLM に推測させる必要がない情報を毎回 AI に再解析させないことで、コンテキスト消費と誤認の両方を減らします。

LLM 補助解析を使う場合は、決定論的解析結果と区別します。

## 9. 外部ツール・外部プロジェクトの扱い

外部リポジトリは参考実装として扱います。

- 標準仕様の必須依存にしない
- 特定ツールのファイル形式や CLI を前提にしない
- 外部ツールが停止・変更・廃止されても標準が成立するようにする
- 有効な手法は抽象化して文書化する
- 必要なら同等機能を別実装へ置き換えられるようにする

`kadoka_code_atlas` は Source Structure Index、共通 IR、call graph、bounded traversal などの参考元の一つです。利用できる場合に補助ツールとして使うことはできますが、AI Context Reducer の標準ワークフロー成立条件には含めません。

## 10. 標準推奨

- ソース全文を読む前に構造インデックスを利用できるなら利用する
- 言語固有 parser と共通 IR を分離する
- 同じ解析結果を複数用途で再利用する
- 対象シンボルから bounded graph traversal で周辺情報を広げる
- fan-in / fan-out / cycle を読む優先順位の補助情報として使う
- generated diagrams を原典や IR の代替にしない
- 機械取得可能な情報は deterministic analysis を優先する
- 外部ツールを使う場合も標準仕様自体はそのツールに依存させない
