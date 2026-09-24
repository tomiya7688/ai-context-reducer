# Releasing v1.x

> Japanese Source of Truth: [リリース手順](../jp/リリース手順.md)

v1.0.0 is the first user distribution. v1.0.x patch releases are maintenance changes that preserve the public CLI / JSON contract / bundle contents and use the same completion gate.

## Release gate

Before creating a Release, every job in `.github/workflows/release.yml` must be green.

The completion CI verifies:

1. repository consistency / `git diff --check`
2. compile + tests for all Python tools
3. tests for all Go modules
4. native builds on Windows x64 / arm64, Linux x64 / arm64, and macOS x64 / arm64
5. E2E using the binaries that will actually be distributed on each platform
6. Small / Medium language fallbacks
7. policy success / violation exit codes
8. template generate / check / drift detection
9. scoped guide resolution
10. major search / find / routing / context / Git commands
11. actual execution of standalone Go tools
12. archive extraction and required-file verification
13. existence of all six archives
14. generation of `SHA256SUMS`

If any gate fails, the Release job does not run.

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

Release-related changes on `main` run the same completion workflow. In that case, the workflow does not publish a Release; it only produces the `v1-release-candidate` artifact.

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
