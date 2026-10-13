# Training vs. Inference

> Japanese Source of Truth: [学習と推論の違い](../../jp/LLMの仕組み/学習と推論の違い.md)

When a user tells an LLM a new project rule, people sometimes say that "the model learned it." Model **training** and **inference** are different operations.

Separating them clarifies what prompting, RAG, fine-tuning, chat history, and tools actually change.

## Training updates parameters

Training feeds examples into a model, measures a loss between predictions and target data, computes gradients, and updates parameters.

```text
training data
  ↓
model prediction
  ↓
loss
  ↓
gradients
  ↓
parameter update
```

Large-scale pretraining repeats this process over huge corpora. Fine-tuning also updates parameters, although its data, scale, and purpose may differ.

## Inference normally keeps parameters fixed

Inference uses already-trained parameters to compute output for the current context.

```text
current context
  ↓
fixed trained parameters
  ↓
generated tokens
```

Telling a model "this project uses string IDs" can influence later turns when that fact remains in context. Ordinary chat inference does not imply that the base model was permanently retrained on the statement.

## Prompting changes inference conditions

A prompt is input supplied at inference time. "Return JSON" changes the token sequence conditioning generation; it does not update model weights.

Few-shot prompting likewise places examples in the current input rather than performing gradient training.

## RAG retrieves external information into context

**Retrieval-Augmented Generation (RAG)** searches an external source and puts selected results into the model input.

```text
question
  ↓
retrieve external documents
  ↓
question + retrieved material
  ↓
generate response
```

Retrieved documents are not automatically written into model parameters.

## Fine-tuning is additional training

**Fine-tuning** uses additional data to update a pretrained model's parameters. Supervised instruction tuning can teach response patterns for instructions. InstructGPT combined supervised fine-tuning with reinforcement learning from human preference rankings.

Fine-tuning persistent behavior and providing current project facts are different tasks. Rapidly changing repository state generally belongs in current context rather than repeated retraining.

## Tool execution is also not training

When an AI system can run tests, an external environment performs the command and returns the result.

```text
LLM requests test
  ↓
external environment runs it
  ↓
failure output enters context
  ↓
LLM generates a revision
```

The feedback loop uses new observations during inference; it is not necessarily fine-tuning the model.

## Product memory and model training are different

A product may store user preferences or old conversations and retrieve them later. That storage system can make information available in future context without modifying the model's base weights.

Always check the product specification for what is stored and when it is reintroduced.

## Why this matters for context reduction

Software development depends on fast-changing specifications, source code, and test results. Those are current sources to inspect and provide, not facts that should be assumed to exist in pretraining.

A useful separation is:

- general language and code capability: trained parameters
- current project facts: selected source context
- latest runtime results: external tools
- persistent model behavior changes: fine-tuning when justified

## References

- [Improving Language Understanding with Unsupervised Learning](https://openai.com/index/language-unsupervised/)
- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)
- [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)
