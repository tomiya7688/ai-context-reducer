# Boilerplate Generation / Canonical Templates

> Japanese Source of Truth: [定型文と定型ファイルを生成する](../jp/定型文と定型ファイルを生成する.md)

For text, notices, license guidance, headers, configuration fragments, and other artifacts whose content is mostly repeated, prefer generating them from a canonical template and a small set of variables instead of asking an AI to regenerate and compare the full text every time.

The key is to separate the stable source template from the values that are allowed to change.

## Purpose

```text
canonical template
  + project-specific variables
  ↓
generated artifact
  ↓
AI inspects only variables / diff / validation result
```

Having an AI rewrite boilerplate in full on every task consumes context and increases the chance of wording drift, missing fields, and unintended edits.

## Canonical source

Keep a template / policy / clause set as the original source, separate from the generated artifact.

Examples:

- license template
- copyright notice
- attribution block
- generated README section
- release notice
- configuration header
- standard disclaimer

Do not make the generated artifact the Source of Truth. Preserve a path back to the template and input values.

## Variable-first context

When possible, pass only the parts that can change instead of the full generated text.

Example:

```text
Template: character-license-v1
Name: Example Character
Version: 1.2
Repository: owner/repo
Credit required: no
Redistribution: allowed with conditions
```

If the template itself has not changed, the generated full text normally does not need to enter AI context.

## Versioned template

For legal, policy, or public text where meaning changes matter, make the template version explicit.

At generation time, it is useful to track at least:

- template identifier
- template version
- input variables
- output path
- generated / checked status

When useful, keep a hash or commit reference so the exact source can be identified.

## Generated artifact validation

A successful generation command does not by itself prove that the output is correct.

Depending on the use case, check at least:

- required variables are not empty
- no placeholder remains unresolved
- expected sections exist
- output encoding / line ending
- generated artifact matches the current template

The generator cannot by itself guarantee legal validity or project suitability. Treat it as a mechanism for consistently expanding an already approved template.

## Context reduction rule

During normal work, do not make the AI read generated boilerplate in full.

Start with:

```text
current template version
+ changed variables
+ generated diff / validation result
```

Read the full template or generated output only when the template itself changes, a legal/contractual judgment is required, or the generated diff looks abnormal.

## Possible common tool

A common generator may live under `tools/<tool-name>/script/`.

Example:

```text
tools/boilerplate-generator/script/
```

Possible capabilities:

- template listing
- variables file / CLI input
- preview / dry-run
- output generation
- unresolved-placeholder check
- template version / source metadata
- generated diff
- check-only mode

Even for license generation, the tool should select and expand an approved template rather than invent legal terms.

## Reuse existing tools

**Copier** is one strong external option. It can generate project scaffolds from Jinja2-based templates and variables, and it also focuses on lifecycle management for updating existing projects after the template evolves. This makes it useful when canonical templates require long-term maintenance rather than one-time generation.

If simple initial scaffolding is sufficient, Cookiecutter or another mature template generator may be enough. The important point is not the product name: if an existing tool can adequately implement `template + variables -> generated artifact`, do not create a custom generator.

Project skeletons, CI configuration, shared README sections, and configuration sets can often be delegated to such tools while AI Context Reducer focuses on the context rule: inspect template version, changed inputs, and validation instead of reading generated output in full.

## Standard recommendations

- separate boilerplate into canonical template + variables
- do not make generated artifacts the Source of Truth
- prefer changed variables / generated diff over full generated text in AI context
- keep template version and source traceable
- move mechanically checkable conditions such as placeholders / required sections into the generator
- do not make the generator responsible for legal validity itself
- prefer reuse of a mature template generator when it is sufficient
- if a common generator is added, avoid making a particular license or external repository a mandatory dependency

## Repository-local portable generator

For simple replacement, a portable fallback is available.

```text
acr-toolbox template --template templates/foo --vars vars.json --out generated/foo --template-id foo --template-version 1
python tools/common/medium/template/script/template.py --template templates/foo --vars vars.json --out generated/foo
```

It supports `{{name}}` placeholders, file / directory templates, required variables, unresolved-placeholder checks, dry-run, check-only, compact diff hints, template id/version, and variables SHA-256. Generation also records metadata in a sidecar or output directory.

If Copier / Cookiecutter is already available, the tool may report that availability, but it does not auto-install those tools or reimplement a fully compatible engine.
