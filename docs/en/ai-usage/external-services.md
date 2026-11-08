# External services

> Japanese source of truth: [外部サービス紹介](../../jp/AI利用/外部サービス紹介.md)

ObaPick explains methods for reducing the information supplied to AI. This page presents **external-service examples** connected to those methods and the conditions to check before using them.

**A listing here is not an endorsement or a recommendation to subscribe.** Paid services may be documented as factual examples. You can use the linked methods with your own documents and existing search tools without adopting any listed service.

## Shared memory: Living Brain

**Provider: ChatAndBuild Limited**  
**Official site: [Living Brain](https://livingbrain.com/)**  
**Related method: [Share memory across AI agents and retrieve only what is relevant](../methods/share-relevant-memory-across-ai-agents.md)**

Living Brain is an external service that organizes saved information from conversations and documents, allowing another AI task to search and retrieve relevant material. It illustrates how separate AI tools can use a common memory store. [1][2]

| Item to check | What the official sources showed on November 5, 2026 |
| --- | --- |
| **Capabilities** | Captures conversations, notes, links, and documents; searches related information; reads pages and returns compact indexes. [1][2] |
| **AI connections** | Official documentation describes MCP account sign-in for ChatGPT and Claude, and API-key-based integration for coding environments such as Claude Code and Codex. Available operations depend on the product and its configuration. [2] |
| **Pricing / free availability** | The published API plan is usage-based, with a **US$5 minimum top-up**. Listed model-processing rates are US$8 per 1M input tokens and US$0.50 per 1M output tokens. The Workspace comparison lists US$99 per month. **No ongoing free-use plan could be verified** from the published pricing page. Check the [current pricing page](https://livingbrain.com/pricing) before use. [3] |
| **Commercial use** | The [terms of service](https://livingbrain.com/terms-of-service) permit personal and commercial use, subject to plan and contractual terms. [4] |
| **Attribution** | We could not establish from the reviewed terms whether ordinary use requires crediting the product in your deliverables. **Do not assume that there are no attribution obligations**; verify the current terms or contact the provider for your use case. [4] |
| **Adoption** | An external account and connection setup are required. The ChatGPT/Claude connection uses sign-in in supported MCP clients; developer integrations may require API keys. [2] |
| **Data handling** | The service receives external data. Check confidentiality, access scope, retention, and deletion. Disconnecting an integration does not necessarily remove previously stored data. [4][5] |

These rates describe pricing presented for **Living Brain processing**, not necessarily the separate cost of ChatGPT, Claude, or another AI you use. Compare the whole cost of capture, search, summaries, and model input/output.

### What this example illustrates

An AI can search a shared store for records needed by the current task instead of receiving every conversation in full. This still requires checking whether a memory is correct, up to date, and actually relevant.

For example, a retrieved memory about a changed settings-file location should direct the AI to verify current specifications, code, and tests before changing anything. This is an illustrative workflow, not a measured claim about Living Brain accuracy or token savings.

### When not to adopt it

For a small, short-lived task, or when a Git-managed note and source search suffice, adding an external service is unnecessary. Include the service's storage, retrieval, communication, expense, and operational overhead when deciding.

## How to evaluate another external service

Check **provider and official sources, functionality, price and free allowance, commercial use, attribution, setup, and data handling**. Free access and commercial rights are different questions. Clearly mark conditions you cannot verify instead of guessing.

Distinguish a vendor's published performance or token-saving claims from measurements on your own tasks. ObaPick has not independently benchmarked the service on this page.

## Sources

**Checked November 5, 2026.** This page links to original provider materials; it does not bundle third-party code or prose. Pricing and terms may change.

1. **ChatAndBuild Limited**. [Living Brain official site](https://livingbrain.com/) — provider and overview.
2. **ChatAndBuild Limited**. [Living Brain developer docs: MCP with sign-in](https://docs.livingbrain.com/mcp/sign-in) — connecting, capturing, searching, and reading.
3. **ChatAndBuild Limited**. [Living Brain pricing](https://livingbrain.com/pricing) — API, Workspace, and Business plans.
4. **ChatAndBuild Limited**. [Living Brain terms of service](https://livingbrain.com/terms-of-service) — commercial use, plan conditions, and storage terms.
5. **ChatAndBuild Limited**. [Living Brain privacy policy](https://livingbrain.com/privacy-policy) — connected-service data, retention, and deletion requests.
