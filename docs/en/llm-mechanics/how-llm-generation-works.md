# How LLM Generation Works

> Japanese Source of Truth: [LLMが文章を生成するまで](../../jp/LLMの仕組み/LLMが文章を生成するまで.md)

An autoregressive LLM does not normally construct an entire finished response internally and then reveal it. It predicts one next token from the current token sequence, appends a selected token, and repeats.

This guide follows the path from user text to generated output.

## 1. The application assembles model input

A chat application may combine the visible user message with system instructions, earlier messages, retrieved documents, and tool results. The exact format is product- and model-specific.

The model conditions its computation on the final sequence that the application sends.

## 2. A tokenizer creates token IDs

The input is split into [tokens](what-is-a-token.md), and the tokenizer maps those tokens to vocabulary IDs.

```text
string
  ↓
tokens
  ↓
token IDs
```

Those IDs are then mapped into vectors.

## 3. Token IDs become vectors

An embedding table maps each token ID to an **embedding vector**. The model also needs position information so that it can distinguish token order. Different models use different positional mechanisms, including learned positions or rotary position representations.

## 4. Transformer blocks update representations

Transformer blocks use mechanisms such as Self-Attention and feed-forward networks to update the representation at every token position.

Self-Attention lets a position combine information from other permitted positions. Autoregressive language models commonly apply a causal mask so a position cannot use future target tokens.

See [Inside a Transformer](inside-a-transformer.md) and [What is Attention?](what-is-attention.md) for the detailed computation.

## 5. The final representation becomes token scores

The model maps the final hidden representation to one **logit** for each vocabulary token. A logit is a raw score used to compare candidates.

A Softmax operation can turn those scores into a probability distribution.

```text
final hidden representation
  ↓
vocabulary logits
  ↓
probability distribution
```

## 6. A decoding method selects a token

Some decoding methods take the highest-scoring token. Others sample from a distribution. Settings such as temperature or top-p can change how candidates are selected.

The same visible prompt therefore need not always produce identical output. Sampling is not the only possible source of differences; model updates, hidden application context, and service settings can also matter.

## 7. The selected token is appended and prediction repeats

```text
input:      [A, B, C]
prediction:          D
next input: [A, B, C, D]
prediction:             E
```

Generation continues until a stop token, a length limit, or another application-level stopping condition is reached.

Implementations commonly use a **KV cache** to retain Key and Value tensors from previous positions so generation does not recompute all of them from scratch. A KV cache is temporary inference state, not parameter training or permanent memory.

## Generation is not retrieval of a finished answer

Later tokens are predicted from the prompt and the tokens already generated. If an early token introduces a wrong premise, later tokens may continue consistently from that wrong premise.

Likewise, a high model probability does not mean that an external fact has been verified. It is a probability over continuations under the model and current input.

That distinction leads directly to [Why LLMs make mistakes](why-llms-make-mistakes.md).

## Why context design matters

Existing types, tests, requirements, and error messages can all condition later token predictions when included in context. Unrelated logs and stale specifications also become part of that same sequence.

Choosing context is therefore not merely an exercise in shortening prompts. It determines which evidence is available to condition generation.

## References

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language-models.pdf)
