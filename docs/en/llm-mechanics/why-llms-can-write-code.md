# Why Can LLMs Write Code?

> Japanese Source of Truth: [なぜLLMはコードを書けるのか](../../jp/LLMの仕組み/なぜLLMはコードを書けるのか.md)

An LLM can generate Python or Go even though it is a language model because source code is also representable as a token sequence. "It memorized a lot of code" is not a sufficient explanation of the capability.

When models train on code-containing data, next-token prediction can reward learning syntax, API patterns, identifier relationships, and correspondences between natural-language descriptions and programs.

## Source code becomes tokens too

For example:

```python
def add(a, b):
    return a + b
```

is tokenized before entering the model. A Transformer does not necessarily switch to a separate neural network because the input happens to be Python.

Programming languages contain strong recurring structure: punctuation, indentation, types, identifiers, calls, and argument patterns. Modeling those dependencies helps next-token prediction on code.

## Documentation connects language and code

Software data often contains both code and natural language:

- README and API documentation
- function and type names
- docstrings and comments
- issue descriptions
- error messages
- tests and expected results

Training on such sequences lets a model exploit statistical relationships between descriptions and implementations.

## Completion and specification-to-code generation use the same core mechanism

Completion conditions on existing code:

```text
existing code
  ↓
predict continuation
```

Specification-to-code generation adds more kinds of context:

```text
natural-language requirement
+ existing code
+ types and APIs
+ examples or tests
  ↓
predict a code continuation
```

The inputs differ, but autoregressive generation still predicts continuation tokens.

## Code-focused training can strengthen the capability

Models can receive additional training on code-heavy data. The Codex study fine-tuned GPT-family models on public GitHub code and evaluated generation from Python docstrings with HumanEval.

The results showed meaningful functional code generation while also identifying failures on longer operation chains and variable binding. Code generation therefore should not be reduced either to pure copying or to guaranteed program understanding.

## Project context still matters

A model may already know common Go or Python patterns, but it cannot be assumed to know yesterday's private project changes.

A real change may require:

- current function and type names
- project-specific APIs
- responsibility boundaries
- coding rules
- tests
- actual errors
- current specifications

Providing those sources lets the model condition generation on the project rather than only on generic code patterns.

## Writing code is not the same as proving it correct

An LLM can generate plausible source without observing the actual runtime result first. It may invent APIs, mismatch types, miss edge cases, rely on an older library version, or violate project rules.

External tools can check the candidate:

```text
generate code
  ↓
compile / type-check / test / execute
  ↓
return result to context
  ↓
generate a revision
```

The LLM and the execution environment play different roles in that loop.

## Why this matters for context reduction

The goal is not to send the whole repository. It is to identify the implementation, types, requirements, tests, and errors needed for the current change.

If new dependencies are discovered while reading those sources, expand the scope then. Context reduction makes project-specific evidence more targeted; it is not merely token saving.

## References

- [Evaluating Large Language Models Trained on Code](https://arxiv.org/abs/2107.03374)
- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)
