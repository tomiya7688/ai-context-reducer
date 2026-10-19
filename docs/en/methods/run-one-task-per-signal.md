# Have the AI advance one listed task per signal

> Japanese source: [課題一覧から一件ずつAIに進めさせる](../../jp/手法/課題一覧から一件ずつAIに進めさせる.md)

For repeated work such as documentation corrections, restating “choose a remaining task, fix it, check it, and report” becomes tedious. Provide the task list and procedure first, then use a short signal such as “next” to request one task at a time.

“Next” alone does not establish permission or scope. First decide which list to inspect, how to choose, how far one request should go, and when to stop.

## When to use it

- Use it for multiple corrections sharing the same checking and reporting procedure when you want to inspect results individually.
- For example, record missing explanations as tasks and request one remaining correction each time.
- For a small, one-time correction, directly specifying the target and completion criteria is simpler.
- If the goal or ordering is unclear, make investigation or a design decision a task first. Do not turn an undefined large request into “implement everything in order.”

## Steps to use the method

### 1. Keep tasks in one place

Use existing task management or create a list such as `docs/tasks/queue.md`. You do not need a duplicate list. Give each task a goal, change scope, completion criteria, checks, and prerequisites.

This fictional example illustrates a list. Priority 1 is highest.

| ID | Priority | Task | Prerequisites | State |
| --- | ---: | --- | --- | --- |
| T01 | 2 | Identify conditions reproducing a save failure | None | Not started |
| T02 | 1 | Fix the save failure | T01 | Not started |
| T03 | 3 | Repair a broken documentation link | None | Not started |

For example, save T01’s details in `docs/tasks/T01.md`. With Issues, put the same fields in the Issue body.

```markdown
# Identify conditions reproducing a save failure
- Goal: Determine which input and operations trigger the failure
- Targets: Reported reproduction and settings-save code
- Excluded: Format changes and behavior fixes
- Completion: Record input, operations, expected and actual results for T02
- Checks: Try the reported procedure; record the result and environment
- Prerequisites: None
- References: Actual Issue, specification, and code paths
```

Size a task so its investigation or change can be checked independently. Bugs with separate outcomes can be separate tasks. A few lines requiring the same specification and checks need not become one task per line.

Record newly found, separate problems with goals and completion criteria. If creating Issues is outside the permitted scope, report a proposed Issue body. Do not silently add them to the current task.

### 2. Save the procedure invoked by “next”

For example, save the following in `docs/ai/next-task.md`. Adapt the list location, tie-breaking rule, permitted actions, and limits to your project.

```text
You advance this project’s tasks one at a time.
When I say “next,” perform this procedure once.

1. Inspect docs/tasks/queue.md, relevant recent changes, and work records.
2. If the previous task is unfinished or awaiting checks, resume that task.
   Report its result or why it cannot proceed, then end without selecting a new task.
3. Consider unfinished tasks whose prerequisites are satisfied and which nobody else is handling.
   Choose one by ascending priority number, then oldest registration for ties.
4. Briefly state its ID, goal, scope, completion criteria, and evidence for satisfied prerequisites.
5. Perform only that task and its specified checks.
6. Record results, evidence, unverified areas, and task state. Report and end.
   Wait for another signal before starting another task.

Permitted scope: Edit target files and perform checks specified by the task.
External writes, PR creation, merging, and similar actions follow permissions explicitly given earlier.
If necessary permission is missing, identify the action and reason before requesting it.
Do not repeatedly request existing permission or treat “next” as additional permission.

One task per request. Set a limit, for example two fix-and-check attempts for the same failure.
Stop earlier if no new evidence is available and report the situation.
When a specification decision is needed, evidence is missing, or changes exceed permitted scope,
stop dependent work and return confirmed facts and the question that needs answering.
If nothing is ready, report whether all work is complete or prerequisites/answers are pending.
```

“Two attempts” is an example setting, not a universal recommendation. Distinguish multiple necessary edits and checks within a task from endlessly retrying the same failure. Do not weaken a failing check to make work appear complete.

### 3. Tell the AI where the procedure is

Name the list and procedure in the initial request.

```text
When I say “next,” run docs/ai/next-task.md once.
The task list is docs/tasks/queue.md.
Read both and confirm the scope and procedure.
For this request, advance one task that is ready.
```

For recurring use, link from an entry instruction the AI reads: “For requests to advance a task with ‘next,’ read docs/ai/next-task.md.” Check whether the environment loads files such as `AGENTS.md` automatically; otherwise include the path in the request.

