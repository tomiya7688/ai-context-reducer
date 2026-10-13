# Inside a Transformer

> Japanese Source of Truth: [Transformerの中では何が起きているのか](../../jp/LLMの仕組み/Transformerの中では何が起きているのか.md)

"Transformers use Attention" still leaves a major gap: how does a token sequence become next-token scores?

This guide follows a common decoder-only Transformer design without deriving the full matrix equations. Real models differ in normalization order, activation functions, positional representations, Attention implementations, and other details.

## 1. Token IDs become embedding vectors

Each token ID is mapped through an **embedding** table to a vector.

```text
token ID 314
  ↓ embedding
[0.12, -0.43, ..., 0.08]
```

The numbers above are illustrative.

The same token ID starts from the same token embedding, but later Transformer blocks update each position using its context. The internal representation of the same token can therefore differ in different sentences.

## 2. The model represents position

Basic Self-Attention does not by itself encode token order. Transformers include a positional mechanism.

The original Transformer used sinusoidal positional encodings. Modern LLMs may instead use learned positions, RoPE, or other schemes. The safe general statement is that the model incorporates position information so Attention can distinguish where tokens occur.

## 3. Each position produces Query, Key, and Value vectors

Learned linear projections create three vectors:

- **Query (Q)** represents what the current position uses to compare possible sources.
- **Key (K)** represents each source position for that comparison.
- **Value (V)** carries information that can be mixed into the result.

The database-search analogy can be helpful, but Q, K, and V are numerical projections rather than literal search records.

## 4. Query-Key comparisons become Attention weights

For a given Query, Scaled Dot-Product Attention compares it with Keys from permitted positions. A causal mask removes future positions in an autoregressive model, and Softmax converts the remaining scores into weights.

```text
Query
  × Keys
  ↓
scores
  ↓ causal mask
future positions excluded
  ↓ Softmax
weights
```

## 5. Weighted Values are combined

Attention multiplies source Values by their weights and combines them. The current position therefore receives information from other permitted positions.

This mechanism makes long-range interaction possible, but it does not guarantee that all information in the context will be recovered or used equally well.

## 6. Multi-Head Attention uses several learned projections

**Multi-Head Attention** performs several Q/K/V projections in parallel and combines the results.

Humans do not assign one fixed semantic role to every head in advance. Different heads can learn different relationships, and their behavior should not be reduced to a permanent label such as "the grammar head."

## 7. Residual connections and normalization support deep stacks

A **residual connection** adds a block's input back to its transformed output, helping information and gradients flow through deep networks.

**Normalization** rescales internal representations according to a defined rule. The original post-normalization layout and common modern pre-normalization layouts place this operation differently, so one diagram should not be treated as universal.

## 8. Feed Forward Networks transform each position

After Attention mixes information across positions, a **Feed Forward Network (FFN)** applies a learned nonlinear transformation independently at each position.

A useful simplification is that Attention handles cross-position mixing while the FFN performs position-wise transformation. This is a teaching model, not a claim that all learned capabilities can be cleanly assigned to one of the two modules.

## 9. Blocks are stacked

An LLM repeats Transformer blocks many times. Each layer consumes representations from the previous layer and produces new ones.

No single Attention operation creates a complete semantic interpretation. The final behavior results from transformations across many layers.

## 10. The final representation becomes vocabulary logits

The last hidden representation for the generation position is projected into one score per vocabulary token. These raw scores are **logits**.

```text
final hidden vector
  ↓ output projection
vocabulary logits
  ↓ decoding
next token
```

[How LLM generation works](how-llm-generation-works.md) explains how those scores lead to repeated token generation.

## Training and inference use the structure differently

During causal language-model training, a known sequence can produce next-token predictions for many positions in parallel while the causal mask blocks future targets.

At inference time, future tokens do not exist, so the model generates one token and then continues. Implementations often cache past Keys and Values in a KV cache to reuse work. That cache is temporary inference state, not persistent learning.

## Why this matters for context reduction

Every included token participates in the model's input sequence and can affect internal computation. Adding unrelated material is therefore not simply free storage.

At the same time, deleting requirements or tests removes evidence the model could have used. The goal is not the shortest input; it is an input concentrated on the relationships needed for the current decision.

## References

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language-models.pdf)
