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

First ask the AI to list questions a first-time reader might ask. Then have it check whether the text, or a reference linked from it that the reader can access, answers them.

An answer found only in a specification supplied to the AI still leaves the reader's explanation incomplete. Use that specification to verify the answer, then add it to the text or link to a reference the reader can access. Put essential steps and success indicators with the relevant instructions.

For example, it might ask “Where can I tell that saving succeeded?” If the next paragraph already says “The app displays ‘Saved’ when saving completes,” no additional explanation is needed. If that answer is too far from the relevant instruction to find easily, moving it closer is another option.

Before adding an answer missing from the text, have the AI confirm it in the specified specification or actual operation. If it cannot confirm the answer, leave it as a question for the requester rather than making it up.

Do not require every sentence to include who, what, why, how, result, and exceptions. Add only information the reader needs to perform the intended action or make the decision.

## 4. Have the AI revise only the problematic sentences or paragraphs

Ask it to identify the location, why the reader would have difficulty, and the supporting source location, then revise only that sentence or paragraph. Have it check that the revision preserves the original meaning and conditions.

Finally, have it reread from the specified reader's perspective and check that the information needed for the intended action or decision is present. For instructions, having a person try the steps also helps. An AI reporting that a text is clearer does not establish that actual users understood it.

## Usually, have the authoring AI do a brief check

Normally, ask the AI that wrote the explanation to perform the four steps above. After finding possible gaps, have it check the text and references available to the reader, then revise only locations with confirmed missing information.

When requesting a check report, have it report only problematic locations, for example:

```text
“The settings are checked”: It is unclear whether the user or app checks them.
Revised to “At startup, the app checks the settings file,” based on the startup specification.
“Where to choose the destination”: Neither the text nor linked references explain it,
and supporting material does not establish it.
Question: Which screen lets the user choose the destination?
```

Do not request a pass/fail result for every item in every sentence or repeat the whole text in the check log. Leave understandable passages unchanged.

Specify one of these output modes in the request:

- **To inspect findings**: Return only problematic locations, reasons, proposed revisions, and questions needing confirmation. Do not duplicate the full text or the same findings in another format.
- **To receive finished text**: Omit the long check log and return the complete revised text. Include unchanged parts; do not abbreviate the requested deliverable. If missing evidence prevents completion, also return the necessary questions briefly.

## For important explanations, use a separate conversation as a reader check

Checking outside the authoring conversation can expose assumptions known only to the writer when any of these conditions applies:

- Publishing setup or operating instructions for first-time users.
- Readers repeatedly ask follow-up questions about the same explanation.
- The writer and reader have substantially different prior knowledge.
- A misunderstanding could lead to an implementation or operating mistake.

Open a new conversation and provide the reader, prior knowledge, purpose, and completed explanation. Provide references only when the intended reader can access them. Do not supply the writer's earlier conversation or internal specifications unavailable to the reader. Ask:

```text
Reader: [intended reader]
Prior knowledge: [what they know]
Purpose: [what they should be able to do]

Read only the following explanation and references linked from it that the reader can access.
Return locations and questions about additional information needed to achieve the purpose.
Do not guess answers or rewrite the whole explanation.
[completed explanation]
```

Give the returned questions to the authoring AI. Discard questions already answered in the text, verify actual gaps against supporting material, and revise only those locations. Keep questions without evidence for the requester to answer.

This is an additional check of reader understanding. Reading the text again in another conversation adds input and output. Start with the usual check for short internal notes or explanations whose readers share the required knowledge. Another AI understanding the text does not establish that people can follow the operations.

## Seven examples of revisions

These illustrative examples use a fictional app and a request to investigate with an AI. The app has a settings screen: selecting a file and pressing Load makes the app load the settings and display their values. Choosing a destination and pressing Save saves settings and displays “Saved.” Verify the facts against your own project's specifications or operation when revising real documentation.

### 1. The reference of “this” is unclear

- **Before**: “The app loads this and then displays this.”
- **What the reader cannot determine**: What is loaded and what is displayed?
- **After**: “The app loads the selected settings file and then displays the settings values on screen.”
- **What changed**: Only the two references were replaced with their object names.

