# Context Amount, Computation, and Cost

> Japanese Source of Truth: [コンテキストの量と計算量と料金の関係](../../jp/LLMの仕組み/コンテキストの量と計算量と料金の関係.md)

Why can three requests use little context in one task but a great deal in another? Why can a short answer still require substantial processing when the supplied document is long? Counting requests alone cannot explain these differences.

Separate **how many tokens each call receives, how many it generates, and which computations it can reuse**. See [What Is Context?](what-is-context.md) for the information itself. Every numerical example here is hypothetical, not a measurement or a current product price.

## First distinguish the meanings of “inference count”

Inference uses a trained model to compute output. But “three inferences” does not establish what is being counted.

| Quantity | Example | What it does not establish |
| --- | --- | --- |
| Model calls | The application supplies input and requests output three times | The input and output lengths of each call |
| Token-generation steps | Select a next token, then compute the continuation | How much history each step references |
| Agent work iterations | Investigate, modify, test, and modify again | How many model calls or tool executions each activity includes |

GPU multiplications, generated tokens, and API calls are also different quantities. An API is the interface through which an application requests service processing and receives results. One internal arithmetic operation is not one separately billed API request.

The basic example below is **an autoregressive Transformer with full-history Attention and a KV cache**. Hold model size and numerical precision fixed when considering length. Architectures with limited attention ranges and implementations that accelerate generation in groups can have different scaling and execution counts. [1][2]

## What happens while processing the input?

Passing a long document does not merely store its text on the inference device. The model converts tokens into numeric arrays called vectors and updates them through multiple layers. [1]

Two kinds of work matter here.

**Computation at each position.** The model applies computations using learned numbers to a position's vector. More input positions mean more items to process. Position-wise networks are one example.

**Computation between positions.** Attention scores the relationship between a position and other positions it may reference, then combines information using weights derived from those scores. In the basic causal form, which cannot see future tokens, the first position references itself, the second references two positions, the third three, and so on. [1]

For `n` input tokens, the number of these relationships is `1 + 2 + … + n = n(n+1)/2`. At 1,000 tokens there are 500,500 pairs; at 2,000 there are 2,001,000, approximately four times as many. This illustrative calculation counts position pairs, not machine instructions.

Thus, full-position Attention includes work that grows quadratically with input length. **The whole model's runtime or bill does not necessarily quadruple.** Position-wise computation, parallel execution, memory access, caching, and service congestion also affect elapsed time.

For example, FlashAttention partitions the calculation to reduce storage and memory traffic for intermediate results. It need not retain every pair in one enormous table. Do not collapse Attention computation, working memory, and the KV cache discussed below into one supposedly quadratic quantity. [3]

Processing the input to prepare for generation is called **prefill**. Because the input is already known, many positions can be computed together within each layer. The model is not newly generating the long input one token at a time as though it were an answer. [2]

## What grows while generating a continuation?

After processing the input, the model selects a next token. Processing that selected token to calculate another, and continuing this process, is the **decode** phase. [2]

```text
process the existing input
  → select the first output token
  → process that token and select the next
  → process the selected token and select another
```

Within Attention, each position's vector produces a **Key** for comparison and a **Value** carrying information to combine. The new position's **Query** is compared with previous Keys, and the resulting weights combine Values. These are numeric arrays calculated within layers, not literal natural-language questions or database records. [1]

Because this architecture does not reference future tokens, previous positions' Keys and Values need not be recreated whenever a new token arrives. A **KV cache** stores them for reuse. [2]

However, the new Query still needs to reference stored Keys and combine Values. Longer history provides more positions to reference and more Key–Value data to retain. In this basic architecture, with the model and precision fixed, the KV data required is approximately proportional to the retained length. [2]

Therefore, generating equally long answers from short and long inputs requires different work. A longer answer adds more generation steps as well. The important distinction is that **a processing step can become larger without the number of steps increasing**.

Shortening input does not shrink the trained model itself. Memory for parameters and other costs that do not scale with input length remain. [3]

## What becomes input after a tool is used?

Suppose a settings-repair agent is organized as follows. This is an illustrative division of work, not a claim that every product uses exactly four calls.

| Model call | Newly supplied information | Model output | What the application does next |
| --- | --- | --- | --- |
| 1 | Request, work rules, and tool descriptions | Search request | Executes the search program |
| 2 | Candidate paths from the search | Request to read relevant passages | Retrieves files |
| 3 | Code, specification, and related test text | Proposed changes or editing requests | Applies permitted changes and runs tests |
| 4 | Test results and necessary error details | Explanation or another proposed fix | Revalidates after further changes |

“Newly supplied” does not mean “the entire input.” When the application carries instructions, conversations, and code forward, those earlier items remain part of later input. Removing obsolete results or substituting summaries changes what is carried forward. [4]

A search program can inspect a thousand files while returning only candidate paths; that does not input a thousand files of text into the model. Returning every file's full contents instead increases later input. **Even one tool execution can lead to very different LLM usage depending on what it returns.**

## Three calls can still have very different cumulative input

Separately from the four-stage example above, consider the following three-call accounting example. Both approaches generate 1,000 output tokens per call. For simplicity, there is no caching and no additional reasoning-token generation.

| Call | Selected-source input A | Long-material carryover input B | Output for each approach |
| --- | ---: | ---: | ---: |
| 1 | 2,000 | 20,000 | 1,000 |
| 2 | 4,000 | 22,000 | 1,000 |
| 3 | 6,000 | 24,000 | 1,000 |
| **Cumulative tokens** | **12,000** | **66,000** | **3,000** |

