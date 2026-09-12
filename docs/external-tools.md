# External Tools

`ai-context-reducer` は、既存の高品質な外部ツールで代替できる処理を無理に再実装しません。

目的は「ツールを増やすこと」ではなく、AI が読む情報量を減らすことです。利用可能な外部ツールがあれば、自前の簡易解析より優先して構いません。

## 推奨ツール

| Tool | 主用途 | 向いている場面 | ai-context-reducer での位置づけ |
|---|---|---|---|
| `ripgrep (rg)` | 高速テキスト検索 | ほぼ全repo | Search-first / Read-second の第一候補 |
| `fd` | 高速ファイル探索 | ファイル数が多いrepo | 対象ファイル候補の絞り込み |
| `ast-grep` | AST構造検索・置換 | 中〜大規模、多言語 | regexより正確な構造検索 |
| `Universal Ctags` | symbol index | 中〜大規模、多言語 | Source Structure Index の軽量実装 |
| `Tree-sitter` | 構文木生成 | 精密解析ツールを作る場合 | 言語固有parserの共通基盤候補 |
| `scc` | LOC・言語・複雑度概要 | 導入前のrepo分析 | repo-profile の高機能代替/補助 |
| `git-sizer` | Git履歴・repoサイズ健全性 | 巨大/長寿命repo | 大容量履歴・巨大blob検出 |
| `Semgrep` | 静的解析・policy check | 規約が多いrepo | 機械判定可能な規約をAI文脈外へ移す |

## 選び方

### ほぼ全プロジェクト

`rg` を最優先候補とします。全文を順番に読む代わりに、キーワード・symbol・エラー文・見出しを先に検索します。

`fd` がある場合は、ファイル探索を `find` や全tree列挙より短くできます。

### 中〜大規模コードベース

symbol探索が多い場合は `ctags`、構文ベース検索が必要なら `ast-grep` を推奨します。

自前の regex-based symbol tools は依存なしのfallbackとして残し、外部ツールが利用できる場合はそちらを優先できます。

### 独自解析ツールを作る場合

複数言語を正確に解析したい場合は `Tree-sitter` を候補にします。

ただし、小規模repoの導入時に parser runtime や grammar を大量追加する必要はありません。導入コストが削減効果を上回る場合は使いません。

### 巨大repo

`git-sizer` でGit履歴・巨大objectの問題を確認し、`scc` で言語構成・コード量・複雑度を短く把握できます。

巨大repoでは「現在のソース量」と「Git履歴の重さ」を別に扱います。

### 規約が多いrepo

機械判定できる規約は `Semgrep` や既存lint/checkerへ移し、AIには成功結果またはcompact findingsだけ渡します。

semantic ownership や設計責務など自動判定しにくいものは targeted review に残します。

## 外部ツール検出

`tools/common/small/external-tool-probe/script/external_tool_probe.py` で代表ツールが PATH 上にあるか確認できます。

```text
python tools/common/small/external-tool-probe/script/external_tool_probe.py
```

存在しないツールを自動インストールはしません。対象環境・CI・開発者の方針を確認した上で導入します。

## 原則

- 外部ツールの導入自体が大きな負担なら使わない。
- 既存のrepo標準ツールがある場合はそれを優先する。
- 外部ツール出力も bounded / compact に扱う。
- 解析結果は原典への索引であり、Source of Truth にはしない。
- security scanner の結果は用途と解析範囲を理解した上で扱う。
