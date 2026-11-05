# Checks for Recommending an External Tool

> Japanese source of truth: [外部ツール掲載基準](external-tool-reference-policy.ja.md)

Use this policy when ai-context-reducer names or links to a specific external tool. Even a brief mention can sound like an endorsement. Check its cost, commercial-use terms, attribution requirements, and ease of adoption first. If it does not meet the criteria, explain the general method without naming a product.

## Example: Recommending a test-finding tool

Suppose a guide wants to name Product X as an example for finding tests related to changed code. Before writing the recommendation, check the following in official sources:

- **Cost:** Can readers use the relevant feature for free? Is it more than a limited free trial?
- **Commercial use:** Can a company use it in a project or paid product?
- **Attribution:** Does ordinary use require the product name or credit in deliverables, UI, or README files?
- **Adoption:** Can developers and CI use it without unreasonable setup?

If all four are clear and the tool directly illustrates the method, link to the product and its official information. If the free option is personal-use only, commercial terms are unclear, or a persistent service contract is required, describe the general method instead. Do not list unclear tools as recommendations.

## Neutral technical examples are not recommendations

The free-use, commercial-use, attribution, and adoption checks above are the threshold for **recommending a product to readers**. Distinguish this from **documenting an external service as a neutral technical case study** directly relevant to a method.

A neutral example may describe a paid service or one with unverified conditions only where the implementation example materially helps readers understand the method. It must also:

- Identify the provider, date checked, **price and free-plan status, commercial-use terms, attribution verification status, setup, and data handling** in the same place, without implying endorsement or free availability.
- Clearly mark unknown conditions; never infer permission for commercial use, lack of attribution obligations, or free availability. Do not list such a product as a recommendation.
- Link to official sources and explain costs, access, and privacy constraints. Clearly identify performance and savings figures as vendor-reported when applicable.
- Keep the underlying method usable without the service; scope the case study to the method it illustrates rather than creating an unrelated product catalog.

## Check cost and license separately

“Free to use” and “usable commercially” are separate conditions. A free plan may restrict company use, and open-source software may still have conditions for particular uses or redistribution. Check official terms and the license against the use being described.

Using a tool during development is also different from including the tool itself in a distribution. If a tool runs only during a build, check the conditions for development use. If the tool is shipped to users, check redistribution terms and license notices. A license that allows free use may still require copyright or license notices when the software is redistributed.

This document does not make a legal determination for every user or distribution. If the conditions are unclear, do not guess; omit the linked recommendation.

## Verify official sources and keep them current

When adding a reference, check the official license, usage terms, pricing, and installation guidance. Keep links to the use case and information checked so readers can verify the conditions. Update or remove the reference if the terms change, official information is unavailable, or an equally suitable and easier option appears.

High performance alone is not a reason to include a product in a method guide. The method should remain understandable without it. Add a product example only when it clarifies the method, and do not create product lists unrelated to the topic.

## Keep technical boundaries elsewhere

The criteria for recommending a tool are separate from which external functions ai-context-reducer uses, what it provides as a fallback, and what it does not implement. Record those technical boundaries in the external-integration section of [tools/README.md](../../tools/README.md). Put commands, configuration formats, and output fields in each tool's README.

## Example request to check a reference

> Check only official pricing, usage terms, license, and installation guidance to decide whether this tool can be referenced for the stated use. Pair each conclusion with its source link. Mark unclear conditions as unknown instead of guessing. Check development use separately from redistribution.

## Optional tools and terminology

No special checker is needed. Treat the product's official pages as source material and compare each condition with the proposed example. This review is called **external tool reference screening**.
