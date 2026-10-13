# Context Amount and Use

> Japanese Source of Truth: [コンテキストの量と使われ方](../../jp/LLMの仕組み/コンテキストの量と使われ方.md)

A larger context window can make it tempting to put the entire project into every request. Input capacity and effective task use are not the same thing.

This document connects LLM mechanics to the context-reduction methods in this repository.

## Too little information forces guessing

If the model does not receive the implementation being changed, it must fill gaps from general patterns. Without project-specific types, rules, and tests, a plausible modification may still be wrong for the repository.

Context reduction therefore does not mean deleting as much as possible. Necessary evidence comes first.

## More information is not monotonically better

Adding text makes it available as model input, but a long-context model is not guaranteed to use every item equally well.

*Lost in the Middle* observed position-dependent performance in long-context retrieval and QA tasks. The result does not establish a universal rule that longer input is always worse. It does establish a useful distinction between information that fits and information that is used reliably.

## Unrelated context is not free insurance

Unrelated files, duplicated explanations, or complete logs do not add task evidence simply because they fit.

Mixing current and obsolete requirements without labeling authority can also create competing conditions. Sending a large set of candidate files can force the model to perform the same search that could have been narrowed mechanically first.

Use search, indexes, and diffs to identify candidates, then read the original sources that matter.

## Do not replace every long source with a summary

Aggressive summarization can remove exceptions and conditions.

If a security specification defines which permission applies to which operation, "check authorization" is not an adequate substitute. Use summaries to locate information, then return to the original text for decisions that depend on details.

## Context can expand during work

You do not need to predict the complete scope perfectly before starting.

```text
request
  ↓
narrow candidates
  ↓
read relevant originals
  ↓
discover a dependency
  ↓
read that dependency and its tests
```

The key is to expand based on evidence rather than sending the entire repository preemptively.

## Give each kind of information a role

| Information | Role in the task |
| --- | --- |
| Request and completion criteria | define the goal and required checks |
| Implementation | establish current behavior and change location |
| Specifications and rules | define constraints |
| Tests | show expected behavior and regression checks |
| Errors and logs | show observed failures |
| Search results and indexes | locate candidate original sources |
| Summaries | transfer state compactly, but defer to originals for decisions |

Confusing those roles can turn a search result into "proof" of behavior or a stale summary into a current specification.

## Aim for necessary and sufficient context, not minimum context

A useful context:

- includes original evidence needed for the decision;
- includes required verification conditions;
- avoids unrelated bulk at the start;
- can expand when dependencies are discovered;
- retains paths back from summaries or indexes to original sources;
- records what has not been verified.

## What the model is doing underneath

The LLM receives the current context as tokens, updates representations through Transformer layers, and generates next tokens.

Context design therefore determines **which facts, code, and instructions become conditions for generation**. It is not a slogan that shorter prompts are always better.

Necessary long source code should be read. Unnecessary short notes should be excluded.

## Continue to repository methods

After the model mechanics, return to [Context Reduction Basics](../context-reduction-basics.md). Concrete workflows are listed in the [Method Index](../method-index.md), and a first code change can start with [Context Priority](../context-priority.md).

## References

- [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
