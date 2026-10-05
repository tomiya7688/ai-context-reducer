# Verify and Publish a Release

> Japanese Source of Truth: [リリースを確認して公開する](../jp/リリースを確認して公開する.md)

A release is the set of files that users download and run. Passing source tests alone does not prove that the package contains everything users need or works after extraction. Verify the code, the packages for each environment, and the compressed archives before publishing.

## Steps before publishing

For example, to distribute `v1.0.1`, first check the version and required files in [`RELEASE_MANIFEST.json`](../../release/RELEASE_MANIFEST.json). The current normal bundle contains five executables, a README, a tool guide, a license, and the manifest. Use that manifest as the source of truth for filenames and supported environments.

Next, run the release checks. Source validation checks repository consistency and the syntax of validation scripts, checks Python tool syntax and tests, and runs static analysis and tests for all Go tools. This catches basic source problems before packages are built.

Then build packages for x64 and arm64 on Windows, Linux, and macOS. Run the main commands against a sample project and check their results. On Windows, also check that the launcher script returns the correct exit status. The GUI Hub is started separately and checked for a local connection and response. That confirms startup and response only; it does not exercise every GUI action.

After making a zip or tar.gz for each environment, extract it again. Check the extracted file layout, required files, and executable permissions, then run the same main checks again. This tests the actual archive users receive, rather than only the working folder. Finally, confirm that there is exactly one archive for each of the six environments and generate `SHA256SUMS`, which lists a checksum for each archive.

## What the results establish

Passing all these checks means the current automated process has verified the source checks, normal packages for the six environments, and the tested behavior after extraction. Producing a candidate package does not publish a release. A change on `main` starts candidate checks only when its files match the paths in [`release.yml`](../../.github/workflows/release.yml). A change outside those paths, such as a release-document-only change, does not start them.

The GUI Hub check is a limited startup check. It does not test every screen and action or a complete Full Bundle archive resolved from its manifest. The current workflow does not create a Full Bundle archive for publication; it checks startup using the normal bundle and GUI Hub. Do not infer unperformed checks from a successful run.

## Publish

After candidate checks pass, a person reviews the package contents and known bugs, then creates and pushes a release tag. The automated checks run again on the exact commit named by that tag. GitHub publishes the verified files as a Release only after all required checks pass. Publishing through a manual workflow run also requires the matching tag to exist and publishing to be explicitly selected.

See the [validation record](../../release/validation/v1.0.0.md) for checks actually completed for v1.0.0. For exact commands and checks, consult the [release workflow](../../.github/workflows/release.yml) and [acceptance checks](../../release/scripts/acceptance.sh).
