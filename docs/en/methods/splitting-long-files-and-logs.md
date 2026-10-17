# Split Long Files and Logs into Parts for the AI

> Japanese version: [長いファイルやログを区切ってAIに渡す](../../jp/手法/長いファイルやログを区切ってAIに渡す.md)

When a needed file or log exceeds the amount the AI can receive at once, send it in smaller parts that follow its structure. Ask the AI to record which ranges it has read, the evidence it found, and what remains unread. This helps prevent it from treating a partial read as a complete review and lets it examine the needed material in order.

## Example: Find the cause of a failure in a long log

If a log is too long to send at once, ask the AI to find the error and its surrounding lines. If that part is cut off in the displayed output, ask it to read the rest using line numbers. If the cause depends on the sequence across the entire log, have it examine groups of operations in order.

## Decide between answering a question and reviewing the whole source

| Goal | Scope to request | Completion condition |
| --- | --- | --- |
| Explain one connection failure | Connection ID, failure, preceding settings or operations, and retry outcome | Evidence supports the cause, with no unresolved relationship that could change the conclusion |
| Check the entire log for a particular failure | Beginning to end of a fixed source | Every range checked with the same criteria and cross-boundary relationships compared |

Search results do not establish that nonmatching content was inspected. Report required ranges still unread as unverified when reviewing the whole source.

## Decide what to read

1. **Decide what you need to know.** Are you looking for the cause of one error, or checking the entire file?
2. **Check the full range.** Ask the AI to find the total line count and its main sections. Use headings for documents; named operations (functions) or groups of related operations and data (classes) for code; and timestamps or operation boundaries for logs.
3. **Split at meaningful boundaries.** Use headings and paragraphs for documents, functions and classes for code, and operation or time boundaries for logs. Use line counts when structure is unknown or one unit exceeds the limit. If a clue may cross a boundary, include a small amount of text from both sides.
4. **Send the needed ranges in order.** For each part, identify the file and its start and end positions. Ask the AI to use the same checklist each time. If the goal is a complete review, do not skip unread ranges.
5. **Record coverage and evidence.** Keep a short note of the ranges read, findings, evidence locations such as filenames, line numbers, or timestamps, and unread ranges. Do not keep only a summary while discarding the original locations.
6. **Reach a conclusion after reviewing the full scope.** Compare notes for relationships or contradictions across ranges. If some needed ranges remain unread, the AI must not report that the whole file was reviewed.

## Check reading limits and omitted output

The amount a file viewer returns at once and the amount an AI can handle across a conversation are different limits. If the output says it was truncated or some content was omitted, ask the AI to read those missing parts using line numbers or timestamps. You can also save long execution output to a file and have the AI read the needed ranges.

Choose the size of each part to fit the AI and file viewer you use. Leave room for the request, coverage notes, and response instead of filling the limit with file content. If one function or section is still too large, split within it and identify the function or section each part continues. There is no fixed character count that suits every environment.

For example, if you request lines 421–620 but only lines 421–510 are displayed, lines 511–620 remain unchecked. Request a smaller range to continue. If a single line is too long, use character positions when supported and retain the original line number. Do not mark undisplayed content as checked.

| Boundary | When it fits | Context to supply |
| --- | --- | --- |
| Heading, function, or related sequence of log entries | Structure is known and the unit fits | Parent heading, function name, operation ID, or equivalent |
| Fixed line or character count | Structure is unknown or a unit is too large | Original location, what it continues, and necessary surrounding ranges |

Overlapping adjacent ranges does not necessarily preserve every relationship. Search separately by name or ID for distant definitions or entries from the same operation.

## Save coverage notes and pass them to the AI

For work spanning several reads, have the AI save coverage notes in a file such as `docs/tasks/log-review.md`. This table illustrates a log split at operation boundaries.

First choose a fixed source snapshot. At the start of the record, include its path, snapshot identifier, total line count, purpose, and per-part checklist. Use a saved copy of a growing log; do not reuse old line numbers or findings unchanged when the source changes. If a fixed snapshot is unavailable, identify the time and range inspected without claiming coverage of a changing whole.

| Source | Lines | Status | Findings and follow-up |
| --- | --- | --- | --- |
| `logs/connection.log` | 1–180 | Checked | Connection settings at line 24; connection starts at line 160 |
| Same file | 181–420 | Checked | Failure at line 210; compare it with the settings at the end |
| Same file | 421–800 | Unchecked | Check retries through shutdown |

Keep the ranges checked and the evidence locations without copying the entire log into the note. When continuing in another chat, give the path in your request: “Read `docs/tasks/log-review.md` and continue from the unchecked ranges.” For a chat AI that cannot open files, paste the short note and the next range to read.

Pasting every range into the same chat accumulates content in that conversation. Splitting alone does not reduce the conversation’s total length. If you condense the notes further for a handoff, retain the unchecked ranges, evidence locations, and unresolved relationships.

For recurring work, save the procedure and checklist in, for example, `docs/ai/long-file-review.md`. In entry instructions the AI reads, say: “When examining material too long for one read, read this procedure and confirm the current coverage-record location.” If files such as `AGENTS.md` do not load automatically, provide the path or text in the request. Do not append task-specific evidence or progress to the shared procedure.

## Combine findings and check original evidence

1. Use the same checklist for each part. For logs, this might include operation ID, time, settings, failure reason, retries, and final state. For documents, inspect definitions of the same terms or conditions; for code, inspect inputs, state changes, and called operations.
2. Record facts, evidence locations, and relationships to check elsewhere. Distinguish “absent from this part” from “absent from the entire source.”
3. Compare records concerning the same operation or condition. For example, use connection IDs to establish whether settings at line 24 and a failure at line 210 concern the same connection.
4. If records grow long, combine related findings and then produce a shorter overall summary. Preserve links to the contributing records and original lines, including unverified items and counterexamples.
5. Return to passages supporting or contradicting the final conclusion. Restore conditions lost from summaries and limit conclusions when required ranges remain unread.

