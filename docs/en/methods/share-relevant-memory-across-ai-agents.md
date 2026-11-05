# Share memory across AI agents and retrieve only what is relevant

> Japanese Source of Truth: [複数のAIで記憶を共有し、必要な情報だけ読み出す](../../jp/手法/複数のAIで記憶を共有し必要な情報だけ読み出す.md)

After asking Codex to fix a bug, do you have to explain the same requirements to Claude Code for review? When research begins in ChatGPT and implementation continues in Copilot, passing the entire conversation to the next AI includes discussions that the next task does not need.

**Shared memory** stores reusable information outside the model so that different AIs and conversations can retrieve only the parts needed later. This does not retrain the model's parameters. Only when an application retrieves a memory and includes it in the current input can that memory condition the model's response. [1][2]

**You** decide what may be shared and who can read it. The AI can propose memory entries and search for relevant records. The memory store retains permitted information and returns selected records. You and the working AI must still verify the current source code, specification, and test evidence. This guide explains a method, not a mandatory external service. For Living Brain's connectivity, pricing, commercial-use terms, and data handling, see [External services](../ai-usage/external-services.md).

## Why sharing entire conversations is not enough

An investigation in chat A contains rejected hypotheses, long logs, old code, and unsuccessful attempts. Passing that entire history to chat B makes the next AI process it again. Doing the same across many AIs can expand both the current input and cumulative usage. Prompt caching may reuse computation, but it does not remove history from the model's context. [3]

With shared memory, retain **confirmed decisions, requirements, and links to original evidence** outside the model. The next AI searches for records relevant to its task and returns to the original sources when needed.

```text
AI A investigates specifications and code and finds a decision
  ↓ submits a candidate record with evidence
You / an authorized reviewer checks content, scope, and revision
  ↓
Shared memory stores content, source, revision, and access scope
  ↑                                              ↓
AI B searches from a separate chat
  → receives only selected, relevant records
  → verifies current original code and tests before editing
  → proposes an update when new evidence appears
```

**Storing much information externally does not reduce context if you load every memory at the start of every task.** When to search, what to return, and how much to include are all parts of the method. Retrieved memories are still ordinary input and count toward context capacity.

## Example: pass a changed settings location to another AI

Suppose a fictional application's settings file moved from `config/old.json` to `config/settings.json`. This is an illustrative workflow, not a measured AI experiment.

1. **AI A investigates.** You ask it to diagnose a settings-persistence bug. It checks current save and load code and related tests, then reports the current location with the source revision.
2. **You verify what is worth retaining.** AI A proposes that the current location is `config/settings.json` and the older location belongs to an obsolete specification. You check the evidence and authorize sharing in this project.
3. **The memory store records the result.** It retains the statement, original source, revision, check date, writer, and authorized reading scope. Unverified information remains a candidate, not a confirmed fact.
4. **AI B searches from another conversation.** You ask it to fix startup loading; it looks up the settings location. The store returns a short, relevant record and source location, not all old hypotheses or logs.
5. **AI B checks the current original.** If the source code has changed since the recorded revision, it retrieves the new implementation and tests rather than trusting the old memory as current truth.
6. **A later change updates the record.** Verified new facts supersede outdated ones so that old information is not repeatedly surfaced as current.

An illustrative record format follows. **This is not the format used by Living Brain or any particular product.**

```yaml
id: settings-location
scope: repository:example/app
status: verified
statement: "Settings are stored in config/settings.json"
source: src/config/storage.go
source_revision: "abc123 (illustrative commit ID)"
checked_at: "2026-11-05"
writer: agent-a
verified_by: project-maintainer
supersedes: settings-location-old
```

This record is **a pointer to current evidence, not a replacement for the original code**. Check the necessary code and tests before changing behavior. Failure to retrieve a record is not proof that the information does not exist.

## What to retain and what to exclude

Do not store every utterance forever. Select information likely to matter to later tasks, with known sources and scope.

