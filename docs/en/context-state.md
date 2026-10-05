# Keep a Short Summary of the Current State

> Japanese Source of Truth: [現在の状態を短くまとめる](../jp/現在の状態を短くまとめる.md)

Keep a short document describing what the project can do now, its known limits, and what it does not support yet. This lets someone understand the current assumptions without rereading the README or old Issues for every task. The summary should not copy detailed specifications or the requirements of the current task.

## Example: current CSV import support

For example, the summary might say:

> CSV import supports UTF-8. Dates do not use time zones. Excel files are not supported. See `docs/csv-format.md` for date formats.

When asked to add Excel support, an AI can use this summary to understand the current scope and then check the relevant feature and new requirements. It does not have to start by rereading old discussions about CSV and dates. The summary is only an entry point: for implementation details or exact date rules, check the linked guide, code, and tests.

## What to include

Keep only facts that provide useful context across recurring tasks:

- major features currently available
- current limitations
- known unsupported items
- links to sources for details

There is no need to list every feature or every open Issue. Details that do not help with a decision make the summary itself a recurring reading burden.

## Keep the summary current

If the summary conflicts with the implementation or tests, do not treat it as current fact; check the discrepancy. When a change affects the summary, update the relevant statement and its reference. Mark unverified information as unverified instead of presenting it as established.

The summary does not replace detailed specifications, change history, priorities, or task-specific completion criteria. Consult their original documents or Issues when the task requires them.
