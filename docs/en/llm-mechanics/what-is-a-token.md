# What Is a Token?

> Japanese Source of Truth: [トークンとは何か](../../jp/LLMの仕組み/トークンとは何か.md)

An LLM does not necessarily process a 10,000-character document as 10,000 individual characters. The surrounding system first divides text or code into **tokens** and maps those tokens to numeric IDs.

Understanding tokens explains why equal character counts can consume different amounts of context and why English, Japanese, source code, punctuation, and identifiers can behave differently.

## A token is not necessarily a word or a character

A **tokenizer** divides a string into units from a vocabulary. An illustrative split might look like this:

```text
string:  context reduction
example: ["context", " reduction"]
```

Other words may be split into multiple pieces, while punctuation or whitespace can participate in token boundaries. Japanese text does not mark every word boundary with spaces, so the rule "one word equals one token" does not work.

Exact segmentation depends on the tokenizer used by the model. Examples in this guide are illustrative rather than a fixed tokenization for a particular product.

## Why use subword units?

Making every possible word a single vocabulary item would require a very large vocabulary for names, inflections, identifiers, and new terms. Using only single characters would create long sequences.

Many tokenizers therefore use **subword** units between those extremes. Frequent strings can be represented as larger units, while rarer strings can be split into smaller pieces. SentencePiece is one example of a tokenizer that can learn subword units directly from raw text.

## Models receive token IDs

The tokenizer maps each token to an ID. Transformer layers do not work directly on human-readable strings; they begin from numerical representations derived from those IDs.

```text
string
  ↓ tokenizer
tokens
  ↓ vocabulary
token IDs
  ↓ embedding
Transformer
```

An **embedding** maps a token ID to a vector that the neural network can process. Later Transformer layers continually update the representation at each position using the surrounding sequence.

See [Inside a Transformer](inside-a-transformer.md) for the next step.

## Equal character counts do not imply equal token counts

Token count depends on the tokenizer vocabulary, the language, punctuation, whitespace, and source-code structure.

For example, these two short strings are not guaranteed to consume the same number of tokens:

```text
ユーザー設定を保存する
save_user_preferences()
```

Code indentation, symbols, logs, generated JSON, and repeated source text all become part of the token sequence. "100 lines" or "a short Japanese paragraph" is therefore not a reliable token measure.

For an exact count, use the tokenizer for the target model or usage information exposed by the service.

## Tokens and the context window

A model can only process a bounded token sequence in one inference call. That limit is the [context window](what-is-a-context-window.md).

A chat product may add system instructions, conversation history, retrieved documents, and tool results in addition to visible user text. How generated output shares or reserves the model's limit depends on the model and API.

The relevant quantity is therefore the final token sequence passed to the model, not only the visible character count.

## Reducing token count is not the ultimate goal

Fewer tokens can reduce input cost or processing work, but deleting requirements or tests can also remove evidence needed for a correct decision.

This repository first identifies the specifications, code, and checks needed for the task, then avoids unrelated or duplicated material. The aim is useful context, not the smallest possible prompt.

## References

- [SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing](https://arxiv.org/abs/1808.06226)
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
