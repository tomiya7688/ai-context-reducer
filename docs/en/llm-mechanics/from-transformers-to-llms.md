# From Transformers to LLMs

> Japanese Source of Truth: [TransformerからLLMが生まれるまで](../../jp/LLMの仕組み/TransformerからLLMが生まれるまで.md)

Implementing a Transformer does not by itself create a system that can answer questions or write programs. An untrained network has not yet learned useful language patterns.

Modern LLMs combine a Transformer-family architecture with large-scale training data and computation, and may then receive additional training for instruction-following behavior.

## 1. The architecture provides trainable structure

A Transformer can move information across token positions and repeatedly transform their representations. Before training, however, its parameters do not contain the learned relationships needed for useful language generation.

Training adjusts those parameters so that the model predicts tokens better.

## 2. Pretraining repeats next-token prediction at scale

A common autoregressive pretraining loop is:

```text
training token sequence
  ↓
predict next tokens
  ↓
compute loss against target tokens
  ↓
compute gradients
  ↓
update parameters
  ↓
repeat on more data
```

Across large corpora, this objective pressures the model to capture statistical structure useful for prediction: syntax, document patterns, code structure, factual associations, and many other regularities.

## 3. Scale changes what the same objective can support

GPT-2 and GPT-3 showed that scaling Transformer language models and training data could broaden performance across summarization, QA, translation, and in-context task adaptation without changing the basic autoregressive objective for every task.

Scaling-law studies found predictable relationships among model size, data, compute, and training loss over studied ranges. Later compute-optimal work showed that the balance between model size and training tokens matters as well.

These findings do not mean "more parameters always makes a model better." Data quality, optimization, architecture, training duration, and evaluation tasks all matter.

## 4. A pretrained base model is not automatically a chat assistant

Pretraining teaches continuation behavior. It does not by itself guarantee that a model will respond helpfully to commands such as "summarize this in three bullets."

**Instruction tuning** adds examples of instructions and desired responses. InstructGPT, for example, used supervised demonstrations followed by reinforcement learning from human preference rankings.

Not every modern model uses the same RLHF pipeline. The important distinction is that additional training can alter how a pretrained language model responds to user intent.

## 5. Chat roles are represented in model input

A user interface may display separate system, user, and assistant roles. The model ultimately receives those roles and messages encoded according to a model-specific format.

There is not a separate neural "brain" for each chat role. Training conventions and current role markers influence the continuation that the model produces.

## 6. Search and execution can be added outside the model

A deployed AI system can also connect an LLM to search, files, code execution, or databases.

```text
user request
  ↓
LLM selects an action
  ↓
external tool searches or executes
  ↓
result is added to context
  ↓
LLM continues from that result
```

The Transformer has not become a search engine or runtime; an external component performed the operation.

## An LLM system is a stack of mechanisms

A useful separation is:

```text
Transformer-family architecture
  ↓
large-scale pretraining
  ↓
optional instruction/preference training
  ↓
chat formatting and system instructions
  ↓
optional external tools
  ↓
current inference context
```

This separation helps identify what a model may know from training, what must be provided from current project sources, and what needs external verification.

## References

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [Improving Language Understanding with Unsupervised Learning](https://openai.com/index/language-unsupervised/)
- [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language-models.pdf)
- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)
- [Scaling Laws for Neural Language Models](https://arxiv.org/abs/2001.08361)
- [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556)
- [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)
