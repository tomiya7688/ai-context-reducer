# Make explanations understandable to their readers

If an AI's explanation repeatedly makes you ask “What does that refer to?”, “Who does it?”, or “What should I actually do?”, specify the reader and purpose before asking it to write, and have it check for missing information before responding.

For example, “Process the settings appropriately” does not tell the reader whether settings are saved or loaded, or whether the user needs to act. “Press Save in the settings screen, and the app writes the entered values to the settings file” identifies the user's action and the app's behavior. The operations and filenames below are examples from a fictional app.

Japanese version: [読者が理解できる説明に直す](../../jp/手法/読者が理解できる説明に直す.md).

## Decide when to use it

- **Instructions for first-time users**: Have the AI check whether the location, order of actions, and indication of success are clear.
- **Design explanations for developers**: Have it check whether responsibilities, reasons for the design, and conditions to preserve are clear.
- **Work reports**: Have it distinguish changes, completed checks, and anything not verified.

If expert readers already share a term's meaning, it does not need to be explained every time. Rewriting understandable text also creates more changes to review. Target sentences or paragraphs that prevent the reader from understanding or acting.

## 1. Specify who will read the finished text

Include these three points in the request:

| What to specify | Example for explaining how to save settings |
|---|---|
| Reader | A person using the app for the first time |
| What they know and what needs explaining | They can use screen buttons, but do not know about settings files or development terms |
| What they should do after reading | Save settings and check that they were saved |

```text
Reader: A first-time user of this app.
Prior knowledge: Can use the interface, but does not know development terms.
Purpose: Can save settings and check that they were saved.
Source material: [settings screen specification path or attached material]

Explain how to save settings, including the terms and steps this reader needs.
Use operations and results confirmed by the specified material.
Do not invent behavior or conditions missing from the material.
```

If the intended reader is unknown and would substantially change the explanation, have the AI ask first. For a short draft that is easy to revise, have it state an assumption such as “I am writing this for first-time users,” and check that reader assumption with the requester.

## 2. Have the AI check unclear references and actors

Give the AI the text and required material, such as specifications, and have it check these points separately:

| What to check | Question that helps find a problem |
|---|---|
| Referenced object | Which named object in the text does “this,” “that,” or “this process” refer to? |
| Who acts | Does the user act, should the AI do it, or does the app do it automatically? |
| Meaning of words | Does an unfamiliar abbreviation or technical term replace an explanation? |
| Action and result | Are the input or action and the indication of success clear? |
| Reasons and conditions | Are reasons, prerequisites, or exceptions needed for the decision missing? |

Calling the same thing “settings information,” “data,” and “input” across paragraphs can make it look like different things. Have the AI use consistent names for the same object. Conversely, “this button” can refer unambiguously to “the Save button” in the preceding sentence; the full name need not be repeated in every sentence.

