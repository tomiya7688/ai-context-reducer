# Policy Routing / Rule Strength

> Japanese Source of Truth: [規則の確認先を絞る](../jp/規則の確認先を絞る.md)

This document describes how to avoid feeding the full policy set to an AI on every task by selecting only rules relevant to the current work according to strength, scope, and checking method.

The key is to separate explanatory material, mandatory rules, recommendations, exception records, and machine-checkable rules so that the current task can retrieve only what it needs.

## 1. Separate explanatory and normative documents

When practical, do not pack human-facing explanation and implementation rules into the same document.

```text
Guide / docs
  -> background, intent, examples, explanation

Specification / policy
  -> MUST / MUST NOT, conformance conditions, exception conditions
```

Normally, an AI should read only rules relevant to the current task first and retrieve background explanation only when it is needed for a decision.

## 2. Rule Strength

Do not treat every policy statement as equally strong.

- Required: mandatory; violation makes the result unacceptable
- Recommended: preferred by default; may be changed with a reason
- Advisory: decision support; do not treat deviation as a confirmed violation
- Project-specific: applies only to the target project

In a Context Pack, prioritize Required rules that apply to the current task and include only the Recommended / Advisory material that is actually needed.

## 3. Confidence-aware checks

Static analysis and automated checkers should distinguish confirmed violations from findings that include uncertainty.

```text
confirmed violation -> error
possible violation  -> warning / review target
```

Do not force uncertain architectural rules into hard errors. When passing results to an AI, keep confirmed findings separate from review candidates.

## 4. Compact exception record

When a policy exception is necessary, do not copy the full policy or a long discussion into the Context Pack. Record only:

- rule / policy
- reason
- scope
- alternative / mitigation
- removal condition or future review
- Source-of-Truth reference

Keep exception scope as small as possible and do not automatically extend it to unrelated files or future changes.

## 5. Language / tool adapters

Separate common policy from language- or tool-specific checkers.

```text
common policy
  -> Python adapter / checker
  -> Go adapter / checker
  -> C++ adapter / checker
```

The standard should not depend on a particular language AST, CLI, or file structure. Keep it possible to check the same policy with another implementation.

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

Do not place long successful-checker output or the full text of unrelated policies into normal context.

## 7. Reuse existing tools

[ast-grep](https://github.com/ast-grep/ast-grep) is one concrete external example. It supports AST-based structural search / lint / rewrite through a CLI and can move forbidden patterns or project-specific static rules into machine checks through custom rules. It can be installed through npm / pip / cargo / Homebrew / Scoop and similar channels.

Before adding a custom parser/checker, first consider whether a mature rule engine can express the rule. If a rule needs architecture semantics or a project-specific IR and becomes unnatural in a generic engine, a dedicated checker is acceptable.

Only link external tools that satisfy [External Tool Reference Policy](external-tool-reference-policy.md).

## 8. Standard recommendations

- separate explanation from normative policy when useful
- distinguish Required / Recommended / Advisory
- put only policies that apply to the current task into the Context Pack
- distinguish confirmed violations from warnings in checkers
- keep exception reason / scope / mitigation / removal condition compact
- separate common policy from language-specific checkers
- prefer reuse of an existing rule engine when it can express the rule well

## Repository-local lightweight checker

Portable fallbacks can handle rules that can be decided reliably with literal / regex checks.

```text
acr-toolbox policy-check --rules policy-rules.json .
python tools/common/medium/policy-check/script/policy_check.py --rules policy-rules.json .
```

Supported scope includes path include/exclude, `forbid` / `require`, literal / regex, `error` / `warning`, and reasoned suppression. A suppression uses `acr-ignore RULE_ID: reason` on the relevant line or immediately preceding line.

Rules that require AST / dataflow / architecture semantics are not confirmed by the portable checker. Mark them with `semantic: true`, leave them in `unsupported_rules`, and delegate them to ast-grep / Semgrep / project-specific checkers or similar tools.
