# Context Amount and Use

> Japanese Source of Truth: [コンテキストの量と使われ方](../../jp/LLMの仕組み/コンテキストの量と使われ方.md)

“Is reducing context only about saving money? With a large enough window, can't the AI receive everything and select what it needs?”

**Removing unnecessary information while retaining required evidence can also help preserve answer and task quality.** Research has observed failures to use evidence within long inputs and reduced accuracy after adding information unnecessary for the answer. [1][2] Conversely, deleting information needed for a decision can make even a short input inadequate.

This guide connects LLM mechanics to information-selection methods. See [What Is Context?](what-is-context.md) for the information itself and [Context Amount, Computation, and Cost](context-compute-and-cost.md) for computation and billing.

## What does “lower performance” mean?

Performance includes more than speed and memory use. It also includes **answering correctly, using the necessary evidence, and following the specified conditions**. We mainly call these latter properties “quality.” Do not directly reinterpret a study's answer accuracy as a success rate for real code changes.

A context window limits the capacity available to input and generation. Being within that capacity does not establish how reliably the information will be used. Success at locating one passage in a long input does not guarantee equal-quality work that must combine multiple pieces of information. [3]

Judge whether the task actually used the necessary evidence and met its completion criteria, not merely whether it fit the advertised limit.

## What errors have been observed with long input?

These sources investigate different problems. Distinguish what each varied and measured instead of simply collecting study names.

| Source and scope | Compared conditions | Observation | What it does not establish |
| --- | --- | --- | --- |
| **Lost in the Middle**, released in 2023 and published in TACL in 2024 [1]; then-current models performing multi-document QA and key-value retrieval | The position of necessary information within long input | Performance often declined in the middle relative to the beginning or end | Not every current model necessarily misses information in the middle |
| **GSM-IC**, ICML 2023 [2]; arithmetic word problems | Adding information unnecessary for the original solution | Accuracy declined for the evaluated models and methods | The same effect size cannot be assumed for code repair |
| **RULER**, COLM 2024 [3]; 17 long-context models and 13 tasks | Varying input length and tasks, including multi-hop tracing and aggregation beyond retrieval | Many models declined with increasing length despite strong simple-retrieval results | Advertised capacity alone does not determine capability on every task |
| **Context Rot**, Chroma technical report dated July 14, 2025 [4]; 18 models across the study | Input length and distractors in retrieval, conversation-history, and repetition experiments | Reports long-input degradation and differences associated with content | Not all 18 models participated in every experiment; no universal token threshold for degradation is established |

Papers and corporate technical reports differ in publication format and experimental conditions. These references support the distinction between **information being present and being used correctly**, rather than ranking particular models.

Unrelated information and distractors also differ. The former is off-topic; the latter resembles relevant material or shares its topic without answering this question. In code, unrelated screen logic and a similarly named obsolete save implementation pose different selection problems. This code analogy is our illustration, not an outcome measured in the cited studies.

## Why can selecting information support quality?

An LLM computes representations of input tokens, combines information across positions through mechanisms including Attention, and generates a continuation. Additional material becomes part of those conditions too. [5]

Attention is not a mechanism guaranteed to select only the correct evidence for the current task. If obsolete and current specifications are supplied without distinguishing them, the model also has to determine which applies. Selecting relevant locations and identifying their revision and purpose reduces that additional selection work.

The resulting proposal in this guide is to **reduce opportunities for confusing candidates and conducting unnecessary searches without losing the evidence needed for the answer**. Verify the magnitude of any improvement on the actual task.

Metaphors such as “losing concentration” or “Attention getting diluted” are not complete causal explanations. Observed experimental results and identification of the internal mechanism behind an individual failure are different achievements. Do not attribute every failure to one cause without separating position, content, task, training, and architecture.

## Compare everything, necessary evidence, and too little evidence

Suppose a fictional application loses saved settings after restarting. Completion requires using the specified storage location, preserving settings after saving and restarting, and passing the related existing tests.

Assume that the current specification, save code, startup loader, storage-path configuration, and related tests are necessary for this decision. The following comparison is illustrative, not a measured AI success-rate experiment.

| Input strategy | Information supplied | Extra selection work or missing evidence |
| --- | --- | --- |
| **Supply everything** | Required evidence plus other screen code, obsolete save-design proposals, and all historical logs | The model must rediscover the current specification and implementation among many candidates |
| **Select necessary evidence** | Current requirements, save and load code, storage configuration, and related tests, with revisions and locations | The model can trace the relevant behavior and check that saving and loading use the same location |
| **Remove too much** | Only the function that saves settings | The startup path and governing requirements are absent; the correct repair cannot be determined from that function alone |

The second approach does not aim to minimize character count. It makes **the sources needed to check this task's conditions available together**.

The third approach might produce a plausible edit from a short input without establishing behavior after restart. Retrieve the missing loader or specification, or report the gap. A change based on guessed requirements is not completion.

“Old” does not always mean “unnecessary,” either. If compatibility or migration from an old format is a completion requirement, the old specification is required evidence. Relevance follows the task, not length or recency alone.

## Benefits extend beyond price

**Selecting information may reduce failures to use evidence.** When required information remains, removing unrelated material and distractors is a candidate quality improvement. [1][2][4] Check both whether retrieval selected the required evidence and whether the model used it.

**It can reduce input-processing and temporary-memory work.** In a basic full-history architecture, shorter input reduces positions to process, reference targets, and retained KV data. This does not promise a proportional latency improvement. See [the computation and cost guide](context-compute-and-cost.md) for the mechanism.

