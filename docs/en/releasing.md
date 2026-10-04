# Releasing v1.x

> Japanese Source of Truth: [リリース手順](../jp/リリース手順.md)

v1.0.0 is the first user distribution. v1.0.x patch releases are maintenance changes that preserve the public CLI / JSON contract / bundle contents and use the same completion gate.

## Release gate

The current Release gate is `.github/workflows/release.yml`. This workflow and `release/scripts/acceptance.sh` are the source of truth for what is actually checked.

### Source validation

On an Ubuntu runner, CI checks repository consistency and the acceptance script syntax, compiles and tests all Python tools, and runs `go vet`, `go test`, and `go test -race` for every Go module.

### Normal distribution validation

Each Windows x64 / arm64, Linux x64 / arm64, and macOS x64 / arm64 runner builds the binaries for the normal bundle and runs `release/scripts/acceptance.sh` against a fixture. The acceptance suite checks output from major commands, statuses and exit codes for cases such as policy violations, template drift, and confirmation required for Large execution, plus generated artifacts.

### Archive validation and re-extracted E2E

After creating each archive, CI extracts it, verifies its contents, and **runs the same full acceptance script again against the extracted archive**. It then verifies that all six archives exist and generates `SHA256SUMS`. The Release job runs only when every required job succeeds.

### Full Bundle smoke and remaining v1.1.0 gates

For each platform's E2E, CI also assembles a smoke Full Bundle from the normal distribution core and the GUI Hub binary, then checks startup on a loopback URL and the health API response. This is a startup-boundary smoke; it does not validate a complete archive resolved from the Full Bundle manifest or every GUI action.

The current workflow does not verify end-to-end inputs / outputs / side effects for every user-facing Python entrypoint and wrapper, or the absence of additional runtime requirements in a clean environment. For v1.1.0, these checks are expected to become part of the #32 completion gate. #33 covers expected inputs, outputs, exit codes, and generated artifacts across source / script execution, built binaries, and re-extracted archives. #34 checks that users do not need additional environment setup and that optional dependencies behave correctly when unavailable. These guarantees are not complete until their checks are implemented and CI is green.

## User distribution

`release/RELEASE_MANIFEST.json` is the Source of Truth for the current v1.0.x distribution.

Required contents:

- `acr-toolbox`
- `go-symbols`
- `go-import-map`
- `go-package-graph`
- `affected-tests`
- `README.md`
- `TOOLS_README.md`
- `LICENSE`
- `RELEASE_MANIFEST.json`

Windows executables use the `.exe` suffix.

## Platforms

```text
ai-context-reducer-v<version>-windows-x64.zip
ai-context-reducer-v<version>-windows-arm64.zip
ai-context-reducer-v<version>-linux-x64.tar.gz
ai-context-reducer-v<version>-linux-arm64.tar.gz
ai-context-reducer-v<version>-macos-x64.tar.gz
ai-context-reducer-v<version>-macos-arm64.tar.gz
SHA256SUMS
```

The current candidate version must match `release_version` in `release/RELEASE_MANIFEST.json`.

## Bundle variants

Starting with v1.1.0, the lightweight normal bundle and the GUI Hub Full Bundle are separate artifacts.

- normal bundle: `release/RELEASE_MANIFEST.json`
- Full Bundle: `release/FULL_BUNDLE_MANIFEST.json`
- Full Bundle layout / compatibility: [Full Bundle Distribution Layout](full-bundle-layout.md)

The Full Bundle is a superset that preserves the normal bundle root contents. It does not require users to install Go source or a Go toolchain.

## Candidate validation

When a push to `main` matches the workflow's path filters, it runs the same completion gates and produces the `v1-release-candidate` artifact. A push that changes only release documentation, for example, does not start this workflow if it does not match those filters. Candidate CI does not publish a Release.

A green candidate CI on `main` does not automatically create a tag or GitHub Release.

## Publishing

Publishing must always start from an explicit action.

```text
main candidate CI green
  -> final distribution / bug check
  -> a human creates and pushes the release tag
  -> rerun completion workflow on the tagged commit
  -> all jobs succeed
  -> create GitHub Release
```

Since `v1.0.0`, there is no automatic promotion from a `main` push or READY marker to a tag / Release.

Publishing through `workflow_dispatch` also requires a matching tag to exist in the repository.

## Post-release

New language support, additional external backends, and heuristic improvements after v1.0.0 are tracked as new Issues. Do not append new features to the completion conditions of a patch release.

## v1.0.0 validation record

See [release/validation/v1.0.0.md](../../release/validation/v1.0.0.md) for the final validation record of the published v1.0.0 release.