### 2. It is unclear who acts

- **Before**: “The user selects a settings file. It is then loaded and its settings values displayed.”
- **What the reader cannot determine**: Does the user also load the file and display its values?
- **After**: “The user selects a settings file. The app then loads it and displays its settings values.”
- **What changed**: The second sentence identifies the new actor. The unambiguous reference to the selected file is preserved.

### 3. English terms do not explain the actions

- **Before**: “The AI investigation uses routing / scope / evidence / fallback.”
- **What the reader cannot determine**: What should they give the AI, how far should it investigate, and what happens if it finds no answer?
- **After**: “Tell the AI which material to read first and how far to investigate, and have it report the passages supporting its answer. If it cannot find an answer within that scope, have it choose the next material to read.”
- **What changed**: The list of terms was replaced with the user's instructions and the AI's actions.

### 4. Abstract verbs do not specify an operation

- **Before**: “Process the settings appropriately.”
- **What the reader cannot determine**: What should they actually do?
- **After**: “Choose a destination in the settings screen and press Save.”
- **What changed**: “Process appropriately” was replaced with the location and concrete operations.

### 5. The use condition and required input are missing

- **Before**: “Press Load.”
- **What the reader cannot determine**: When should they use it and which file is the input?
- **After**: “To use settings saved in a file, select that file in the settings screen and press Load.”
- **What changed**: The use condition and file selection were added before the original operation.

### 6. Success cannot be recognized

- **Before**: “Choose a destination in the settings screen and press Save.”
- **What the reader cannot determine**: What indicates that saving has finished?
- **After**: “Choose a destination in the settings screen and press Save. Saving is complete when ‘Saved’ appears.”
- **What changed**: The operation remained unchanged; one sentence naming the success indicator was added.

### 7. Repeating explicit names makes the text unnecessarily long

- **Before**: “The user presses the settings screen's Save button. When the user presses the settings screen's Save button, the app saves the settings screen's settings values.”
- **What the reader cannot determine**: Nothing about the object or actor is missing. This example instead repeats the same location and button name, making the text harder to read.
- **After**: “Press Save in the settings screen. The app saves the entered settings values.”
- **What changed**: Repeated names were removed, and the user's instruction was separated from the app's behavior. Behavior and conditions were preserved.

## Compare follow-up questions before and after

A longer explanation is not by itself evidence of improvement. Keep the reader and purpose fixed, and compare questions whose answers cannot be determined from the explanation.

### 1. Keep the compared text and reader conditions consistent

Save the original and revised explanations of the same content, and specify the reader's knowledge and purpose. For example: “A first-time app user can save settings and recognize completion.” Separately verify that revised operations and conditions agree with supporting material.

You can keep the text in `docs/explanation-check/before.md` and `docs/explanation-check/after.md`, and reader assumptions, purpose, and results in `docs/explanation-check/results.md`. These paths identify what to give the AI and where to record findings. For one use, attachments or text pasted into a request are enough. Remove temporary files when the check is finished and the records are no longer needed.

### 2. Collect questions the explanation cannot answer

Start by reading the text yourself and checking these questions. When another person reads it, keep their prior knowledge consistent with the intended reader.

- What does this refer to?
- Who performs the action?
- What does that word mean?
- What exactly should be done?
- When is it used, and with which input?
- What indicates completion?

Include only questions needed for the purpose. Combine duplicates and exclude questions answered by the text or a linked reference available to the reader. Check the original questions against the revision and include any new questions introduced by the revision.

