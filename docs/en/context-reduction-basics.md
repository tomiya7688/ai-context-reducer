# Context Reduction Basics

> Japanese Source of Truth: [コンテキスト削減の基本](../jp/コンテキスト削減の基本.md)

Even when context reduction for AI appears complex, most methods are one of the following three ideas, or a combination of them.

> 1. Perform static analysis outside the AI when possible  
> 2. Package repeated operations  
> 3. Let the AI read only a subset

Once these three principles are clear, individual tools and routing methods do not need to be treated as unrelated advanced techniques.

## 1. Perform static analysis outside the AI

There is no need to make an AI read all source code and infer information that can be determined mechanically.

When possible, collect information such as the following before it enters AI context:

- symbols / functions / types
- imports / dependencies
- file structure
- syntax / parser health
- changed files / changed symbols
- source/test relationships
- package / module relationships

Pass only the analysis results needed for the current task.

```text
source
  -> static analysis
  -> compact structure / candidates
  -> AI inspects only what is needed
```

Static analysis is not meant to understand the implementation instead of the AI. Its purpose is to remove information that can be determined mechanically **before the AI reads the source**.

## 2. Package repeated operations

When an AI repeatedly has to reason through the same exploration, verification, and decision sequence, the sequence itself consumes context and reasoning effort.

Package repeated work into a script, tool, workflow, or compact procedure.

Examples:

```text
search
  -> scope
  -> inspect
  -> validate
  -> stop
```

```text
changed files
  -> related source
  -> matching tests
  -> required validation
```

The operation does not need to be complex. If the same sequence is repeated often, it may be worth packaging.

Do not add excessive complexity merely for automation.

```text
expected repeated context saving
    > adoption + maintenance cost
```

Package repeated work only while this condition holds.

## 3. Let the AI read only a subset

The most direct way to reduce context is not to make the AI read everything.

Narrow the target first, then read only the required source / docs / tests / diff.

Useful mechanisms include:

- search
- routing
- index
- manifest
- scoped instructions
- changed-symbol information
- responsibility map
- compact diff
- summary / pointer

Do not turn summaries or indexes into replacements for the Source of Truth.

```text
pointer / summary / index
  -> locate the required area
  -> return to the original source
```

Reading only a subset and losing evidence are different things.

## Most methods combine the three principles

Most methods in this repository can be decomposed into these principles.

| Method | Static analysis | Package operations | Read only a subset |
|---|---:|---:|---:|
| Source Structure Index | ✓ |  | ✓ |
| Change / Test Impact Routing | ✓ | ✓ | ✓ |
| Change Routing Map |  | ✓ | ✓ |
| Responsibility Map |  | ✓ | ✓ |
| Hierarchical Context |  |  | ✓ |
| Remote Delta First | ✓ | ✓ | ✓ |
| Context Manifest / Context Pack |  | ✓ | ✓ |
| Policy Check | ✓ | ✓ | ✓ |
| Boilerplate Generation |  | ✓ |  |
| Syntax Health Validation | ✓ | ✓ |  |

More check marks do not mean a method is more advanced. They show which type of unnecessary reading, exploration, or repeated reasoning is being reduced.

## Tools are optional implementations of the principles

This repository includes several portable tools, but the tools themselves are not the goal.

```text
context reduction principle
  -> choose methods needed by the project
  -> automate only repeated parts with tools
```

If the same principle can be satisfied without a tool, that is valid.

Conversely, a tool is counterproductive as a context reducer if it causes the AI to:

- receive full output unchanged
- run unnecessary analysis every time
- read large tool instructions on every task
- rely on summaries that no longer point back to original sources

## First question when adopting something new

When evaluating a new mechanism or external tool, first ask:

```text
What does this reduce?

1. mechanical analysis the AI was inferring
2. repeated operations the AI was performing every time
3. unnecessary scope the AI was reading
```

If it fits none of these, reconsider whether it materially reduces context.

## Priority

Do not sacrifice correctness when applying the three principles.

```text
correctness
  > speed of reaching the work target
  > amount of context reduction
  > amount of automation
```

The objective is not to minimize reading at all costs. The objective is to reach the necessary information accurately with less context.
