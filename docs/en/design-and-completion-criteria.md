# Set Design and Completion Criteria First

> Japanese Source of Truth: [設計と完了条件を先に決める](../jp/設計と完了条件を先に決める.md)

Before asking an AI to implement a task, the person requesting the work briefly decides what should change, what should stay as it is, and what must be checked for the work to count as complete. Put those decisions in the request or Issue and give them to the AI. It can then start without inferring the design intent from old conversations or broad areas of code.

## Example: changing the CSV date format

Suppose the CSV output date format must change. Before implementation, the person requesting the work decides: "Change the output format only; do not change the input format or public command. Change the date-output code and check examples of the old and new formats in its test." If the change may affect existing users, include that compatibility check as well.

With these conditions in the request, the AI can start with the date-output code and its tests. It does not need to explore screens, input handling, or old discussions to guess the scope and completion criteria. If implementation reveals facts that conflict with the note, the AI should stop and ask the requester before proceeding.

## Give the criteria to the AI

Put the decisions where the AI receives the task. If you are using chat, include them in the same request. If they are in an Issue or a work note, tell the AI to read that Issue or file. Merely storing a note somewhere does not mean the AI has seen it.

For example, add this to the request:

```text
Change plan:
- Change: Format CSV output dates as YYYY-MM-DD instead of YYYY/MM/DD
- Keep: The CSV input format and public command
- Done when: Output uses the new format, while input and command behavior remain unchanged
- Check: Verify the new format in the date-output test
Implement after confirming these conditions. If they conflict with the code, ask me before continuing.
```

The requester does not have to draft the note alone. The AI can propose one from the request, then wait for the requester to review and approve it before implementation.

## What to record

Keep only decisions relevant to the task:

- **Goal**: whose problem the change solves
- **Design and boundaries**: which behavior will change and which will stay as it is
- **Conditions to preserve**: command usage, output format, file locations, or compatibility with existing users
- **Completion criteria**: what must work from the user's point of view
- **How to check**: what automated tests will verify and what still requires human review

If an existing rule or safeguard must remain for a reason that may not be obvious, record the reason and its reference. For a small change, putting only the goal and check in the Issue or request is enough. There is no need to turn every task into a long design document.

## Separate automated checks from human review

If the same input/output or package check is repeated, a reliable condition can become an automated test. For example, "the extracted package contains the required files and the specified command runs" is suitable for automation. This saves requesters and implementers from looking up and repeating the same procedure each time.

Keep usability and design judgments for human review when a machine cannot assess their meaning. Do not add checks just to increase their number; automate conditions that clearly reduce repeated work or protect a user-facing contract.

## How this differs from choosing validation

[Validation Routing](validation-routing.md) decides which checks to run after a change. This method comes first: decide the goal, constraints, boundaries, and completion criteria before implementation. Then use validation to check the criteria that can be automated.

## When to use it

This is useful when work will be handed to someone else, when changing user-facing behavior or compatibility, or when the scope and completion criteria can easily become unclear. For an obvious one-line fix, a separate design note is unnecessary; record the goal and test in the Issue.

No special tool is needed. Include the note in the request, or put it in an Issue or short work note and tell the AI where to find it.

## Example request to the AI

> Before implementation, read the goal, scope, constraints, and completion criteria below. For each criterion, name the code and check needed. Raise unclear or conflicting criteria before coding. At completion, report the result for each criterion.

## Optional tools and terminology

No dedicated tool is needed; record the note in the request, an Issue, or a [Context Pack](context-pack.md). Agreeing on goals and acceptance criteria first is called **Acceptance Criteria** or design-first planning.
