# Build context-use estimates for each kind of task

> Japanese source: [作業ごとのコンテキスト使用量の目安を作る](../../jp/AI利用/作業ごとのコンテキスト使用量の目安を作る.md)

A short question, a one-file change, and a repository-wide investigation need different material and numbers of interactions. Rather than assigning one token count to “coding,” use past tasks with similar reading scope and workflows to build estimates for your environment.

Separate **input supplied in one call** from **cumulative usage across the task**. Published numbers are conditional examples, not general averages for short questions or one-file changes.

## Identify what increases usage for each task

| Task | Initial material | Main drivers of higher usage | How to request the work |
| --- | --- | --- | --- |
| Short question | Question, assumptions, and a short necessary example | Long inherited conversations or whole documents | Provide only current prerequisites |
| One-file change | Target processing, specification, users, and relevant tests | Whole large files, repeated failing tests and fixes | Start with relevant functions; add dependencies when needed |
| Changes across files | Exchange formats, callers and callees, affected tests | Repeated reading, missed changes, long diffs | Keep shared specifications in one place; separate change units |
| Repository-wide investigation | Criteria, target inventory, inspected scope | Many files, full logs, similar candidates | Record results and uninspected areas by folder or feature |

File count alone does not determine the order of usage. A difficult one-file bug with repeated checks can consume more than simple changes to several files. Mechanically searched files also differ from files whose contents reach the AI.

## Decide which quantity to count

Tokens are small units the AI uses to process text or code. Segmentation differs by model, so characters and tokens are not equivalent.

| Quantity | Meaning | What it helps assess |
| --- | --- | --- |
| Input tokens per call | Instructions, history, code, tool results, and other input supplied that round | Whether individual inputs are becoming large |
| Output tokens per call | Content generated that round | Growth from code proposals or reports |
| Cumulative task input and output | Sum of per-call measurements, including repeated history each time it is sent | Investigation, implementation, verification, and retries together |
| Largest single-call input | Largest measured input during the task | Input size per call; output allowance and other limits require separate checks |

The following values are **fictional arithmetic examples, not measurements**.

| Call | Input | Output |
| --- | ---: | ---: |
| First | 2,000 | 1,000 |
| Second | 3,500 | 500 |
| Whole task | 5,500 | 1,500 |

Cumulative input plus output is 7,000 tokens, while the largest measured input is 3,500. Do not interpret the cumulative total as simultaneous context. When the second call includes previous input and output, that history is counted again in cumulative input.

Check whether cache counters are components of input totals or separate categories. Do not add reasoning counts twice when they are part of output. Preserve unknown definitions rather than invent totals. Usage, charges, and remaining application allowances are different quantities.

## Read numerical examples with their conditions

### Text selected from a fixed small repository