Compare the record’s source and coverage with actual displayed content or work history yourself. For whole-source review, check for gaps from beginning to end. An AI’s report alone does not prove correct inspection of every range.

## Example request to the AI

```text
The source is logs/connection.log. Check the entire log for the cause and order of the connection failures.
Use a fixed snapshot; record its identity, total lines, and per-part checklist.
First find the total number of lines and search for error types and timestamps to decide what to read.
If the log exceeds what you can receive at once, read it in order using operation boundaries.
For each part, record:
- lines checked
- findings
- evidence line numbers
- lines not yet checked
Save the notes in docs/tasks/log-review.md without copying the entire log.
If displayed output is cut off, read the missing parts too.
Mark only actually read ranges as checked, not every range requested.
Include context on both sides when a clue may cross a boundary.
Do not report the whole log reviewed until every required range has been checked.
At the end, compare the notes and report the conclusion separately from any unread range.
Compare settings, failures, and retries with the same ID; return to original evidence lines to check the conclusion.
```

If you only need an answer to a specific question, you do not need to split and read the entire file. Ask the AI to search for the relevant phrase or operation and read the matching location with its surroundings. Broaden the range if no relevant location appears or if the overall sequence or dependencies could change the conclusion.

For a chat that cannot read files, provide each range with snapshot identity, path, and start/end positions. Ask for findings and unread ranges before sending the next part.

## Decide whether to split the file itself

Dividing what the AI reads and changing the project’s file layout are different decisions. Do not split a file only because it is long. Check whether it contains features that change independently, whether their behavior can be checked independently, and how those parts refer to each other. For example, if settings loading and screen rendering share a file but can be changed and tested separately, consider splitting them. Closely connected operations using the same data may still require reading both files after a split. If splitting adds references or handoffs and makes the AI read more related files, keep the file layout and divide only the ranges sent to the AI.

| Criterion | Consider splitting | Prefer splitting only the reading ranges |
| --- | --- | --- |
| Independently changing work | Settings loading and rendering change for different reasons | Splitting stages of one calculation solely by character count |
| Explainable inputs, outputs, and users | A settings-loading operation with a clear calling interface | Many internal variables must still be shared |
| Effect on checks and navigation | Related tests map to each part and reading can start from the needed side | Parts repeatedly call each other and all must still be read |

Do not turn an investigation request into a source reorganization. If restructuring is needed, have the AI propose reasons, operations to move, users, and checks as a separate task. When splitting is undertaken, verify preserved behavior in consumers and related tests as well as the moved code.

## How this relates to other guides

[Choose which files to read](../context-priority.md) narrows candidate files. [Make a short list of where information lives](../context-manifest.md) provides starting points for finding necessary text. This guide handles selected text that is itself too long, including how to transfer it and record coverage.

## Why this can reduce what the AI reads

For a question about one issue, the AI can inspect only relevant parts and skip unrelated lines. A complete review still requires reading all the original material once. Coverage notes can reduce repeated reads of the same ranges and the need to pass a long conversation to another chat. Creating notes or summaries and checking relationships across boundaries adds work.

[Liu et al.](https://aclanthology.org/2024.tacl-1.9/) report that document question-answering performance can decline when relevant information is in the middle of an input. [1] This does not validate this guide’s log-review procedure. Splitting alone does not guarantee accuracy: check cross-boundary relationships and return to original ranges for information missing from notes.

Headings and paragraphs can reduce cuts through related content, but oversized units still need subdivision. Summarization and combining results add reading too; this guide does not establish a measured usage-reduction rate.

## Optional helper tools

- [Function and file relationship tool](../../../tools/common/large/source-structure-index/README.md) — shows connections between functions and files to help locate related code in a long source file.
- [File manifest tool](../../../tools/common/large/context-manifest/README.md) — lists file locations and sizes. It can help find large files and plan the reading order or how to divide them.

Existing search, line-based file viewing, or log-viewing features can support the same steps.

## About these methods

Dividing long text into smaller ranges is called **chunking**. [Dong et al.](https://aclanthology.org/2024.findings-emnlp.150/) describe **MC-indexing**, which splits structured documents into sections and retrieves them through text, keyword, and summary representations. [2]

[Sarthi et al.’s RAPTOR](https://arxiv.org/abs/2401.18059) builds summaries at multiple levels for retrieval. [3] It groups similar content and summarizes repeatedly. Its document-retrieval design differs from this guide’s sequential reading and whole-scope comparison.

These retrieval studies do not establish exhaustive code or log-review accuracy or usage savings for this guide’s requests.

## References

1. Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, and Percy Liang. “Lost in the Middle: How Language Models Use Long Contexts.” *Transactions of the Association for Computational Linguistics*, 2024. [Paper](https://arxiv.org/abs/2307.03172)
2. Kuicai Dong, Derrick Goh Xin Deik, Yi Quan Lee, Hao Zhang, Xiangyang Li, Cong Zhang, and Yong Liu. “MC-indexing: Effective Long Document Retrieval via Multi-view Content-aware Indexing.” *Findings of the Association for Computational Linguistics: EMNLP 2024*, 2024. [Paper](https://aclanthology.org/2024.findings-emnlp.150/)
3. Parth Sarthi, Salman Abdullah, Aditi Tuli, Shubh Khanna, Anna Goldie, and Christopher D. Manning. “RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval.” *International Conference on Learning Representations (ICLR)*, 2024. [Paper](https://arxiv.org/abs/2401.18059)
