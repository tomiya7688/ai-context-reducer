# Measured Context-Reduction Benchmark

> Japanese version: [コンテキスト削減の実測ベンチマーク](../../jp/AI利用/コンテキスト削減の実測ベンチマーク.md)

This document explains a reproducible way to measure how much AI-visible input changes when candidate files are narrowed before they are given to an AI.

The numbers below are not a universal reduction rate for real repositories. They come from a fixed synthetic repository and three fixed tasks that compare a **read-all baseline** with a **search-first context-reduced strategy**.

## What is compared

The benchmark lives under `benchmarks/context-reduction/`. Its fixture contains five independent features: settings, profile, notification, report, and cache. Each feature has one implementation file, one test file, and one document, for 15 eligible files in total.

### Read-all baseline

The `baseline` sends every eligible `.py` and `.md` fixture file to the AI-visible context.

This does not claim that ordinary developers always read every file. It is a fixed baseline for comparing broad AI input with a search-first strategy.

### Search-first strategy

The `context_reduced` strategy runs a mechanical literal search over the same 15 files and only sends matching files to the AI-visible context.

A mechanical search may scan all 15 files without sending their full contents to the model. The benchmark therefore records **mechanically scanned files** separately from **files opened for AI context**.

## The same tasks and required evidence

The three tasks are fixed in `benchmarks/context-reduction/tasks.json`.

| Task | Required evidence |
| --- | --- |
| Prepare a change that adds the failing file path to an invalid `settings.json` error | `src/settings.py`, `tests/test_settings.py`, `docs/settings.md` |
| Verify how `display_name` whitespace is normalized | `src/profile.py`, `tests/test_profile.py`, `docs/profile.md` |
| Prepare a retry change that must not retry permanent notification failures | `src/notifier.py`, `tests/test_notifier.py`, `docs/notifier.md` |

Both strategies are checked against the same required-evidence list. A smaller input does not count as a success if required evidence is missing.

In the committed fixture, both strategies include all required evidence for all three tasks.

## Current fixed-fixture result

The committed `reference-results.json` reports:

| Task | Read all | Search first | File reduction | Character reduction |
| --- | ---: | ---: | ---: | ---: |
| settings | 15 files / 4,826 chars | 3 files / 1,328 chars | 80.0% | 72.5% |
| profile | 15 files / 4,826 chars | 3 files / 1,032 chars | 80.0% | 78.6% |
| notification | 15 files / 4,826 chars | 3 files / 1,183 chars | 80.0% | 75.5% |
| three-task total | 45 files / 14,478 chars | 9 files / 3,543 chars | 80.0% | 75.5% |

Across the three fixed tasks, the AI-visible file count falls from 45 to 9 and the character count falls from 14,478 to 3,543, while both strategies retain all predefined required evidence.

The **75.5%** figure is only a measurement for this fixture and these tasks. It is not a claim that every project using ai-context-reducer will reduce context by 75.5%.

## Why the reference result does not claim token measurements

The committed reference does not measure tokens.

Tokenization depends on the target model and tokenizer. Dividing character count by a constant without running the target tokenizer would be an estimate, not a measured input-token count.

`benchmark.py --chars-per-token` can produce an explicitly labeled `estimated_tokens` value from a user-supplied ratio. The committed reference leaves that field unset.

When a real environment exposes model-specific tokenizer output or API usage, use that source for actual token comparisons.

## Reproduce the result

From the repository root:

```bash
python3 benchmarks/context-reduction/benchmark.py
```

To verify that the fixture still matches the committed result:

```bash
python3 benchmarks/context-reduction/benchmark.py --check-reference
```

A successful check prints:

```text
context-reduction benchmark reference matches
```

The `Context reduction benchmark` GitHub Actions workflow runs the same check.

## What this benchmark measures

It records:

- files selected for AI-visible context;
- characters in those files;
- UTF-8 bytes;
- files mechanically scanned;
- files opened for AI context;
- whether predefined required evidence is complete.

It does not, by itself, measure:

- actual input tokens for a particular LLM;
- API cost;
- response latency;
- generated-code quality;
- average reduction in real repositories;
- human search time.

The result therefore measures context selection, not end-to-end model quality.

## Keeping the baseline honest

The baseline is fixed as "send every eligible fixture text file." The fixture, tasks, search terms, required evidence, measurement script, and reference result are all committed.

Do not add irrelevant dummy files only to make the baseline look worse, and do not give the reduced strategy hidden knowledge of the oracle files.

## Measuring a real project

Use the same task and completion criteria for both strategies:

1. Record the files and documents sent under the baseline.
2. Record the files and documents sent after search or routing.
3. Compare file count, text size, and token count only when a real tokenizer or usage metric is available.
4. Record whether both strategies inspected the required specification, implementation, tests, errors, and other evidence.
5. Do not call the smaller input a success if verification quality is weaker.
6. Do not present one result as a universal reduction rate.

The purpose is not to minimize a number. It is to avoid sending information the task does not need while preserving the evidence required to make and verify the change.

## Estimate usage by task kind

See [Build context-use estimates for each kind of task](estimate-context-use-by-task.md) for distinguishing input, output, and cumulative usage and recording comparable measurements.
