# Choose Validation Scope from the Change's Impact

> Japanese source of truth: [変更の影響範囲から検証対象を絞る](../jp/変更の影響から検証範囲を選ぶ.md)

Use the changed code and the places that depend on it to choose which tests to run first. This avoids having to inspect every unrelated test for every change. Narrowing the scope is not a reason to skip necessary checks: expand to broader tests when a change has wide impact or its impact cannot be established.

## Example: Fixing CSV date parsing

Suppose you change `src/csv/date_parser.py`, which converts date strings from CSV. Running only the parser's test could miss a problem when it is used by the CSV importer. If the changed file and its existing test mapping are clear, start with:

```text
Changed:       src/csv/date_parser.py
Run first:     tests/csv/test_date_parser.py
Also check:    tests/csv/test_importer.py
```

If the change also affects the shared CSV format or a public API, add tests for its consumers and compatibility. If you cannot tell which features use the parser or cannot trace its dependencies completely, expand to the CSV feature's broader test suite. Passing a small test does not prove that wider effects were checked.

## Find candidate tests

Start by finding how the changed file or feature maps to tests. Use an existing guide, directory structure, or test naming convention when the relationship is clear. If the project already has a way to show code or package dependencies, add tests for the changed code's consumers and the features that use those consumers.

Existing test coverage data can help identify which tests previously executed changed lines. It does not prove that unexecuted paths or indirect effects are unaffected. Do not use coverage as the sole basis for choosing tests.

Check an existing map or dependency information against authoritative documentation and current code if it may be stale or incomplete. Search or inspect the code to find missing tests. If the relationship remains uncertain, expand the test scope rather than concluding that there is no impact.

## How far to expand

| Change | Additional checks |
| --- | --- |
| Implementation inside one feature | Regression tests for that feature and direct consumers |
| Shared library or component used by several features | Related tests including consumers; expand to the whole feature when needed |
| Public API, settings format, or data format | Tests for producers and consumers, plus compatibility checks |
| Build, dependencies, or distribution settings | Check the built distribution in addition to tests |
| Dependencies or test mappings are unknown | The related feature's full tests or an even broader suite |

For public contracts, shared components, or widely used authentication and storage code, include the tests for their users. Do the same when code generation or runtime loading makes it impossible to trace all affected locations statically. If broader checks cannot be run, state what remains unverified in the completion report.

Describe confidence in plain terms: “a test is mapped directly to the changed file,” “consumers were inferred from dependencies,” or “dynamic behavior makes the impact unclear.” A numeric score is unnecessary. In the last case, run broader tests or say what remains unverified.

## When a test fails

After a selected test fails, inspect the failure and the change, then expand to directly related consumer tests, feature-wide tests, and the full suite as needed. Do not ignore a failure unless you have established that it is unrelated.

A passing initial test is not enough when the change affects shared code, a public contract, or a distribution, or when the impact is unclear. A local change with an explicit target and test mapping does not need a full-suite run by habit. In either case, check that the tests actually cover the change.

## Record the result

Record the checked scope and outcome briefly. A short reason for adding or omitting broader tests is more useful than a large log.

```text
Validation:
- Targeted: date parser and CSV importer tests (18 passed)
- Broader: CSV feature tests (42 passed; shared format changed)
- Unverified: none
```

Choosing tests is separate from choosing the type of validation. For checks beyond tests, such as a visual check or a built distribution, see [Choose Validation by Change Type](validation-routing.md).

## When this helps

This approach helps when test suites are large or slow, the repository contains multiple applications or packages, or every small change triggers an investigation of the whole test suite. Following a change to its relevant tests also reduces the unrelated results and logs that need to be read.

For a small project where all tests finish quickly, running them all is simpler than maintaining a test map or impact-analysis system. Update a map when code or tests move.

For optional helpers to automate this approach, see the [method-to-tool map](tool-method-map.md). Tools are not required; you can use dependency or build information already available in the project, or search manually. Whichever method you use, check candidates against current code and tests, and expand the scope when the impact is uncertain.

## Example request to the AI

> Find direct consumers and test candidates from the changed files. First report paths, reasons, and confidence. Run the candidate tests, and broaden the scope if a check fails or a dependency cannot be traced. Report results and anything not verified.

## Optional tools and terminology

Use [affected-tests for Python](../../tools/python/medium/affected-tests/README.md), [affected-tests for Go](../../tools/go/medium/affected-tests/README.md), or [source-structure-index](../../tools/common/large/source-structure-index/README.md) to find candidates if helpful. This method is called **Change Impact Routing** or affected test selection.
