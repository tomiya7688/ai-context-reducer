# What Is an LLM?

> Japanese Source of Truth: [LLMとは何か](../../jp/LLMの仕組み/LLMとは何か.md)

An LLM can answer questions, summarize text, translate, and generate code even though these tasks look very different. The first useful mental model is that an LLM is **not a database that stores one finished answer for every question**.

This guide focuses on autoregressive LLMs, a common design in chat and code-generation systems. An autoregressive model predicts the next token from the tokens available so far, appends a selected token, and repeats the same process. Not every language model uses exactly this architecture.

## What the model directly computes

Before text reaches the model, the surrounding system converts it into [tokens](what-is-a-token.md). The model processes the token sequence numerically and produces scores for candidate next tokens.

For example:

```text
The capital of Japan is
```

The model does not have to look up a stored row containing the finished answer. It uses its trained parameters and the current input to score possible continuations. The generation procedure selects a token, appends it, and asks the model to predict again.

```text
current token sequence
  ↓
score candidate next tokens
  ↓
select one according to the decoding method
  ↓
append it
  ↓
predict again
```

This repeated next-token process can produce both short answers and long programs. [How LLM generation works](how-llm-generation-works.md) follows the full sequence.

## Training changes parameters

A model's **parameters** are numerical values that determine how inputs are transformed. During pretraining, the training system measures prediction error on many token sequences and updates those parameters to reduce that error.

Documents and programs are not generally stored inside the parameters as ordinary files or database rows. Patterns such as syntax, word use, factual associations, and code structure are distributed across many parameters. At the same time, research has shown that some training examples can be reproduced verbatim, so it is also inaccurate to say that a model can never memorize examples.

[What does an LLM know?](what-does-an-llm-know.md) discusses that distinction in more detail.

## Why can next-token prediction answer questions?

Training corpora contain explanations, conversations, questions and answers, specifications, programs, tests, and many other kinds of sequences. To improve next-token prediction across such data, a model can learn useful regularities involving long-range relationships, document forms, and associations between problems and answers.

Large language models have also demonstrated the ability to adapt to tasks from instructions and examples placed in the input. That empirical ability does not prove that scaling next-token prediction necessarily produces human-like understanding.

Chat-oriented models may also receive additional training that makes instruction-following behavior more likely. The behavior of a deployed assistant therefore depends on more than the Transformer architecture alone. [From Transformers to LLMs](from-transformers-to-llms.md) separates pretraining, instruction tuning, chat formatting, and external tools.

## Search, verification, and execution are separate operations

Bare language-model inference is different from web search, database access, and program execution.

When an AI product can search the web or run code, an external tool can perform that operation and return the result to the model as new context. The Transformer has not automatically become a search engine or runtime.

A fluent answer therefore is not the same thing as a verified answer. [Why LLMs make mistakes](why-llms-make-mistakes.md) explains why this distinction matters.

## Why this matters for context reduction

An LLM conditions its output on the current token sequence. Specifications, source files, test results, stale notes, and unrelated logs can all become part of that input.

If necessary evidence is absent, the model may fill gaps from learned patterns. But adding everything is not a guarantee of correctness either; research on long-context models has shown that how information is positioned can affect task performance.

Context reduction in this repository is therefore not about withholding information from the model. It is about **selecting the original sources needed for the current decision, avoiding unrelated material, and expanding the scope when evidence shows that more is needed**.

Continue with [What is a token?](what-is-a-token.md) and [How LLM generation works](how-llm-generation-works.md).

## References

- [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language-models.pdf)
- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)
- [Extracting Training Data from Large Language Models](https://arxiv.org/abs/2012.07805)
