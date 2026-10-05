# Choose Checks That Match the Change

> Japanese source of truth: [変更内容に応じて検証を選ぶ](../jp/変更内容に応じて検証を選ぶ.md)

To decide whether a change works, use a check that can verify the property you care about. A test can check a calculation, for example, but passing tests alone cannot show that a screen is laid out correctly. Decide what must be verified, then avoid spending time on unrelated checks and logs.

## Examples: CSV import, a screen, and a distribution

For a CSV date-conversion change, use a test with an input and expected date to verify the result. For a button-position change, launch the screen and inspect its placement. For a distribution change, a successful build of development code is not enough; check that the resulting package contains required files and launches.

| Change | What to verify | Suitable check |
| --- | --- | --- |
| Date conversion | The input produces the correct date | Regression test for conversion |
| Screen layout | The button appears in the right place | Launch and inspect the screen |
| Distribution settings | The deliverable contains required files and launches | Build and launch the deliverable |
| Performance | Processing time or throughput improves under equivalent conditions | Measure before and after with the same input and settings |

The first example does not require screen checks or performance measurements. Do not run the same large set of checks for every change. Start with a check that directly verifies the result promised by the task. Choosing relevant checks also reduces the amount of unrelated output and logs to inspect.

## Choose checks

1. Read the completion criteria and state what must be true when the work is done.
2. Select tests, a build, runtime checks, visual inspection, measurements, or another method that can directly verify that property.
3. Confirm that the result actually covers the changed code and relevant conditions.
4. Add checks when impact reaches shared features or deliverables, or when the first result cannot establish correctness.

A successful syntax check does not show that dates are converted correctly. A passing automated screen test may not verify the visual placement required by Acceptance. Do not treat a result as proof of a property it did not check.

## Check what the result covers

A successful exit code is not completion evidence if the check did not cover the target. Confirm that the changed code was included and that the check used the necessary input and conditions.

- Zero tests do not verify the feature.
- A successful run with the wrong target selection does not check the change.
- A successful build does not prove the distribution contains required files.
- If visual confirmation is required, do not infer appearance from test results.

Run checks that create files in a temporary directory when practical. This keeps generated data out of the working tree and makes it easier to retry from the same starting state. If the generated distribution itself is required to verify completion, inspect it temporarily as a check target. Afterward, do not keep full logs or generated artifacts in the normal task notes.

## When results depend on the environment

If results vary with randomness, time, or settings, fix the input, configuration, random seed, timestep, or other conditions when practical. This makes the check repeatable and avoids comparing large amounts of output from different runs.

When investigating runtime behavior, record only the state, events, or decisions that answer the current question, preferably in a short structured log. Keep a summary for successful checks and add only the relevant output when something fails.

## How much to run

See [Choose Validation Scope from the Change's Impact](change-impact-routing.md) for selecting tests from the changed code. For shared components, public formats, multiple consumers, or uncertain impact, expand to the related feature's wider checks. Report any required checks that could not be run.

Logic or saved formats that can be checked without launching a GUI can be tested first. When appearance or interaction is part of completion, inspect the screen too. When the deliverable differs from source, launch the actual package when needed.

## Record the result

Briefly record what was checked, the result, and anything left unverified. Full success logs are unnecessary.

```text
Checks:
- Date conversion tests: 12 passed
- CSV import tests: 8 passed
- Screen appearance: not applicable
- Unverified: none
```

## When this helps—and when it does not

This approach helps when every change triggers the same large test run, test results alone cannot verify completion, or checks must cover a screen or packaged deliverable rather than only source code. It selects checks from the change and its completion criteria.

For a small change with obvious target tests, those tests plus the project's normal completion checks may be sufficient. There is no need to perform every listed kind of check mechanically. Do not skip a check needed to establish correctness merely to reduce time or logs.

## Related guides

- What syntax checks can and cannot establish: [Use Syntax Checks as a Lightweight Validation](syntax-health-validation.md)
- How to keep generated files and temporary data out of routine investigation: [Decide What Not to Read](context-exclusion.md)
