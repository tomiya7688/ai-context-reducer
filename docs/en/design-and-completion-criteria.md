# Set Design and Completion Criteria First

> Japanese Source of Truth: [設計と完了条件を先に決める](../jp/設計と完了条件を先に決める.md)

Before implementation, briefly record what will change, how far the change may go, and what will count as complete. The next person can then continue without rereading past conversations or broad areas of code to infer the design intent.

## Example: changing the CSV date format

Suppose you need to change the date format in CSV output. Before implementation, record: "Change the output format only; do not change the input format or public command. The target is the date-output code and its tests. Check expected results using examples of the old and new formats." If the change may affect existing users, include that compatibility check as well.

The implementer can start with the date-output code and its tests. They do not need to explore screens, input handling, or old discussions to guess the scope and completion criteria. If implementation reveals facts that conflict with the note, update it before continuing.

## What to record

Keep only decisions relevant to the task:

- **Goal**: whose problem the change solves
- **Design and boundaries**: which behavior will change and which will stay as it is
- **Conditions to preserve**: command usage, output format, file locations, or compatibility with existing users
- **Completion criteria**: what must work from the user's point of view
- **How to check**: what automated tests will verify and what still requires human review

If an existing rule or safeguard must remain for a reason that may not be obvious, record the reason and its reference. For a small change, putting only the goal and check in the Issue or pull request is enough. There is no need to turn every task into a long design document.

## Separate automated checks from human review

If the same input/output or package check is repeated, a reliable condition can become an automated test. For example, "the extracted package contains the required files and the specified command runs" is suitable for automation. This saves implementers from looking up and repeating the same procedure each time.

Keep usability and design judgments for human review when a machine cannot assess their meaning. Do not add checks just to increase their number; automate conditions that clearly reduce repeated work or protect a user-facing contract.

## How this differs from choosing validation

[Validation Routing](validation-routing.md) decides which checks to run after a change. This method comes first: decide the goal, constraints, boundaries, and completion criteria before implementation. Then use validation to check the criteria that can be automated.

## When to use it

This is useful when work will be handed to someone else, when changing user-facing behavior or compatibility, or when the scope and completion criteria can easily become unclear. For an obvious one-line fix, a separate design note is unnecessary; record the goal and test in the Issue.

No special tool is needed. Put the note somewhere the next implementer can find it, such as an Issue, pull request, or short work note.
