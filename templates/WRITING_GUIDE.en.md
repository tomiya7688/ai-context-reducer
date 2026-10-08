# Procedure for writing and revising understandable explanations

Use this procedure for instructions, design explanations, and work reports.
Obtain the reader, prior knowledge, purpose, target, sources, and output mode from the current request.
Ask before writing when missing conditions would substantially change the content.

1. Write for the reader and purpose, or read the existing explanation.
2. Check these dimensions separately to identify possible reader difficulties.
   - Object: Can “this” or “this process” be linked to one specific object?
   - Actor: Is it clear whether a person, AI, or program acts? Check changes of implied subject and passive wording that hides the actor.
   - Words: Are unfamiliar abbreviations and technical terms explained? Is the same object named consistently?
   - Required information: Are the object, action, reason, steps, result, and conditions needed for the purpose present? Not every sentence needs every item.
3. For each candidate, check whether the text or a linked reference available to the reader already answers it. Do not add duplicate answers.
4. Verify genuinely missing information against the specified sources. An answer available only in AI supporting material does not make the reader-facing explanation sufficient.
5. Revise only sentences or paragraphs with confirmed gaps. Add the answer or link to a reference the reader can access. Put essential steps and success indicators with the instructions. Do not invent facts; retain questions when evidence is unavailable.
6. Check that meaning and conditions are preserved and the reader has the information needed for the purpose. Avoid introducing unnecessary jargon; explain terms that are needed.

## Output

- For “findings,” briefly return only problematic locations, reasons, proposed revisions, and questions needing confirmation. If none are found, say no explanation gaps were found.
- For “complete revised text,” return the whole text including unchanged parts, without the long check log. Briefly append questions if unresolved facts prevent completion.
- Do not duplicate the full text, check tables, and JSON. Leave sound sentences unchanged.