For a chat that cannot read files, attach or paste the procedure, current list, selected task details, and necessary sources. “Next” in a new chat does not necessarily carry over earlier conditions. You can also use the [chat-handoff procedure](../ai-usage/split-chats-by-task.md).

### 4. Have the AI verify which task is ready each time

In the example, T02 has the highest priority but requires T01’s result. If T01 and T03 are ready, choose T01 because its priority is higher. On a later request, T02 becomes eligible when T01 is complete and its reproduction record is available.

Check prerequisites against the specifications, code, and check results the task needs, as well as its written dependencies. A closed Issue might merely have been closed as a duplicate. Verify where the required outcome is and whether it is available in the revision being used.

Report tasks waiting on each other, inconsistent priorities, or unresolved specifications. Do not change priorities solely because a task has an earlier number or seems easier. Refresh the list and relevant changes on each request rather than reusing the previous candidate without checking.

### 5. Distinguish complete, awaiting checks, and stopped

Record results in, for example, `docs/tasks/T01-result.md` or the original Issue using this format. Writes to the record location also follow the agreed permissions.

```markdown
- Selected task and reason:
- Work performed and changed locations:
- Checked revision, commands/operations, results, and evidence locations:
- Result for each completion criterion:
- Unverified or unresolved:
- State: complete / awaiting checks / stopped
- Next decision or work needed:
```

Mark complete only when all required checks are finished. Waiting for CI—automated checks on shared infrastructure—or lacking the environment to verify a result means awaiting checks. If a specification choice is needed, stop and identify options and missing decision criteria. Keep the task list consistent with the report.

A PR is a proposal to integrate changes. Creating one does not itself satisfy completion criteria. If review and merging are required, carry them through under the necessary checks and existing permissions. Keep partial results explicitly partial.

Compare reports with diffs, original sources, and check results yourself, requesting corrections when needed. Record what enables resumption when something remains unverified. Stop when everything is complete; another signal should not invent nonexistent work.

## Example using Issues

The same procedure applies in this repository when missing methods become Issues and the user says “next.” An Issue is a task record containing its goal, completion criteria, and status.

1. Check for duplicates before registering missing work with its goal, targets, and completion criteria.
2. On “next,” inspect current Issues and PRs; choose one satisfying priorities and prerequisites.
3. Make the changes needed for that task, including its document, required translation, and navigation links.
4. Record verification and remaining work. Update the Issue state when its completion criteria are met.
5. After receiving the report, you send the next signal.

After choosing a task, use the [task-type starting-point guide](task-routing.md) to determine what to read first. This guide chooses the next task; the starting-point guide chooses where to begin reading for that task.

## How this differs from automatic repetition

The procedure above advances one task per human signal. Searches, edits, and checks within that task differ from starting further tasks without a signal.

To advance multiple tasks automatically, separately define the list, maximum task count, overall time or usage limit, failure handling, and conditions for returning control. For example: “Only these three tasks; stop if a specification decision is needed.” If time or usage cannot be measured, do not claim those limits were enforced; use observable limits such as task count.

A procedure document alone neither starts work on a schedule nor keeps it running after the conversation ends. Automatic initiation and a mechanism that checks stop conditions during execution are also needed.

## Why repeated explanation can decrease

Referencing an agreed procedure avoids rewriting long instructions each time. Recording each task’s goal, sources, and check results can let the next request begin with candidates and relevant details instead of rereading long conversations or every task body.

List checks and result records also add input. Conversation history accumulates in a long chat, and excessively small tasks increase management work. A short “next” request alone does not prove lower total AI usage. Use [usage records](../ai-usage/estimate-context-use-by-task.md) to compare history, checks, and retries while preserving required quality.

## Supporting tools and features

- **Task lists and filters:** Find candidates by state, priority, and prerequisites before opening every body. Verify prerequisite outcomes as well.
- **Saved, reusable instructions:** Reuse selection, checking, and reporting procedures. Supported environments can avoid repeatedly pasting procedure references.
- **Execution features with iteration limits:** Supported environments can end execution at specified counts or conditions. Check what is counted and how failures and interruptions are handled.

## About this workflow

A list of remaining work is a **backlog**. A requirement to wait for another task is a **dependency**. This workflow selects one ready task using priority and dependencies, then records its result.

An AI repeatedly receiving results and choosing and performing its next operation is an **agent work loop**. The [ReAct paper](https://arxiv.org/abs/2210.03629v3) combines reasoning and actions, using external results to inform subsequent decisions. [1] It neither proposes nor validates this guide’s Issue workflow or “next” signal. Its numerical results are not evidence of context reduction here.

## References

1. Shunyu Yao et al. (2023). [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629v3). ICLR 2023, arXiv:2210.03629v3, Section 2.
