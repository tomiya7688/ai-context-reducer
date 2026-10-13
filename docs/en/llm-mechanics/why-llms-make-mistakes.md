# Why LLMs Make Mistakes

> Japanese Source of Truth: [なぜLLMは間違えるのか](../../jp/LLMの仕組み/なぜLLMは間違えるのか.md)

LLMs can produce incorrect statements in fluent, confident language. Calling this "hallucination" names a symptom but does not explain the mechanism.

The basic autoregressive objective is to predict likely continuation tokens under trained parameters and current context. Bare language-model inference does not automatically verify each sentence against a database, runtime, or external source.

## Next-token prediction and fact checking are different tasks

A plausible continuation is not the same thing as a verified fact.

A model can generate an API name that fits local naming patterns even when that API does not exist. The model's internal token scores are not a certificate that an external claim is true.

```text
plausible continuation
≠
externally verified fact
```

## Training data can be incomplete, conflicting, or stale

If relevant information is rare, contradictory, or old in training data, the model may not generate the correct continuation reliably.

Current library behavior, laws, prices, public APIs, and repository state often require checking current primary sources rather than relying on parameter memory.

## Ambiguous context creates room for guessing

A request such as:

```text
Fix the save behavior.
```

does not identify which setting, storage location, or completion condition applies. The model can fill in missing details from common patterns, but those guesses need not match the project.

Providing the target implementation, specification, tests, and actual error reduces how much must be inferred.

## Contradictory context also creates problems

If current requirements and stale notes are presented with equal apparent authority, the model must somehow resolve the conflict.

The lesson is not "long prompts always cause errors." A long original specification may be necessary. The useful distinction is between relevant current evidence and stale, duplicated, or unrelated material.

## Autoregressive generation can propagate an early error

Generated tokens become part of later context. If the model invents a nonexistent function early in a response, it may continue producing internally consistent code and explanation around that false premise.

Coherent continuation is not proof that the initial premise was correct.

## Instruction tuning does not remove all errors

Instruction tuning and preference training can improve helpfulness and truthfulness. InstructGPT reported such improvements while still documenting remaining mistakes.

Following user intent and independently verifying every claim are different capabilities.

## Use external checks

For code, useful checks include:

- reading the governing specification;
- compiling or type-checking;
- running related tests;
- inspecting the real error output;
- checking official dependency documentation.

For factual questions, retrieve trustworthy primary sources when the stakes require it.

The important record is not merely that a tool was called, but which source or test established which claim.

## "Say you do not know" is not a complete solution

Instructing a model to express uncertainty can help, but the model cannot perfectly detect every one of its own errors.

Next-token probabilities are also not equivalent to the probability that a real-world proposition is true. External evidence remains necessary for important decisions.

## Why this matters for context reduction

The repository uses a bounded workflow:

```text
clarify the change
  ↓
locate relevant original sources
  ↓
read implementation, requirements, and tests
  ↓
generate or modify
  ↓
verify with task-appropriate checks
  ↓
expand scope if evidence requires it
```

The goal is to reduce unsupported guessing while keeping verification grounded in original sources.

## References

- [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)
- [Evaluating Large Language Models Trained on Code](https://arxiv.org/abs/2107.03374)
