# What Is a Context Window?

> Japanese Source of Truth: [コンテキストウィンドウとは何か](../../jp/LLMの仕組み/コンテキストウィンドウとは何か.md)

Models are sometimes described as having a "128K context." It is misleading to read that number as "everything up to this size is remembered and used perfectly."

A **context window** is the bounded token range that a model can process for one inference. Exact accounting between input and generated output depends on the model and API.

Context as information and the window as capacity are different concepts. Cumulative tokens across calls are different from current occupancy as well. See [What Is Context?](what-is-context.md).

## Context can include more than visible user text

A chat system may send:

- system instructions
- the current user message
- conversation history
- retrieved files or web pages
- search results
- tool outputs
- temporary task state

The text visible in the interface therefore need not equal the actual model input.

Output reservation and maximum generation length are also API-specific. Check the target service instead of assuming that the entire advertised context can always be used as user input.

## Distinguish remaining capacity from whole-task usage

Consider a fictional service allowing 10,000 tokens of combined input and generation, with a separate output limit of 3,000. With 6,000 input tokens, capacity leaves 4,000, but output is still limited to 3,000. With 8,000 input tokens, combined capacity leaves at most 2,000 for generation. This illustrates accounting, not an actual API's reservation or enforcement behavior.

If reasoning tokens are included in generation under that service's rules, the entire allowance is not available for a visible answer. OpenAI's [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state) provides a product-specific example of these categories.

Adding an earlier call's input to cumulative usage does not itself consume current capacity. Separate information actually carried into current processing from the record of past usage. Reusing input computation through caching also does not remove that input from processing, so a cache hit alone does not free window space. See [computation, billing, and caching](context-compute-and-cost.md).

## Being inside the window is not the same as being used reliably

The window determines what can be available to inference. It does not guarantee equal-quality retrieval and use of every included item.

*Lost in the Middle* moved relevant information to different positions in long inputs and observed position-dependent performance on multi-document QA and key-value retrieval. The evaluated models often performed worse when relevant information was in the middle.

That finding does not prove that every model always fails on middle positions. It does show why "fits in context" and "will be used reliably" are separate claims.

## A context window is not permanent memory

Inference context is not the same as the model's trained parameters. Telling a model a project rule once during a conversation does not, by itself, permanently train that rule into the base weights.

Products may separately store conversation history or user memory and later retrieve it into context. That is a product-level storage and retrieval mechanism, not evidence that ordinary inference changed the base model parameters.

A KV cache is likewise temporary computation state for generation, not permanent knowledge storage.

## Long input has practical cost

Pricing, latency, and memory behavior depend on the model and implementation, but more input means more data must be represented and processed.

[Context Amount, Computation, and Cost](context-compute-and-cost.md) separates position-wise processing, relationships between positions, and reuse during generation, explaining why equal call counts can involve unequal work. A larger context limit is not a reason to add unrelated material.

## What should remain in context?

For a code change, long material may still be necessary when it contains:

- the implementation being changed
- the governing specification
- related types or interfaces
- tests that define expected behavior
- the actual failure
- rules that apply to the change

Unrelated source trees, duplicated explanations, and stale contradictory notes are different candidates for exclusion.

## Capacity and context design are different decisions

```text
bad goal:
fill the available window

repository goal:
select sources needed for the task
  ↓
add more when evidence shows a dependency
  ↓
return only the relevant check results
```

A larger window does not eliminate the value of selecting evidence. See [Context amount and use](context-amount-and-use.md).

## References

- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state) — input, generation, and context capacity; a product-specific example.
