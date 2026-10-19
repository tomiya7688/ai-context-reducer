# Decide which tests to run based on change impact

> Japanese version: [変更の影響から実行するテストを決める](../../jp/手法/変更の影響から実行するテストを決める.md)


Start with tests related to the code you changed. Broaden the checks when the change can affect more of the project. A test is a repeatable check that runs a program with chosen inputs and compares the result with what is expected.

## Decide which tests to run first

Start with an existing map between code and tests, or use the project's existing dependency information.

| Changed area | Tests to run first | When to broaden the checks |
| --- | --- | --- |
| `src/date/` | `tests/date/` | Shared date handling or saved data format also changed |
| `src/settings/` | `tests/settings/` | Other screens or saving behavior may be affected |
| Packaging settings | Build and launch the packaged app | Multiple platforms or ways of using the app may be affected |

If there is no map, search for code that uses the changed function and for related tests. If those callers and tests cannot cover the change, run tests for the related folder.

## Tell the AI what to do

```text
Check the files I changed and find where that code is used.
Run the tests that match the changed code first. Report the tests and how many ran.
Broaden the checks when I changed shared code, a promise used by other programs, a saved-data format, or packaging; also broaden them when you cannot identify all affected areas.
Explain why you chose this test range and what remains unchecked.
```

## When to broaden the checks

If the change stays within one screen and clearly matches tests for that screen, start with those tests. If shared date handling or the saved-data format changed, include tests for the other features that use them.

Broaden the checks when:

- You changed code used by several features.
- You changed how other programs call this code, the data format, or the messages sent between programs.
- You cannot tell which tests cover the changed code.
- The test map or code-dependency information is old or incomplete.

When a test fails, first inspect that test and the code it exercises. Add related checks when the failure or the change reveals more affected areas. A passing small test set does not replace wider checks when one of the conditions above applies.

## Why this reduces context

Instead of running every test and giving the AI a large log, begin with checks related to the change. Keep the test range, number of checks, and failures; there is usually no need to retain every passing line. If the change affects more areas, expand the checks. This reduces irrelevant output without hiding uncertainty.

## When to add a test map or tool

A map is useful when the test suite is large or slow, or when the AI repeatedly receives long logs. For a small project where all tests finish quickly and the right tests are obvious, just run all tests. A map or dedicated tool would add upkeep without saving much work.

## Optional helper tools

- If useful, `affected-tests` lists tests that may relate to changed files. Use it to find tests to run first. Have the AI broaden the checks if the list does not cover the change.
- If useful, `source-structure-index affected` uses recorded code relationships to show areas that may be affected. Use it to check whether a change may reach other code.

Neither tool can guarantee that an incomplete map has no omissions. Broaden checks when the change may have wide effects or the map is uncertain. Reuse an existing project tool for finding dependent code if one is available.
