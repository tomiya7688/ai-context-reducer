# Keep Repeated Explanations in One Place

> Japanese Source of Truth: [文書の同じ説明を一か所にまとめる](../jp/文書の重複を管理する.md)

When the same instructions appear in the README, setup guide, and AI guidance, readers have more to read and updates can leave the copies out of sync. Put the detailed explanation in one document. In the others, keep a short, purpose-specific note and a link. Readers can then open only what they need, and it is clear where to make updates.

## Example: application setup instructions

Suppose the README, setup guide, and AI guidance each contain all the required software and setup steps. Whenever setup changes, someone has to edit all three. If one copy is missed, neither the reader nor the AI can tell which instructions are current.

Instead, put the full steps in `docs/setup.md`. The README can say, "See the setup instructions for supported environments and installation steps." AI guidance can say, "When changing setup, check these instructions." Both link to the same page. The AI follows the entry relevant to its task instead of reading and comparing duplicated steps. Updates also happen in one place.

## How to consolidate

When you find the same rule or instructions in multiple documents, first check who each document is for and what it needs to explain. If the purpose and details are the same, choose one document for the full explanation. Do not delete the other text mechanically. Keep the overview readers need in that location, then say what they can find at the link and when to read it.

For example: "For the settings format and compatibility rules, see `docs/settings-format.md`." This tells someone reading only the README where to go and why. It also lets the AI avoid opening details before they are relevant.

## Repetition that should stay

Not every repeated sentence needs to go. Keep usage requirements that a standalone document needs, warnings next to a risky action, and short overviews that help new readers. But copying the full specification means those copies must be updated separately again. Check that a short note is enough to use the document safely and that readers can reach the full explanation without guessing.

Similar wording does not always mean two explanations serve the same purpose. An introduction for beginners and operating steps for administrators, for example, may each need different details. Keep what each audience needs instead of deleting one copy just because the words overlap.

## Check the result

After moving the detailed explanation, confirm that each remaining note points to the right place, each link works, and the original documents still have the overview or warning their readers need. Automatically deleting or merging text based only on similarity can remove information needed by a different audience. Use duplicate-finding tools to locate passages for review; decide what to keep by checking each document's purpose.