B carries an additional 18,000 tokens of material from the first call into every call. This produces a 54,000-token difference across three calls. The call count is identical, while cumulative input differs by a factor of 5.5.

A's maximum input of 6,000 and cumulative input of 12,000 are different quantities. Adding earlier inputs does not establish current window occupancy. Conversely, including the same passage in a later input counts that occurrence in cumulative usage. OpenAI's conversation API also accounts for input carried forward using response IDs. [4]

## Provider workload and the user's bill are different

Running a model requires arithmetic, memory, and device time. A metered API bill, however, normally uses the input, output, and other categories specified by its price schedule, rather than charging for each internal multiplication. [5]

Ignoring caching and other categories, the example calculation is:

```text
whole-task price
  = sum over calls of (input tokens × input unit price
                       + output tokens × output unit price)
```

Apply hypothetical prices of 100 yen per million input tokens and 400 yen per million output tokens to the table. Taxes, tool charges, and other fees are excluded.

| Approach | Input price | Output price | Total |
| --- | ---: | ---: | ---: |
| A | 12,000 ÷ 1,000,000 × 100 = 1.2 yen | 3,000 ÷ 1,000,000 × 400 = 1.2 yen | **2.4 yen** |
| B | 66,000 ÷ 1,000,000 × 100 = 6.6 yen | 3,000 ÷ 1,000,000 × 400 = 1.2 yen | **7.8 yen** |

Input differs by a factor of 5.5, but including the shared output cost makes the total-price ratio 3.25. An input-reduction percentage is not automatically a whole-task price-reduction percentage.

**Producing each successive token inside one response does not turn the complete input into a newly billed API call.** Separate computation within a call from counting history as input when it is carried into another call. [4][5]

## Reusing input cheaply is not the same as removing it

In addition to a KV cache within generation, a service may offer **prompt caching**, which reuses computation for matching input across separate calls. Availability conditions, retention, and billing categories vary by service. [6]

| Operation | What changes | What remains different |
| --- | --- | --- |
| Within-call KV caching | Reduces recomputation of earlier Keys and Values | References to earlier information remain |
| Cross-call prompt caching | Reuses computation for matching input | That information still belongs to the context |
| Removing unnecessary input | Reduces the information conditioning this generation | Removing required evidence prevents a justified decision |

A cache hit can lower cost or processing time without freeing space in the context window. This also differs from an answer cache that simply returns an earlier response text.

Calculate real prices using the applicable categories: ordinary input, cache reads, sometimes cache writes, output, and others. Check totals and component definitions so cached input is not added twice to ordinary input. [5][6]

For a practical example of why cache reuse does not justify keeping unrelated tasks in the same conversation, see [Assign AI roles and separate chats by task](../ai-usage/split-chats-by-task.md).

## Visible answer length is not sufficient either

Some reasoning models generate reasoning tokens that are not directly displayed to the user. For example, OpenAI documents that these occupy context space and are billed as output. Which information is carried into another call depends on the model and settings. [7]

Suppose usage reports 6,000 input tokens, including 4,000 cache-read tokens, and 1,500 output tokens, including 1,000 reasoning tokens. Total input plus output is 7,500, not 12,500: the cached and reasoning counts are components, not additional totals. This is an illustrative accounting example.

Equally long final answers need not have equal internal generation. Compare the same model, settings, inputs, and usage fields, and do not invent unavailable measurements.

## What happens with large inputs, and what should be measured?

Larger inputs increase the input-processing, reference, and temporary-state work described above. A finite window also needs room for additional evidence and generation. Nevertheless, halving input does not necessarily halve latency. Output length, implementation, parallel execution, and waiting time still matter. [2][3][4]

For metered APIs, aggregate the actual billing categories. With a flat-rate service, reducing input need not immediately lower the monthly fee. For self-hosted inference, compare devices, memory, and execution time rather than an API token price.

Search and summarization also have costs. If shortening one input involves repeatedly asking another model to summarize the whole source, include that work. See [Build context-use estimates by task kind](../ai-usage/estimate-context-use-by-task.md) for recording actual usage.

**Price, speed, capacity, and correctness are separate evaluation dimensions.** [Context Amount and Use](context-amount-and-use.md) explains long-input omissions and confusion, and the quality benefits and limits of selecting necessary information.

## References

Checked October 18, 2026. Product-specific accounting is presented as an example of that product. Consult current official specifications for actual prices, limits, and cache conditions.

### Research papers

- [1] Ashish Vaswani et al. (2017). [Attention Is All You Need](https://arxiv.org/abs/1706.03762). NeurIPS — Attention, position-wise computation, and causal masking.

### Official documentation, technical reports, and practical guidance

- [2] Hugging Face. [How caching works](https://huggingface.co/docs/transformers/cache_explanation) — autoregressive generation and KV reuse.
- [3] Hugging Face. [Optimizing LLMs for Speed and Memory](https://huggingface.co/docs/transformers/llm_tutorial_optimization) — Attention working memory, FlashAttention, model weights, and cache costs.
- [4] OpenAI. [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state) — carried-history input accounting and capacity.
- [5] OpenAI. [Pricing](https://developers.openai.com/api/docs/pricing) — input and output billing categories; the illustrative yen prices above are not copied from this schedule.
- [6] OpenAI. [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) — reusing input computation and interpreting usage components.
- [7] OpenAI. [Reasoning models](https://developers.openai.com/api/docs/guides/reasoning) — reasoning tokens and output usage.