**It leaves room for information needed later.** Avoiding unnecessary history leaves capacity for newly discovered dependencies, failed-test results, output, and reasoning. Spare capacity and guaranteed model quality remain different claims.

**It can lower metered input costs.** Include output, caching, retrieval, summarization, and other expenses in the comparison. It does not automatically reduce a flat monthly subscription price. See [the computation and cost guide](context-compute-and-cost.md) for accounting examples.

**Less misreading can mean less rework.** Preventing a mistaken specification choice can avoid another explanation, edit, or verification cycle. This is an indirect benefit: shorter input alone does not establish it. Measure retries through correct completion.

## Reduction also introduces failure modes and overhead

Search can omit necessary files. A common helper without “settings” in its filename might not appear in the initial search. Do not treat search results as a complete scope; follow calls and tests to check what is missing.

Replacing every long original with a short summary can also remove conditions and exceptions. For example, “check authorization” does not identify the permission required for each operation. Anthropic's practical guidance discusses both losing later-important details through aggressive compaction and retaining sufficient information rather than optimizing for shortness alone. [6]

Use indexes and summaries as **pointers to sources**, returning to originals for decisions that depend on details. Keeping a source path and revision does not mean its contents have been checked again.

Additional summaries and retrievals can also cost more time and usage than they save. There is no need to split a task that already fits in a small, sufficient source set into many stages solely to shorten context.

## Separate information roles and expand from evidence

| Information | Role in the task |
| --- | --- |
| Request and completion criteria | Define the change and required verification |
| Implementation | Establish current behavior and change location |
| Specifications and rules | Define constraints the change must preserve |
| Tests | Indicate expected behavior and regression checks |
| Errors and logs | Show observed failures |
| Search results and indexes | Locate candidate original sources |
| Summaries | Transfer state compactly, while deferring to originals for necessary decisions |

Confusing these roles can turn a search result into purported proof of behavior or a stale summary into a current specification. Before reducing information, check that no role necessary for the decision or its verification has disappeared.

The initial scope need not be perfect.

```text
check the request and completion criteria
  → narrow candidates and read originals
  → check what is missing for decisions or verification
  → if a new dependency appears, read its source and related tests
```

For example, reading the save code may reveal a shared serializer: a component that converts settings into their stored format. Expand to that component and its related tests. Do not omit required code merely because it is long.

## How to check whether reduction helped

Compare the same task kind, starting revision, model, settings, and completion criteria. Before changing the selection approach, check that necessary evidence remains. The following is an evaluation plan, not a result measured for this guide.

| Question | Example record |
| --- | --- |
| Did required evidence remain? | Presence and revisions of current requirements, save/load code, and related tests |
| Was quality preserved? | Required behavior, existing tests, diff review, and remaining defects |
| Was input reduced? | Per-call input separately from cumulative task input |
| How did whole-task burden change? | Output, reasoning, and cache components; prices and elapsed time including search and summarization |
| How did rework change? | Counts and reasons for extra explanations, edits, retrievals, and checks |

Keep failures and runs stopped by missing information, not just successful cases. Where practical, repeat matching conditions and inspect the spread of results. Without usage measurements, do not substitute character reductions for measured token or price savings.

See [Build context-use estimates by task kind](../ai-usage/estimate-context-use-by-task.md) for detailed recording. Also distinguish whether this repository's [measured benchmark](../measured-context-reduction-benchmark.md) measures actual LLM repair quality or the amount of material provided.

## Select what correct completion requires, not the smallest input

Context reduction is not about making an AI work with inadequate information. **It selects information so the model can use necessary evidence correctly, with the aim of reducing cost, time, and rework through correct completion.**

Read necessary long originals and exclude unnecessary short notes. Add missing evidence when discovered and report unverified areas. Continue to [Context Reduction Basics](../context-reduction-basics.md) and the [Method Index](../method-index.md); for a first code change, start with [Context Priority](../context-priority.md).

## References

Checked October 18, 2026. Distinguish the studies' models, tasks, and publication dates from current models and real work. This guide's repair examples and evaluation plan are not those studies' experimental results.

### Research papers

- [1] Nelson F. Liu et al. (2024). [Lost in the Middle: How Language Models Use Long Contexts](https://aclanthology.org/2024.tacl-1.9/). Transactions of the Association for Computational Linguistics, 12, 157–173 — QA and retrieval with varied evidence positions.
- [2] Freda Shi et al. (2023). [Large Language Models Can Be Easily Distracted by Irrelevant Context](https://arxiv.org/abs/2302.00093). ICML — GSM-IC arithmetic tasks with unnecessary information.
- [3] Cheng-Ping Hsieh et al. (2024). [RULER: What's the Real Context Size of Your Long-Context Language Models?](https://arxiv.org/abs/2404.06654). COLM — long-context evaluation including retrieval, multi-hop tracing, and aggregation.
- [5] Ashish Vaswani et al. (2017). [Attention Is All You Need](https://arxiv.org/abs/1706.03762). NeurIPS — combining information across positions through Attention.

### Official documentation, technical reports, and practical guidance

- [4] Kelly Hong, Anton Troynikov, Jeff Huber. (2025-07-14). [Context Rot: How Increasing Input Tokens Impacts LLM Performance](https://www.trychroma.com/research/context-rot). Chroma Technical Report — technical report varying input length and distractors.
- [6] Anthropic. [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — practical guidance on sufficient information and over-aggressive compaction.
