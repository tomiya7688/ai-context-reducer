# External Tools

`ai-context-reducer` は、既存の高品質な外部ツールで代替できる処理を無理に再実装しません。

目的は「ツールを増やすこと」ではなく、AI が読む情報量を減らすことです。利用可能な外部ツールがあれば、自前の簡易解析より優先して構いません。

## 推奨ツール

| Tool | 主用途 | 向いている場面 | ai-context-reducer での位置づけ |
|---|---|---|---|
| `ripgrep (rg)` | 高速テキスト検索 | ほぼ全repo | Search-first / Read-second の第一候補 |
| `fd` | 高速ファイル探索 | ファイル数が多いrepo | 対象ファイル候補の絞り込み |
| `ast-grep` | AST構造検索・outline | 中〜大規模、多言語 | `structural-search` backend / Source Structure Index inputとして再利用 |
| `Universal Ctags` | multi-language symbol index | 中〜大規模、多言語 | `source-structure-index` の既存symbol backendとして再利用 |
| `SCIP` | semantic code intelligence index | semantic indexを既に生成できるrepo | `source-structure-index` のsymbol/dependency backendとして再利用 |
| `Tree-sitter` | 構文木生成 | 精密解析ツールを作る場合 | 言語固有parserの共通基盤候補。低品質な再実装はしない |
| `scc` | LOC・言語・複雑度概要 | 導入前のrepo分析 | repo-profile の高機能代替/補助 |
| `git-sizer` | Git履歴・repoサイズ健全性 | 巨大/長寿命repo | 大容量履歴・巨大blob検出 |

## 選び方

### ほぼ全プロジェクト

`rg` を最優先候補とします。全文を順番に読む代わりに、キーワード・symbol・エラー文・見出しを先に検索します。

`fd` がある場合は、ファイル探索を `find` や全tree列挙より短くできます。

### 中〜大規模コードベース

symbol探索が多い場合はUniversal Ctags、構文ベース検索が必要なら `ast-grep` を優先候補にします。

`source-structure-index` は、既存Universal Ctags JSON Linesを `--ctags-json`、既にインストール済みのUniversal Ctagsを `--ctags-source` で利用できます。full tag outputをagentへ流さず、file / symbol / scope ownershipへ圧縮して `query` / `expand` から再利用します。

SCIP indexがある場合は `--scip` / `--scip-json` で同じ共通IRへ取り込めます。SCIPはcross-file dependencyも持てるため、`affected` routingではCtags単独より高精度なSource of Truthになり得ます。

`ast-grep` は `structural-search` の高品質backendとして利用し、`ast-grep outline` のJSONはSource Structure Index inputとしても利用できます。

自前のregex/stdlib-based toolsは依存なしfallbackとして残します。外部toolを自動インストールはしません。

### 独自解析ツールを作る場合

複数言語を正確に解析したい場合は `Tree-sitter` を候補にします。

ただし、小規模repoの導入時にparser runtimeやgrammarを大量追加する必要はありません。既存parser/indexerが利用可能なら再利用し、Context Reducer内に別のmulti-language parserを複製しないことを優先します。

### 巨大repo

`git-sizer` でGit履歴・巨大objectの問題を確認し、`scc` で言語構成・コード量・複雑度を短く把握できます。

巨大repoでは「現在のソース量」と「Git履歴の重さ」を別に扱います。

### 規約が多いrepo

機械判定できる規約はrepository標準のlint/checkerへ移し、AIには成功結果またはcompact findingsだけ渡します。

semantic ownershipや設計責務など自動判定しにくいものはtargeted reviewに残します。

## 外部ツール検出

`tools/common/small/external-tool-probe/script/external_tool_probe.py` で代表ツールがPATH上にあるか確認できます。

```text
python tools/common/small/external-tool-probe/script/external_tool_probe.py
```

存在しないツールを自動インストールはしません。対象環境・CI・開発者の方針を確認した上で導入します。

## 原則

- 外部ツールの導入自体が大きな負担なら使わない。
- 既存のrepo標準ツールがある場合はそれを優先する。
- 外部ツール出力も bounded / compact に扱う。
- 解析結果は原典への索引であり、Source of Truth にはしない。
- 高品質な外部index/parserを再利用できる場合、同じ解析器を別実装しない。
