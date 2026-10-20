# What Does an LLM Know?

> Japanese Source of Truth: [LLMは何を知っているのか](../../jp/LLMの仕組み/LLMは何を知っているのか.md)

When an LLM answers a history question or describes an API, it is tempting to say that the fact is "stored in the model." Treating that storage like a database makes important failures harder to understand.

Training distributes statistical structure across model parameters. Generation then combines those parameters with the current context.

## Parameters are not a lookup table of documents

A database has explicit records and keys. Language-model training instead updates many numerical parameters to reduce prediction error across many examples.

Grammar, factual associations, styles, and code patterns can therefore be represented in distributed form rather than as one stored "question → answer" row.

## That does not mean models never memorize

"Not a database" does not mean "never reproduces training examples."

Research on GPT-2 showed that some training strings could be extracted verbatim with suitable querying. Models can therefore both generalize patterns and memorize some examples.

"Everything is memorized" and "nothing is memorized" are both oversimplifications.

## Producing an answer is not the same as providing provenance

A model may correctly generate "Tokyo is the capital of Japan" without retrieving one identifiable source record for that claim.

Ordinary parameter-based generation does not automatically provide a document ID proving where a fact came from. When provenance matters, retrieve an original source and make it available for comparison.

## Whether knowledge is expressed depends on input

The same model can answer differently depending on wording, language, examples, and surrounding context because output depends on both parameters and current input.

One failed prompt therefore does not completely characterize what information a model can express, and one successful answer does not guarantee reliable recall under every phrasing.

## Separate trained knowledge, current context, and tools

For software work:

```text
trained parameters
  general language, code, and world patterns

current context
  current specification, code, tests, errors

external tools
  latest sources, search results, runtime observations
```

A model may know common Go syntax but cannot be assumed to know yesterday's private function rename or today's failing test.

## A practical interpretation of "knows"

For project work:

- verify important facts against sources when needed;
- treat project-specific details as current source material rather than assumed training knowledge;
- check current information externally instead of guessing a training cutoff;
- do not treat confident wording as proof.

## Why this matters for context reduction

Assuming "the model probably knows it" can omit project-specific requirements. Assuming "the model knows nothing" leads to sending every document.

The useful decision is which parts can rely on general trained capability and which current facts must be provided and verified.

## References

- [Extracting Training Data from Large Language Models](https://arxiv.org/abs/2012.07805)
- [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165)
