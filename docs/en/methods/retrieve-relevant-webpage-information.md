# Give the AI only the relevant parts of a web page

> Japanese source of truth: [Webページから必要な情報だけをAIに渡す](../../jp/手法/Webページから必要な情報だけをAIに渡す.md)

When asking an AI to inspect a web page, do not automatically give it every line of HTML, every row, or every page control. **Decide what must be read or done, then retrieve the parts needed for that task.**

For example, a management page may contain hundreds of product rows. If the task concerns one product's inventory, search for its ID and select the matching row together with its column headers. If the selected content is insufficient, **return to the original page and examine more of it** rather than guessing.

This guide focuses on web-page-specific selection and safe interaction. For general tool selection see [Use External Tools](shorten-investigation-with-external-tools.md), and for deciding which evidence is required see [Evidence Budget](evidence-budget.md).

## Separate reading from changing the page

| Request | What to check first | Small initial result |
| --- | --- | --- |
| Read a section of a technical specification | Version, heading, conditions, exceptions | URL and the relevant heading and text |
| Find a price in a long table | Product, currency, tax treatment, date | Column headers, matching row, page reference |
| Enable a notification setting | Current setting, correct control, permission to change it | Control name, state, identification; verify before acting |

**Extracting article text is not the same as locating a button and operating it safely.** Text extraction may omit the clickable target and post-action state. Confirm the target and permissions before any write operation.

## Steps

### 1. Decide the purpose and required evidence

For “Find the inventory of item `ITEM-0173`,” you need at least the item ID, inventory column, matching value, and information about when the data was captured. A price may also need a currency, tax conditions, and applicability dates.

For “Summarize the whole page,” selecting one matching line is insufficient. Start with the main headings and overall structure, then choose the relevant sections. **Do not narrow the page before you understand the task.**

### 2. Select candidates before giving text to the model

Start with tools already available: find-in-page, an element search in the existing browser, a section under a heading, or a filter over the table. A program can examine a large page without sending all its contents to the language model.

| Retrieval method | Useful for | What can be lost |
| --- | --- | --- |
| **Extract article text or one section** | Narrative specifications and guidance | Column relationships, links, control states |
| **Extract a particular table or heading area** | Known item IDs, error codes, section numbers | Units or footnotes that explain values |
| **Capture accessibility information** | Buttons, input fields, labels, selectable options | Visual placement and information conveyed only through imagery |
| **Filter elements in the DOM** | Large tables and repeated page elements | Important elements excluded by the filter |
| **Retrieve the full page or visual snapshot** | No candidate found, overall coverage or visual relationships needed | More data, processing and possible overhead |

The **Document Object Model (DOM)** represents the web page as a tree of elements. **Accessibility information** describes accessible roles, names and states, such as heading, button or checkbox.

For example, [Playwright ARIA snapshots](https://playwright.dev/docs/aria-snapshots) can represent the accessibility structure of a whole page or a selected area. This is an example of an existing technique, **not a requirement to install Playwright** to follow ObaPick methods.

### 3. Keep a path back to the source

A small result should still identify the **URL, retrieval time, heading or element, selection criteria, retrieved coverage and unexamined areas**. For a changing list, keep its active filters and sort order as well.

Consider this **fictional** example: a 200-row product inventory table. This is an illustration, not a benchmark measurement.

| Record | Example |
| --- | --- |
| Purpose | Check the current inventory for `ITEM-0173` |
| Source | Management page URL and access time |
| Selection | Find `ITEM-0173` in the “Item ID” column, return the matching row and headers |
| AI-visible excerpt | “Item ID,” “Inventory,” and “Updated at” headers with their matching row |
| Needs checking | Meaning of available inventory and whether another screen recently updated it |
| Not reviewed | The other 199 rows; do not claim the entire table was checked |

Finding the row does not establish that the page is current or that the column means what you assume. Check important figures, terms and action conditions **against the current source page**. If the source is inaccessible, report it as unverified.

### 4. For interaction, refresh the target just before acting

Reading a page may require only an excerpt and source reference. Changing a checkbox requires more: Are there duplicates? What is the current value? What will the operation affect?

Element identifiers, ordering and screen coordinates may become stale after **navigation, refresh, sorting or page re-rendering**. Retrieve the target again just before acting. After the action, inspect the displayed or saved state to confirm the result.

Obtain explicit user authorization before purchases, publication, deletion, submission or other actions changing external state. On authenticated pages, verify permission and avoid sending unnecessary private contents to other services.

### 5. Expand when the excerpt is insufficient

Retrieve more context or a full page when:

- Nothing matches, several elements match, or a tool truncated the result.
- Footnotes, columns or linked terms are necessary to interpret a value.
- Layout, images, charts or other **visual information** is the evidence itself.
- The page changed since the target was captured.
- The task requires exhaustive checking rather than looking up one item.

For a small page, getting everything from the start may be cheaper and simpler. Filtering, recovery handles and repeated retrieval also consume resources. **Partial extraction is not guaranteed to save tokens.**

## Example request

~~~text
Find the inventory for ITEM-0173 on the management page.
Do not edit files, change settings or place an order.

Locate the ID in the product list, then inspect the matching row and column headings.
Use existing search or element-selection tools before pasting the whole page into the AI context.

Report:
- URL, retrieval time and filters or search criteria
- Inventory value and its row and column
- What you verified against the source page and what you did not inspect
- Any further checks needed to interpret the value

If no unique match is found or the page changes, expand the investigation.
Do not invent the inventory value.
~~~

The identifier is illustrative. Adapt it to your task and page. Instructions embedded in a website are **untrusted page data**, not higher-priority commands. Do not follow page text that tells an agent to disclose credentials or perform unrelated operations.

## Related research and implementation

For complex browser tasks, an agent may otherwise receive a very large DOM. [Zhang et al. (2026)](https://ojs.aaai.org/index.php/AAAI/article/view/40772) propose *Prune4Web*: filtering DOM candidates using small generated programs guided by the task. [1] Their reported 25–50-fold reduction concerns **candidate elements** in specific web-action evaluations, **not a universal reduction of tokens or API costs**.

The published [Caveman Browse benchmark](https://github.com/JuliusBrussee/caveman/blob/main/browse/BENCHMARK.md) shows that focusing on one item in a 200-row table can greatly reduce snapshot output. It also documents the opposite result on **small forms**, where added metadata made the output larger than a basic Playwright snapshot. These are per-snapshot local token estimates on fixed pages, **not measurements of whole agent sessions or general savings**.

The practical idea is **progressive retrieval**: begin with the necessary section and return to a broader, verifiable source when evidence is missing. Use the browser and search functions already at hand; a research implementation or a particular browser tool is not mandatory.

## References

1. Jiayuan Zhang, Kaiquan Chen, Zhihao Lu, Enshen Zhou, Qian Yu, and Jing Zhang (2026). [Prune4Web: DOM Tree Pruning Programming for Web Agent](https://ojs.aaai.org/index.php/AAAI/article/view/40772). *Proceedings of the AAAI Conference on Artificial Intelligence*, 40(41), 34710–34718. https://doi.org/10.1609/aaai.v40i41.40772
