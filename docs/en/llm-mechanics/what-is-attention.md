# What Is Attention?

> Japanese Source of Truth: [Attentionとは何か](../../jp/LLMの仕組み/Attentionとは何か.md)

Attention is often summarized as "the model focuses on important words." That phrase is easy to remember but can produce a misleading mental model.

Self-Attention is a learned computation that determines how much information a token position receives from other permitted positions when its representation is updated.

## Attention is not human visual attention

An Attention weight does not directly mean "the model considered this word important in the human sense." The weight belongs to a particular layer, head, and query position.

Different layers and heads compute different weights, so one Attention map is not a universal importance ranking for the whole model.

## Query, Key, and Value

Each token-position representation is projected into three learned vectors:

- **Query** is used by the current position to compare possible information sources.
- **Key** represents a source position for that comparison.
- **Value** contains information that will be combined according to the resulting weights.

"Query searches Keys and retrieves Values" is a useful analogy, but the model is not querying a database. All three are vectors produced by learned transformations.

## Weights are computed for each query position

Consider:

```text
The saved setting disappeared after restart.
```

To update a later position, its Query is compared with the Keys at positions it may read. Those comparison scores are converted into weights, which are then used to combine Values.

This allows a position to receive information directly from distant positions rather than passing it only through a one-step recurrent chain.

[Inside a Transformer](inside-a-transformer.md) explains Scaled Dot-Product Attention in the full block.

## A causal mask hides future tokens

During autoregressive training, a position must not read the correct future target token. A **causal mask** blocks Attention to positions on the right.

For:

```text
A B C D
```

the representation used to predict after C may use A, B, and C, but it cannot read D as future ground truth.

This lets a training system process many known positions in parallel without leaking future targets.

## Multi-Head Attention learns several projections

Multi-Head Attention performs several Q/K/V projections and Attention computations in parallel, then combines their results.

The model learns those projections. Humans do not preassign a permanent role such as "syntax" or "subject" to each head.

## Attention does not guarantee perfect use of long context

A token can be within the context window and technically available to Attention without being used reliably for a task.

*Lost in the Middle* found that, on multi-document QA and key-value retrieval tasks, model performance changed when relevant information was moved to different positions in a long context. In the evaluated models, information in the middle was often used less effectively than information near the beginning or end.

That result should not be generalized into "every model always ignores the middle." It does show why "present in context" and "reliably used" are different claims.

## Attention and context reduction

Users normally do not manipulate Attention weights directly when reducing context. They choose the token sequence that the model receives.

Providing the relevant specification, source code, and tests focuses the available evidence on the task. Stale notes, repeated explanations, and unrelated logs also become model input when included.

See [Context amount and use](context-amount-and-use.md) for how this connects to repository work.

## References

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
