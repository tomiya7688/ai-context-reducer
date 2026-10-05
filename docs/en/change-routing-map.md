# Find References by Change Type

> Japanese source of truth: [変更内容ごとの案内表](../jp/変更内容ごとの案内表.md)

This guide is a table that connects each kind of change to the code to read first, the tests to run first, and any documentation to consult when needed. For example, when fixing settings that do not persist, use the table to find the likely screen, storage code, and tests instead of searching the whole repository each time. A clear starting point means less time reading unrelated features.

## Example: Settings revert after restart

For a report that “settings return to their old values after restart,” storage is a better place to start than the display code. A table might look like this:

| Change type | Read this code first | Run these tests first | Read these docs if needed |
| --- | --- | --- | --- |
| Save or load settings | `src/settings/storage.py` | `tests/settings/test_storage.py` | `docs/settings-format.md` |
| Display or operate a screen | `src/settings/view/` | `tests/settings/test_view.py` | `docs/settings-screen.md` |
| API response fields | `src/api/` and its consumers | API and consumer contract tests | `docs/api.md` |

For a settings persistence bug, start with the storage code and its tests. Read the format guide only if the change affects the settings format. For a display-only change, there is no need to begin with detailed storage or API documentation.

## Build the table

Use change types that match work people actually request. A broad row such as “API change” should say which API and consumers it covers. Each row should point to specific starting code and tests.

A simple table can start with three columns:

```text
Change type       Read this code first       Run these tests first
Save settings     src/settings/storage.py   tests/settings/test_storage.py
Display screen    src/settings/view/        tests/settings/test_view.py
```

Add documentation references only when they help make implementation decisions. Point to the document instead of copying its specification into the table.

## Use the table

1. Identify the behavior that the request asks to change.
2. Find the closest change type and check its starting code and tests.
3. If the change reaches beyond what the row describes, add direct consumers and related contract tests.
4. If no row fits, search normally and update the table once the right references are known.

The table is a starting point; it does not guarantee that the listed files are always sufficient. Expand the investigation and tests if code movement, a shared API, or a settings-format change reveals broader impact. If the current code disagrees with the table, check the code and tests, then correct the outdated row.

## Reuse the existing design

If the project already defines areas such as screens, storage, and communication, use those boundaries in the table. There is no need to rename or recreate existing design boundaries. Once responsibilities are clear, connect each change type to its likely starting code and tests.

Changes involving large data transformations or distribution packages may need additional procedures or checks. Explain those in their own guides instead of crowding every detail into this table.

## When it helps—and when it does not

This table helps when people repeatedly look up the same locations for settings or API changes, similar features exist in multiple apps, or the project is large enough that ownership is unclear. Once common references are mapped, future work can start from its change type.

For a small project where the changed file and its test are obvious, a table is unnecessary. Writing the references directly in the request is simpler than maintaining categories no one uses.

## Keep it current

Update the relevant row in the same change when code or tests move or responsibilities change. A stale row can send someone to the wrong place, erasing the time the guide was meant to save. Keep the table small enough to maintain.