| Information | Appropriate handling |
| --- | --- |
| Confirmed specifications and design decisions with rationale | Candidate for retention to avoid rediscovering decisions |
| Repository structure and existing procedures | Keep the existing documents authoritative; retain brief summaries and paths/revisions rather than duplicate bodies |
| Facts established by tests | Include tested revision, command, result, and date; past success is not current success |
| Unfinished tasks and constraints | Record scope, source, and expiry or review conditions; invalidate when complete |
| Investigation hypotheses | Retain only when useful, marked unverified, never mixed with confirmed requirements |
| Entire conversations, temporary logs, rejected attempts | Usually do not duplicate them in shared memory; link to controlled source storage if needed |
| API keys, credentials, and personal information | Check necessity, consent, permissions, and storage controls; do not place secret values into shared memory |

The 2026 *Shared Selective Persistent Memory* study selected reusable task specifications, data schemas, tool configurations, and output constraints, while discarding session-specific reasoning traces. [4] These are examples of useful categories, not the only possible taxonomy.

## Risks when several AIs update the same memory

Shared memory can propagate one agent's mistakes to others. [5]

| Risk | Example | What you set and what the AI/store verifies |
| --- | --- | --- |
| **Stale information** | AI B reuses a previously correct storage path after the code changes | Retain source revision, validation date, and validity status; recheck current originals and supersede outdated entries |
| **Contradictory writes** | AI A records JSON as canonical while AI B records a database as canonical | Do not overwrite blindly; check versions when writing, compare both sources, and resolve the authoritative choice |
| **Unauthorized disclosure** | An agent retrieves another project's private notes | Enforce user/project/agent scope on searches **and direct record retrieval**; tool connection alone is not authorization |
| **Missing provenance** | A short memory claims a test passed without saying when or where | Record writer, timestamp, source revision, command, and result so the original can be checked |
| **Instructions hidden in stored content** | A saved page says to skip required tests | Treat memory text as data, not as a new high-priority instruction; do not apply unapproved commands or permission changes |
| **Incomplete deletion** | A source is deleted but its summary remains searchable | Define retention and deletion for records, indexes, and copies; verify deletion |

Writing “only this agent may read” in a prompt does not enforce access control. The actual store must restrict operations. Concurrent updates may require version checks or review to detect writes based on stale state.

## How this compares with a Context Pack and source retrieval

| Method | What it passes forward | Best for | Relation to shared memory |
| --- | --- | --- | --- |
| **Full chat history** | Dialogue and tool outputs together | A very short continuation | Easily carries irrelevant attempts |
| **Conversation summary** | Condensed account of earlier turns | Continuing a conversation or briefing another worker | May omit needed conditions; unlike shared memory it needs separate cross-task retrieval and versioning. Verify against originals |
| **Context Pack / task handoff** | Goal, constraints, diff, next step | Continuing one bounded task | Retain reusable long-term facts separately when warranted |
| **Source retrieval** | Current original code/specification passages | Establishing what is true now | Confirms whether a shared memory is still correct |
| **Shared memory** | Source-linked, versioned knowledge reusable across tasks | Repeated tasks and multiple AIs | Adds retention, retrieval, updating, invalidation, and access control |

Shared memory does not replace task handoffs or original sources. A task note can hold current unfinished work, shared memory can hold a continuing design decision, and source code remains the evidence. A small project may need only a Git-managed note and search rather than a dedicated memory service.

## Research and the role of Living Brain

**Living Brain is a ChatAndBuild product name, not the general name for this method.** Its official materials describe capturing information from conversations and documents, organizing it as linked pages, and offering retrieval to different AI tools through APIs and MCP. [1][6] MCP is a connection protocol through which an AI application can call external tools.

Living Brain publishes token-cost reduction and question-answer accuracy figures from **its own internal evaluations**. The comparison systems and settings are limited. These are vendor reports, not measurements by ObaPick or proof that any agent will obtain the same reduction. [1]

