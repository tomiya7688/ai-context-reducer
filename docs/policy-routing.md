# Policy Routing / Rule Strength

この文書は、規約全文を毎回 AI に読ませず、現在タスクに必要な規約だけを強さ・適用範囲・判定方法で選別するための方針です。

重要なのは、説明・必須規定・推奨事項・例外記録・機械判定可能な規則を分離し、現在タスクに必要なものだけを先に取得できるようにすることです。

## 1. 説明文書と規定文書を分ける

人間向けの説明と、実装時に従う規定を同じ文書へ詰め込まないことを推奨します。

```text
Guide / docs
  -> 背景、意図、例、理解補助

Specification / policy
  -> MUST / MUST NOT、適合条件、例外条件
```

AI は通常、現在タスクに関係する規定だけを先に読み、背景説明は判断に必要な場合だけ追加取得します。

## 2. Rule Strength

規約は同じ重さとして扱いません。

- Required: 必須。違反すると受け入れ不可
- Recommended: 原則推奨。理由があれば変更可能
- Advisory: 判断補助。違反とは断定しない
- Project-specific: 対象プロジェクト固有

Context Pack には現在タスクに関係する Required を優先し、Recommended / Advisory は必要なものだけ入れます。

## 3. Confidence-aware checks

静的解析や自動 checker は、確実に判定できる違反と、推測を含む警告を分けます。

```text
confirmed violation -> error
possible violation  -> warning / review target
```

不確実な設計規約を無理にエラー化しません。AI に渡す場合も、確定 finding と review candidate を混同しないようにします。

## 4. Compact exception record

規約例外が必要な場合、規約全文や長い議論を Context Pack に複製せず、最低限次を残します。

- rule / policy
- reason
- scope
- alternative / mitigation
- removal condition or future review
- source-of-truth reference

例外範囲は最小化し、無関係なファイルや将来変更へ自動拡張しません。

## 5. Language / tool adapters

共通規約と、言語・ツール固有 checker を分けます。

```text
common policy
  -> Python adapter / checker
  -> Go adapter / checker
  -> C++ adapter / checker
```

標準は特定言語の AST、CLI、ファイル構成へ依存しません。同じ規約を別実装で検査できる状態を保ちます。

## 6. Context reduction workflow

```text
Task / changed area
  ↓
Applicable required rules
  ↓
Available checker result
  ↓
Confirmed findings only
  ↓
Warnings only if relevant
  ↓
Detailed policy text only if needed
```

成功した checker の長い出力や、現在タスクに無関係な規約全文は通常コンテキストへ入れません。

## 7. 既存ツールの利用

外部ツールでは [ast-grep](https://github.com/ast-grep/ast-grep) が具体例です。ASTベースのstructural search / lint / rewriteをCLIで行え、custom ruleを使って禁止パターンやproject固有の静的規則を機械判定へ移せます。npm / pip / cargo / Homebrew / Scoop 等から導入できます。

成熟したrule engineで十分表現できる規則は、自前parser/checkerを増やす前に既存ツールで実現できないか確認します。一方、architecture semanticsやproject固有IRが必要で不自然になる規則は、専用checkerへ分離して構いません。

外部ツールリンクは [`external-tool-reference-policy.md`](external-tool-reference-policy.md) の掲載条件を満たすものだけに限定します。

## 8. 標準推奨

- 説明と規定を必要に応じて分離する
- Required / Recommended / Advisory を区別する
- 現在タスクに適用される規約だけを Context Pack へ入れる
- checker は confirmed violation と warning を分離する
- 例外は reason / scope / mitigation / removal condition を短く残す
- 共通規約と language-specific checker を分離する
- 既存rule engineで十分な規則は、自前checkerより既存ツール再利用を優先する


## Repository-local lightweight checker

literal / regexで確実に判定できる規則にはportable fallbackを利用できます。

```text
acr-toolbox policy-check --rules policy-rules.json .
python tools/common/medium/policy-check/script/policy_check.py --rules policy-rules.json .
```

対応範囲はpath include/exclude、`forbid` / `require`、literal / regex、`error` / `warning`、理由付きsuppressionです。suppressionは `acr-ignore RULE_ID: reason` をlineまたは直前lineに記録します。

AST / dataflow / architecture semanticsが必要な規則はportable checkerで確定判定せず、`semantic: true` として `unsupported_rules` に残し、ast-grep / Semgrep / project固有checker等へ委譲します。
