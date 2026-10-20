# Check a change in a way that matches what changed
> Japanese version: [変更に合った方法で動作を確かめる](../../jp/手法/変更に合った方法で動作を確かめる.md)


Fixing date handling, changing a screen, and rebuilding a package require different checks. Do not use the same test for every change. Choose checks that can show whether this change works.

## Choose checks based on the change

| What changed | What to check first |
| --- | --- |
| A calculation or data processing rule | Run tests for the changed behavior |
| Behavior affected by time or randomness | Fix the input and time conditions before running it |
| Screen layout or appearance | Run automated checks and, when needed, open the screen |
| Data format | Read and write representative data, including older data if relevant |
| App package for distribution | Confirm the built app starts and includes required files |
| Processing speed | Compare before and after with the same input and environment |

For example, changing a screen color may not require every date-processing test. But changing a distributed app and checking only its source tests does not show whether the package starts after release.

## Check what the tests actually covered

A test or check that reports “success” is not useful evidence if it did not examine this change.

- If zero tests ran, the feature was not checked.
- Do not count a result from unrelated folders as success.
- A successful build does not prove that the package contains every required file.
- If appearance matters, do not mark the work complete without checking the screen.

Briefly record what was checked and how much of it ran. You do not need to keep every line of a long success log. If a check fails, inspect only the output needed to understand the cause.

## Start with a quick check and expand when needed

If a quick check for obvious code-writing mistakes is available, run it before tests or a build. This can find simple mistakes early. But correct syntax does not prove that the behavior or requirements are correct. See [Start by checking code syntax](syntax-health-validation.md).

Expand checks when a change affects several features, changes a promise used by other programs, or has an unclear impact. When there are many tests and it is hard to choose, see [Decide which tests to run based on change impact](change-impact-routing.md).

When results depend on time, randomness, or environment settings, fix the inputs, settings, random seed, and time step where you can. You can then rerun under the same conditions and avoid comparing large amounts of output that differ from run to run. To find the cause of a behavior, record only the values that answer the current question, such as state, events, and decisions, in a short structured log. On success, keep a summary of what was checked; add detail only for a failure.

Report what was checked, the result, and what was not checked, briefly:

```text
Checked:
- Date conversion tests: 12 passed
- Screen display: not applicable
- Not checked: none
```

If the change is small and the target test is clear, that test plus the checks the project requires at completion may be enough. Do not skip a check that is needed to confirm correctness just to save time or log volume.

## Keep temporary check files separate

When you or the AI saves, converts, or exports files for a check, use a temporary folder. This keeps check output out of the normal change list and prevents it from being mistaken for source material on the next task.

## Tell the AI what to do

```text
Choose checks that match the kind of change and run them.
Report what was checked and how many checks ran.
Broaden the checks for shared code or unclear impact. Mark anything you could not run as unverified.
Keep files created only for checking in a temporary folder.
```

## Why this reduces context

Give the AI results related to the change instead of logs from every possible check. For screen changes or packaged files, ask it to inspect the actual screen or files when that is needed to confirm the result.

## Optional helper tool

- [validation-plan](../../../tools/common/medium/validation-plan/README.md) suggests the first checks to run from the changed files. Choose among the suggestions using the project's test procedure and completion conditions.

## Terms

- **Test**: A repeatable way to run a program with chosen inputs and check whether it returns the expected result.
- **Syntax check**: A check for obvious mistakes in how program code is written. It does not tell you whether the behavior is correct.
- **Distribution package**: The program and required files collected for delivery to its users.
- **Validation Routing / targeted validation**: Choosing checks that fit the property you need to confirm for the change.
