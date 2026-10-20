# What Is a Transformer?

> Japanese Source of Truth: [Transformerとは何か](../../jp/LLMの仕組み/Transformerとは何か.md)

Saying that "LLMs use Transformers" does not explain why the architecture is useful or how it affects model behavior.

A Transformer is a neural-network architecture that updates token-position representations by letting positions combine information from other positions. *Attention Is All You Need* introduced the architecture in 2017 as an encoder-decoder model for machine translation.

Modern generative LLMs do not necessarily reproduce that original architecture exactly. GPT-style autoregressive models commonly use a **decoder-only Transformer** derived from the decoder side of the original design.

## What problem did the Transformer address?

Earlier recurrent models process sequence state through a chain of time steps, which constrains parallel computation. The original Transformer removed recurrence and made Attention the central mechanism for connecting positions in a sequence.

A key advantage described in the original paper is that this structure can be trained with substantially more parallel computation.

The useful mental model is not "Transformer equals perfect long-text understanding." It is that the architecture provides a scalable way to learn transformations involving relationships across a sequence.

## What does a Transformer block do?

A simplified decoder-only path is:

```text
token IDs
  ↓
embeddings + position information
  ↓
Transformer block
  ├─ Self-Attention
  └─ Feed Forward Network
  ↓
more Transformer blocks
  ↓
next-token scores
```

**Self-Attention** computes how information from permitted positions is combined for the current position.

A **Feed Forward Network** then applies a learned nonlinear transformation at each position.

Real architectures also use residual connections and normalization, and models differ in ordering, positional methods, and other details. [Inside a Transformer](inside-a-transformer.md) follows those steps more closely.

## What does Attention add?

Consider:

```text
The setting was saved. After restart, that setting disappeared.
```

When processing a later reference such as "that setting," the model needs information from earlier positions. Self-Attention provides a learned computation that can connect those positions directly.

Attention weights are not a universal human-readable ranking of which words the model "considered important." They are internal quantities that vary by layer, head, and query position. See [What is Attention?](what-is-attention.md).

## Decoder-only models hide the future

During causal language-model training, a token position must not read future target tokens. A **causal mask** prevents Attention from accessing positions to the right.

Known training sequences can therefore be processed in parallel while preserving the next-token prediction task. At inference time, future tokens do not yet exist, so generation proceeds token by token.

## A Transformer architecture alone is not an LLM

The architecture provides a trainable structure. It does not by itself contain useful language behavior.

Large-scale pretraining adjusts the parameters using text and code data. Additional instruction or preference training may then alter how a model responds to users.

```text
Transformer architecture
  + data
  + training objective
  + scale and compute
  + optional additional training
  = a usable language model
```

[From Transformers to LLMs](from-transformers-to-llms.md) explains that path.

## Why this matters for context reduction

Attention makes positions in the input available for learned interaction, but it does not guarantee that every item inside a long context will be used equally well. Long-context studies have shown position-dependent performance on some retrieval and question-answering tasks.

"Fits in the context window" and "should be included for this task" are therefore different decisions.

## References

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language-models.pdf)
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