| Publisher or authors | What they published | Contribution to understanding | What is not guaranteed |
| --- | --- | --- | --- |
| **ChatAndBuild**, Living Brain [1][6] | Product that stores and retrieves linked knowledge across AI tools | Practical interoperability | Universal reproduction of its internal benchmarks |
| **Prateek Chhikara et al.**, Mem0 [2] | Extracting, consolidating, and retrieving useful conversational memory | Selecting memory rather than retaining everything | Automatic correct access governance across all agents |
| **Wujiang Xu et al.**, A-MEM [7] | Dynamic memory linking and reorganization as new information arrives | Managing memory as it evolves | All linked information remains correct |
| **Sanjana Pedada et al.**, Shared Selective Persistent Memory (2026) [4] | Shared memory of reusable context, evaluated on specific enterprise tasks | Selecting reusable information and controlling access | Applying the reported effect sizes to every task or product |
| **Yanki Margalit et al.**, Governed Shared Memory (2026) [5] | Scoping, temporal supersession, provenance, and propagation, including observed production bugs | Treating governance as distinct from retrieval accuracy | That every implementation prevents leaks and contradictions |

Memory organization, retrieval, and multi-agent access control are separate engineering concerns even when products use similar terminology.

## How to measure whether shared memory helped

Compare three strategies using the **same task kind, starting source revision, and completion criteria**. Prefer testing each strategy on the same tasks. When using different tasks, assign them randomly and balance task difficulty, recording any remaining differences. Tasks of the same kind may still vary in difficulty. Prefer the same model, model version, and inference settings. Search and memory tools can differ by strategy, so record the actual tool configuration and permissions for every run rather than forcing identical tools. This is an evaluation plan, not a result from this guide.

- **Full history:** Pass earlier conversation content to the next agent.
- **Short task handoff:** Pass only goals, decisions, and unfinished work.
- **Selective shared memory:** Retrieve relevant stored facts and verify the current original sources.

Record per-call input/output and whole-task totals; search, extraction, storage, and update time/cost; recall of required evidence; correctness and tests; stale or contradictory memories; access-policy violations; and repeated explanations or edits. Keep failed runs. Do not double-count cached input or reasoning-token components, and mark unavailable measurements as unmeasured.

When retrieval requires an extra LLM to repeatedly summarize large documents, include its cost. **Shorter inputs do not by themselves prove lower whole-task cost or higher answer accuracy.** See [Estimate context use by task](../ai-usage/estimate-context-use-by-task.md) and [Context amount and use](../llm-mechanics/context-amount-and-use.md).

## Request example (text you send to the AI)

This example asks an AI to work with an existing authorized memory store; it cannot store or search data without the necessary access.

```text
The task is [task]. If earlier decisions or constraints are relevant,
search only the authorized shared memory scope for this task.
Do not load full history or the entire memory collection into context.

For each retrieved record, show its source and revision, date checked,
scope, and whether it is verified. Inspect original code, specifications,
and tests whenever the current decision depends on them.
If a record is stale or contradicted, propose an update with evidence.

Do not publish new shared memories, overwrite confirmed records,
or change access permissions until I approve. Do not store credentials
or personal data. Run necessary checks and report actual results and
any unverified areas.
```

Check what the AI actually retrieved against its original sources and tests. Without shared-memory access, continue with a small task note and direct source links instead.

## Sources and publishers

Sources checked November 5, 2026. This is original explanatory content prepared for ObaPick. No external code, configuration, or text is copied or bundled.

1. **ChatAndBuild**. [Living Brain official site](https://livingbrain.com/) — product concepts and the conditions of internally reported benchmarks.
2. **Prateek Chhikara et al.** (2025). [Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory](https://arxiv.org/abs/2504.19413) — memory extraction, consolidation, and retrieval.
3. **OpenAI**. [Prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching) — distinguishing reuse of input computation from removal of input.
4. **Sanjana Pedada, Aditya Dhavala, Neelraj Patil** (2026). [Shared Selective Persistent Memory for Agentic LLM Systems](https://machinelearning.apple.com/research/shared-selective-persistent-memory) — reusable shared context and enterprise evaluation, published by Apple Machine Learning Research.
5. **Yanki Margalit et al.** (2026). [Governed Shared Memory for Multi-Agent LLM Systems](https://arxiv.org/abs/2606.24535) — scope, time, provenance, and propagation with observed production failures.
6. **ChatAndBuild**. [Living Brain developer docs](https://docs.livingbrain.com/) — capture, retrieval, linking, and external AI connectivity.
7. **Wujiang Xu et al.** (2025). [A-MEM: Agentic Memory for LLM Agents](https://arxiv.org/abs/2502.12110) — dynamically linked and evolving memories.