For an AI check, use the same material boundaries as the [separate-conversation reader check](#for-important-explanations-use-a-separate-conversation-as-a-reader-check). Give the original and revised texts to separate new conversations. Do not give either conversation the other text or the author's previous conversation. Combine the questions yourself and check whether each explanation answers them.

```text
Target: [before.md or after.md path, or attached text]
Reader: [intended reader]
Prior knowledge: [what they know]
Purpose: [what they should be able to do]

Read only the target text and references linked from it that the reader can access.
Return questions that require asking for additional information to achieve the purpose,
using “location / question.”
Exclude duplicates and questions answered by the text. Do not guess answers.
If none remain, return “No additional questions.”
```

### 3. Record remaining questions and actual repeated work

Verify the questions yourself. For both versions, record the answer location or that it is missing. For example 6 above, “What indicates saving is complete?” remains unanswered before revision; afterward, “Saved” supplies the answer. This is an illustration, not a measurement involving an AI or real users.

You can fill this table in `results.md` for each case. Do not treat blank or unmeasured entries as zero.

| Record | Before | After |
|---|---|---|
| Date and reviewer; model and settings if an AI checks | [fill in] | [fill in] |
| Unanswered questions and their count | [fill in] | [fill in] |
| Answer locations in text or linked references | [fill in] | [fill in] |
| Actual repetitions of the same explanation | [unmeasured if unavailable] | [unmeasured if unavailable] |
| Exchanges requesting text revisions | [unmeasured if unavailable] | [unmeasured if unavailable] |
| Incorrect explanations or missing required operations or conditions | [fill in] | [fill in] |

Candidate question counts and actual follow-up questions in conversation are different measures. An AI's candidate questions do not establish actual reader understanding or a measured reduction in repeated explanation. Fewer questions do not constitute improvement if the revision introduced incorrect operations or conditions.

### 4. Claim reduced reading only within what was measured

Adding object names or operations may lengthen the first response. The aim is to reduce subsequent questions, repeated explanations, and revisions caused by missing meaning. Different prior knowledge changes how much explanation readers need.

If you compared only unanswered questions, say “For this reader and example, fewer questions remained unanswered by the explanation.” Discuss fewer repetitions or revision exchanges only when actual conversations were recorded.

If token counts are available, compare input and output from the initial request through completion, including additional checks. Use the same model, settings, and task conditions; do not treat one response's token count as the whole conversation's saving. Without token measurements, do not claim that total tokens decreased, specify a reduction percentage, or promise a reduction. Do not generalize a few examples to all readers or tasks.

## Use it for one request

Attach the [brief checking procedure template](../../../templates/WRITING_GUIDE.en.md), or save it where the AI can read it and specify its path. Fill in the current request's conditions:

```text
Check the explanation using the attached procedure (or [saved procedure path]).
Target: [text or document path]
Reader: [intended reader]
Prior knowledge: [what they know and what needs explaining]
Purpose: [what they should understand, decide, or do]
Sources: [specifications, observed operation results, etc.]
Output: [findings only / complete revised text]
```

## Where to keep it for repeated use

Copy the [template](../../../templates/WRITING_GUIDE.en.md) to your project's `docs/writing-guide.md`, and add shared reader assumptions if applicable. If readers vary by document, specify the reader and purpose at the start of the document or in the current request.

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

The idea of another reader receiving an explanation and continuing the task is also related to [West and colleagues' paper](https://aclanthology.org/2026.eacl-long.386/). [2] Their **tandem training** intermittently hands generation to a weaker model while training a stronger one, encouraging solutions the weaker partner can continue correctly. This guide's separate-conversation reader check draws on that perspective; it does not implement the training method.

## References

1. Eunsol Choi, Jennimaria Palomaki, Matthew Lamm, Tom Kwiatkowski, Dipanjan Das, Michael Collins. 2021. [Decontextualization: Making Sentences Stand-Alone](https://aclanthology.org/2021.tacl-1.27/). *Transactions of the Association for Computational Linguistics*, 9:447–461. DOI: [10.1162/tacl_a_00377](https://doi.org/10.1162/tacl_a_00377).

2. Robert West, Ashton Anderson, Ece Kamar, Eric Horvitz. 2026. [Tandem Training for Language Models](https://aclanthology.org/2026.eacl-long.386/). *Proceedings of the 19th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers)*, 8265–8278. DOI: [10.18653/v1/2026.eacl-long.386](https://doi.org/10.18653/v1/2026.eacl-long.386).