If an object name or condition appears only in earlier conversation, include it in the text when the reader needs it. Preserving a sentence's meaning while making it understandable without its surrounding text is also addressed in [Choi and colleagues' paper](https://aclanthology.org/2021.tacl-1.27/). The research term appears near the end of this guide.

## 3. Have the AI verify whether suspected gaps are actually missing

First ask the AI to list questions a first-time reader might ask. Then have it check whether the text or referenced material already answers them.

For example, it might ask “Where can I tell that saving succeeded?” If the next paragraph already says “The app displays ‘Saved’ when saving completes,” no additional explanation is needed. If that answer is too far from the relevant instruction to find easily, moving it closer is another option.

Before adding an answer missing from the text, have the AI confirm it in the specified specification or actual operation. If it cannot confirm the answer, leave it as a question for the requester rather than making it up.

Do not require every sentence to include who, what, why, how, result, and exceptions. Add only information the reader needs to perform the intended action or make the decision.

## 4. Have the AI revise only the problematic sentences or paragraphs

Ask it to identify the location, why the reader would have difficulty, and the supporting source location, then revise only that sentence or paragraph. Have it check that the revision preserves the original meaning and conditions.

Finally, have it reread from the specified reader's perspective and check that the information needed for the intended action or decision is present. For instructions, having a person try the steps also helps. An AI reporting that a text is clearer does not establish that actual users understood it.

## Six examples of revisions

### 1. The reference of “this” is unclear

- Before: “Save this.”
- After: “Save the values entered in the settings screen.”

Naming the object makes it clear what is saved, even to a user who has not read the earlier conversation.

### 2. It is unclear who acts

- Before: “The settings file is checked.”
- After: “At startup, the app reads the settings file and checks that the required fields are present.”

This names the app and what it checks. If the instruction asks a user to inspect a file, write it accordingly: “Open the settings file and check the destination field.”

### 3. Technical terms replace an explanation

- Before: “Limit the scope with Context Routing.”
- After: “Tell the AI the task and ask it to list related documentation and code locations. Have it start its investigation there.”

The reader can tell what to ask the AI without guessing the terms' meanings. Put research terms or names useful for searches after explaining the action.

### 4. “Process appropriately” does not specify an action

- Before: “Process the settings appropriately.”
- After: “Choose the destination in the settings screen, then press Save.”

This states what the reader should do. If choosing a destination has conditions, confirm them in the specification and include them.

### 5. Prerequisites and results are missing

- Before: “Press Save.”
- After: “Choose the destination in the settings screen, then press Save. Saving is complete when ‘Saved’ appears.”

This adds the required choice and the indication of completion. Confirm in the specification or by using the app that a message like this actually exists.

### 6. Repeating names makes the explanation harder to read

- Over-expanded: “The user should press the settings screen's Save button. When the user presses the settings screen's Save button, the app saves the settings screen's settings.”
- After: “Press Save in the settings screen. The app saves the entered values.”

The instruction to the user and the app's behavior are separate, without repeating the location and button name. Omit repeated names where the actor and object remain unambiguous.

## Use it for one request

Attach this guide to the AI request, or save it somewhere the AI can read and specify its path. Also provide the text to revise, the intended reader, and supporting material.

```text
Follow [this method guide's path or attached guide] to check this explanation.
Target: [text or document path]
Reader: [intended reader]
Prior knowledge: [what they know and what needs explaining]
Purpose: [what they should understand, decide, or do]
Sources: [specifications, observed operation results, etc.]

First list questions the reader might ask, then check whether the text or references answer them.
Revise only sentences or paragraphs with confirmed gaps. Do not invent unsupported actions or conditions.
Return the revised text and briefly list changed locations, reasons, and questions still needing confirmation.
```

## Where to keep it for repeated use

Save shared reader assumptions, explanation checks, and revision steps briefly in your project's `docs/writing-guide.md`. If readers vary by document, specify the reader and purpose at the start of the document or in the current request.

In an instruction file your AI tool loads automatically, state when to use the guide and where it is. For an AI tool that supports `AGENTS.md`, for example, put this in the repository-root file:

```text
When writing instructions, design explanations, or work reports, read docs/writing-guide.md.
Confirm the reader and purpose for this text, and revise only sentences or paragraphs with missing explanation.
```

If there is no automatic loading configuration, specify `docs/writing-guide.md` in each request. Keep the shared procedure in one place instead of copying it into several instruction files, so one update is enough.

## Why it can reduce information repeated in conversation

A clear first explanation can reduce follow-up questions and repeated explanations about objects and actors. When continuing the conversation, you may avoid giving the AI the same explanation and correction instructions repeatedly. Avoiding regeneration of sound paragraphs also avoids extra versions to compare.

Checks and additions can make the initial request and response longer. Having another AI check the entire text every time also adds reading. Keep checks that help reduce follow-up questions or enable readers to act and decide. Do not claim reduced context usage without measuring token counts.

## Helper tools

- [doc-duplicate-hints](../../../tools/common/medium/doc-duplicate-hints/README.md) — Reports candidate duplicate passages in documents. It can help find whether added explanations repeat content in several places. It does not judge whether an explanation is understandable.

## About this method

Choi and colleagues use **decontextualization** to describe rewriting a sentence so it can be understood on its own while preserving its meaning, by including object names or necessary conditions from the surrounding text. [1]

This guide draws on that idea to check missing names and conditions, and combines it with specifying readers, verifying suspected gaps, and revising only problematic passages. That paper does not evaluate these example requests or measure their effect on token usage across a conversation.

## References

1. Eunsol Choi, Jennimaria Palomaki, Matthew Lamm, Tom Kwiatkowski, Dipanjan Das, Michael Collins. 2021. [Decontextualization: Making Sentences Stand-Alone](https://aclanthology.org/2021.tacl-1.27/). *Transactions of the Association for Computational Linguistics*, 9:447–461. DOI: [10.1162/tacl_a_00377](https://doi.org/10.1162/tacl_a_00377).
