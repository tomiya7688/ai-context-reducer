# What Is Context?

Why can you ask an LLM to “fix the function from earlier”? Did it permanently learn that function? And why can sending just “next” produce a large input-usage count?

**Context is the information available to condition the model's current generation.** It can include instructions, conversation, code, documents, and tool results. This guide focuses on autoregressive LLMs that receive text as a sequence of tokens and generate a continuation. A token is a unit the model uses to handle text, not necessarily one character or word. [1]

> Japanese Source of Truth: [コンテキストとは何か](../../jp/LLMの仕組み/コンテキストとは何か.md)

We follow the application that supplies information separately from the model that computes an output. Capacity limits are covered in [What Is a Context Window?](what-is-a-context-window.md), and processing and billing in [Context Amount, Computation, and Cost](context-compute-and-cost.md).

## Why are instructions alone not enough?

Suppose you ask two fictional applications to “fix the setting that disappears after restarting.”

| Application | Current implementation | What to check before making a change |
| --- | --- | --- |
| A | Saves settings to a JSON file | Whether saving and startup loading use the same file |
| B | Saves settings to a database | Whether writes are committed and which value startup retrieves |

This is an illustrative example, not a diagnosis of either bug. The request is identical, but the implementations and checks differ. Knowing general JSON or database usage does not establish **which implementation this task concerns**.

The application or user therefore supplies the current implementation, governing requirements, and related tests. An autoregressive model calculates candidate next tokens from the current sequence containing that material. Both “fix it” and the code being fixed condition that calculation. [1][2]

Different code changes the conditions and may change the proposed modification. Conversely, without information showing the difference, the model lacks evidence for distinguishing these projects. Rather than filling the gap with a guess, the workflow needs to retrieve the files or report the missing information.

Context is not decoration attached to an answer. It is **input that connects general capability to this particular task**.

## Who supplies what to the model?

A chat or coding agent need not send only the sentence the user typed. The application calling the model collects information and assembles it into a format that includes conversation roles and boundaries. [1][3]

| Possible input | Example of who supplies it | What it communicates |
| --- | --- | --- |
| System or project instructions | Service, developer, or user | Constraints and permitted work |
| Current request and completion criteria | User | What to change and verify |
| Selected conversation history or task notes | Application | Decisions already made and current state |
| Code, specification, and test text | File retrieval or user | Original evidence for this decision |
| Tool descriptions | Application | Available operations and their arguments |
| Search results, errors, and test results | Executed programs | Candidate locations and observed outcomes |

This is an example composition, not a claim that every service includes every item on every call. Multimodal models may also receive image or audio representations, whose accounting needs separate checking.

For example, if the application adds the task list and previous result before “next,” the model can choose the next task from those conditions. The newly typed text is short; **the complete input assembled for this call may not be**.

## How does the model use context?

The basic text-processing sequence is as follows. [1][2]

1. **A tokenizer converts text into token IDs.** It maps words, fragments, and symbols to the model's units and identifiers.
2. **The model converts IDs into numeric arrays.** These arrays are called vectors. Position information also helps represent the order of the text.
3. **Transformer layers update the vectors at each position.** Attention computes relationships among permitted positions and combines information from them.
4. **Generation selects the next token.** The final position's representation produces candidate scores, and the generation method selects a token.
5. **The selected token becomes a condition for further generation.** The answer already generated also affects what comes next.

This is not merely storing the supplied text. It processes that material and incorporates it into the conditions for the next output. See [How LLM Generation Works](how-llm-generation-works.md) for the detailed sequence.

Including code does not execute it. An application-side program runs tests and returns the result. A generated sentence saying “passed” is not, by itself, evidence of a successful execution.

## Stored information and currently available information differ

Several distinct mechanisms are easily conflated as “memory.”

| Location | What it contains | Relationship to current generation |
| --- | --- | --- |
| Trained parameters | Numbers adjusted during training and used in computation | Support the model's general output tendencies and capabilities |
| Application-stored conversations or notes | Earlier text and task records | A separate mechanism must make relevant information available to the current computation |
| External files such as a repository | Current code and specifications | Naming a file is not equivalent to retrieving and supplying its contents |
| Current context | Instructions and evidence available to this generation | Conditions the current next-token predictions |

Ordinary inference does not retrain the model's parameters after every conversation. [Training vs. Inference](training-vs-inference.md) explains the distinction between inference state and training.

Even when the application retains history, omitting passages or replacing them with a summary changes the current input relative to the text visible in the interface. Some services accept a previous response ID and carry state forward on the server. Not retransmitting the full text over the network is different from removing that information from model processing. [3]

Do not infer that every earlier detail remains available solely because it was attached before or appears in the same chat. For important decisions, check the revision and passage consulted, and retrieve the original again when necessary.

## What an external program searches is not what the LLM receives

Suppose a search program scans a thousand files and returns three candidate paths. At that point, the LLM receives the candidate information returned, not a thousand files of source text.

Only after the application retrieves the relevant passages and returns them can their contents condition the next generation. A path identifies where to look; it does not supply the document. The following is an example division of responsibilities.

```text
User: asks for a settings-persistence fix
Model: requests a search for related locations
Search program: scans files and returns candidate paths
Model: requests relevant candidate contents
Retrieval program: returns code, specification, and test passages
Model: generates a proposed change from the returned evidence
```

Searching may also consume time or money. Record that work separately from the tokens supplied to the LLM. This distinction underlies searching first and then providing only the needed passages.

## What does “context usage” measure?

Using one label for different quantities obscures what is being reduced.

| Quantity | Question it answers |
| --- | --- |
| Input tokens in one call | How much input was supplied this time? |
| Output tokens in one call | How much was generated this time? |
| Capacity used by current processing and its limit | How much additional evidence or generation can fit? |
| Cumulative input and output across calls | How much was used across the task? |

For example, including the same 2,000-token passage in three inputs produces 6,000 cumulative input tokens for that passage. This does not mean 6,000 tokens are held simultaneously. It is an accounting example; pricing separately considers categories such as caching.

Follow the model's specification for output that includes internal reasoning tokens and for capacity accounting. [3] When inspecting usage, establish whether a value is per-call or cumulative, and whether it is a total or a component.

**Reducing context first means selecting what information conditions the current generation.** Starting from that idea, rather than treating context as a separate fuel being consumed, makes capacity, computation, and billing easier to distinguish. Continue to [Context Amount and Use](context-amount-and-use.md) for what to retain to support quality.

## References

Checked October 18, 2026. Applications, quantities, and divisions of responsibilities are illustrative, not measurements or claims about a particular product's internal architecture.

### Research papers

- [2] Ashish Vaswani et al. (2017). [Attention Is All You Need](https://arxiv.org/abs/1706.03762). NeurIPS — position representations, Attention, and autoregressive generation.

### Official documentation, technical reports, and practical guidance

- [1] Hugging Face. [Chat templates](https://huggingface.co/docs/transformers/chat_templating) — assembling conversation roles and content into a model-appropriate token sequence.
- [3] OpenAI. [Conversation state](https://developers.openai.com/api/docs/guides/conversation-state) — state carryover, input accounting, and context windows; used as a product-specific example.
