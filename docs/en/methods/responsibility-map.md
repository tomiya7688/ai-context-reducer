# Find which files handle what
> Japanese version: [ファイルやフォルダーの担当を探す](../../jp/手法/ファイルやフォルダーの担当を探す.md)


File names do not always make it clear where each part of a project lives. Start by grouping the work into broad categories, then show the area responsible for each one. This is not a list of every file. Summarize only the main areas by category.

## Example: a reminder email arrives after an invoice was paid

Suppose you need to fix a bug where an invoice has been paid, but a payment reminder is still sent. The table below uses a fictional billing app.

| Work category | Main area | What it handles |
| --- | --- | --- |
| Invoices and payments | `src/invoices/` | Stores invoices and whether they have been paid |
| Reminders | `src/reminders/` | Selects unpaid invoices and prepares reminder emails |
| Sending email | `src/email/` | Sends emails |
| Behavior checks | `tests/reminders/` | Checks that paid invoices do not get reminder emails |

For this bug, tell the AI to start with `src/reminders/` under "Reminders" and `tests/reminders/` under "Behavior checks." They show the rule for preparing reminders and how that rule is checked. If the payment status itself looks wrong, direct it to "Invoices and payments." If the right email is prepared but never arrives, direct it to "Sending email."

This lets you choose where to look based on the problem. You do not need to open every file and guess what it handles.

## How to make a responsibility map

When preparing the map, choose broad work categories and list only the main folders or areas for each one. There is no need to list every file or small function. Update the map when an area's responsibility changes.

For a small project, a few lines in an existing guide may be enough; a separate map is not always needed. If the map no longer matches the code, check the code instead of relying on the map.

For a map used repeatedly, save it as `docs/file-ownership.md`, for example, and link it from the root `AGENTS.md`. In the request, tell the AI to start with the row that matches the problem and widen the search only if that row does not explain it. If a resource list or change-check map already records the same ownership, add to that document instead of creating another map.

## Tell the AI what to do

```text
Choose the area in the map that matches the problem. Start with its code and behavior checks.
If that area does not explain the cause, inspect related areas too.
If the map disagrees with the current code, correct the map after the work.
```

## Why this reduces context

Give the AI the area that handles the problem as its starting point instead of having it open files one by one to guess their purpose. Ask it to expand to another area only when the first one does not explain the behavior.