This repository’s [measured benchmark](https://github.com/tomiya7688/ai-context-reducer/blob/4621d09c9d6a5b4131f6d6b9e46c29fc321730c2/docs/en/measured-context-reduction-benchmark.md) selects material for three investigations from five features containing 15 implementation, test, and document files. It counts selected file text without generating actual AI responses.

| Investigation | Selected characters after search | Files |
| --- | ---: | ---: |
| Invalid settings-file error display | 1,328 | 3 |
| Display-name whitespace handling | 1,032 | 3 |
| Notification retry conditions | 1,183 | 3 |

Across three cases, the median is 1,183 characters, mean 1,181, and range 1,032–1,328. The median is the middle value after sorting. These are **characters from three small fixed cases**, not average tokens for one-file changes or whole-task usage. Requests, history, outputs, and retries are excluded.

The numbers are derived from [version-pinned reference results](https://github.com/tomiya7688/ai-context-reducer/blob/4621d09c9d6a5b4131f6d6b9e46c29fc321730c2/benchmarks/context-reduction/reference-results.json). Characters are counted with Python `len()` on UTF-8-decoded text. No model or tokenizer was used, so measured token counts are absent.

### A published study of autonomous coding tasks

Figure 1 of [Bai et al., v3](https://arxiv.org/abs/2604.22750v3) reports average cumulative input plus output of approximately 4.17 million tokens for agentic coding. [1] This includes repeated history across calls, not one input.

Conditions: OpenHands; 500 SWE-bench Verified tasks; four runs per task; eight models—Claude Sonnet 3.7/4/4.5, GPT-5/5.2, Qwen3-Coder-480B-A35B-Instruct, Kimi-K2, Gemini-3-Pro. Full history is carried forward; counts come from execution usage logs (Section 2). Do not invent an unreported median.

This does not establish ordinary coding-task requirements. Different tasks, history policies, models, and run variation change estimates. Model names describe the experiment, not recommendations.

## Steps to build estimates in your environment

### 1. Save task categories and measurement conditions

Save a short record in, for example, `docs/usage/measurement-method.md`.

```markdown
# Usage measurement conditions

- Category: short question / one-file change / multi-file change / whole-project investigation
- Start and finish: initial request through required checks and completion report
- AI, model, version, settings, measurement date:
- History carryover, summaries, and rereading:
- Source screen or log for input/output and definitions of its fields:
- Treatment of cache and reasoning counters:
- Inclusion of reviews by other AIs or chats:
- Measured tokens / estimates / characters only:
```

Record an AI editing only visible code separately from one searching the repository and running checks, even for the same task label. Do not pool results when settings or measurement methods change.

### 2. Record calls and task outcomes

Use available logs to record, for example, `docs/usage/requests.csv`. This is a header template.

```csv
task_id,task_kind,request_id,input_tokens,output_tokens,measurement_kind,source_log
```

One row represents one call. Leave unavailable numbers blank, not zero. If only characters are available, store them separately rather than presenting them as tokens.

In `docs/usage/task-results.md`, record cumulative input, output, call count, largest input, target files, checks, and completion or noncompletion. Identify aborted tasks, retries, and reviews in separate chats with their IDs and aggregation scope. Count a call appearing in multiple logs only once.

When some calls are missing, label the sum as “recorded portion only” and do not aggregate it as complete measured task usage. Do not infer token counts from percentages of remaining allowances.

### 3. Group comparable tasks and inspect median and range

Start by recording a few similar everyday tasks. Include count, completed and incomplete counts, and input/output definitions. Report the middle sorted value and minimum/maximum. For an even count, use the mean of the two central values as the median.

For five completed tasks consuming 1,600, 2,000, 2,600, 3,200, and 18,000 tokens, the median is 2,600, mean 5,480, and range 1,600–18,000. **These are fictional values illustrating aggregation, not measured usage.** One large value changes the mean.

A small sample’s minimum and maximum are not future bounds. Do not hide retries or failures by showing only successes; report incomplete tasks separately. Do not pool characters, measured tokens, different models, or different workflows into one average.

### 4. Decide how to proceed with the next task

- If individual inputs are large, search for relevant parts or split long material into meaningful sections. Preserve necessary specifications and tests.
- If inputs are small but cumulative usage grows, inspect repeated file reads, long check logs, and repeated fixes.
- If features can be changed and verified independently, consider separate tasks. Count shared specifications and handoffs too; splitting does not necessarily reduce usage.
- When additional investigation supplies the facts required to decide, proceed to the agreed completion checks. Do not stop necessary verification merely because it consumes tokens.

For example, settings loading and screen presentation may be independent change units sharing a specification. If you are still identifying one bug’s cause, preserve confirmed evidence and unresolved questions before moving to another chat.

## Example AI request

```text
This task is a one-file change.
Record usage according to docs/usage/measurement-method.md.
Save available per-call input and output in docs/usage/requests.csv.
At completion, append totals, call count, largest input, and outcome to docs/usage/task-results.md.

Identify measurement sources. Mark unavailable values as unmeasured.
Do not double-count cache/reasoning components or duplicate calls.
Include retries and additional checks with explicit aggregation scope.
Use only comparable past tasks to report count, median, and minimum/maximum.
Do not turn illustrative values or character counts into measured tokens.
Do not omit necessary evidence or checks to reduce usage.
```

If the AI cannot read logs or usage displays, provide the values and their definitions yourself. Attach or paste records in a chat that cannot read files. Do not ask the AI to invent its usage. For repeated use, add a brief entry-instruction reference: for tasks recording usage, read `docs/usage/measurement-method.md`.

## How this differs from a reduction benchmark

The [measured benchmark](https://github.com/tomiya7688/ai-context-reducer/blob/4621d09c9d6a5b4131f6d6b9e46c29fc321730c2/docs/en/measured-context-reduction-benchmark.md) compares the same task before and after narrowing information. These estimates group comparable tasks by kind to plan reading scope or work units.

Using estimates to narrow material can reduce irrelevant inputs or repeated investigations. Recording and handoffs add input too. Compare whole-task usage while preserving necessary evidence and completion conditions.

## Supporting tools

- **Usage displays or execution logs:** May expose measured input and output. Check field definitions and call coverage.
- **A tokenizer matching the model:** Counts how text is segmented before sending. It may not include hidden instructions, history, or actual generated output.
- **A spreadsheet or short aggregation script:** Groups recorded calls and computes totals, median, minimum, and maximum. Inspect scope and missing values first.

## About these quantities

Using past measurements to estimate future work is **measurement-based estimation**. The information limit processed at once is the **context window**; dividing text into model units is **tokenization**. Keep cumulative task usage separate from per-call limits.

The referenced paper analyzes a particular coding environment. These recording procedures and categories do not establish universal averages.

## References

1. Longju Bai et al. (2026). [How Do AI Agents Spend Your Money? Analyzing and Predicting Token Consumption in Agentic Coding Tasks](https://arxiv.org/abs/2604.22750v3). arXiv:2604.22750v3, revised October 2, 2026. Figure 1, Section 2.
