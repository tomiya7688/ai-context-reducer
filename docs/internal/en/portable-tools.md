# Portable Tools / Runtime Selection

> Japanese version: [追加インストールを減らすツール運用](../jp/追加インストールを減らすツール運用.md)

Do not require users to install Python or another environment just to run a helper tool. For example, on Windows, run the distributed `acr-toolbox.exe analyze .` command to inspect a repository without Python. The AI should first use an executable or environment already available, and look for another method only when it lacks a needed feature. This reduces the time spent installing and configuring an environment or troubleshooting errors, as well as the setup instructions and logs that must be sent to the AI. That leaves more time and context for the actual investigation or change.

## Basic policy

Preferred implementation order:

```text
prebuilt native binary
  -> available Python implementation
  -> available shell / batch wrapper
  -> external optional tool
```

However, when a high-quality external tool such as `rg` or `ast-grep` is already available, it may be preferred over a built-in implementation for the same purpose.

## Distribution unit

Frequently used Common tools should provide the following where practical:

```text
tool/
├─ script/       # Python reference implementation
├─ native/       # Go/C++ source
├─ bin/          # optional local build output; normally gitignored
├─ run.sh
└─ run.bat
```

Do not commit large numbers of binaries directly to source control. Prefer generating them through GitHub Actions / Release artifacts.

The current `Build portable tools` workflow produces the following together in each platform bundle:

```text
acr-toolbox
affected-tests
go-symbols
go-import-map
go-package-graph
```

Targets are Windows / Linux / macOS × amd64 / arm64. Before artifacts are produced, all five Go modules run `go test ./...` on both Ubuntu and Windows.

## Native implementation

Go is the first choice.

Reasons:

- easy cross compilation
- easy single-binary distribution
- one codebase can target Windows / Linux / macOS
- well suited to file walking / text processing / JSON CLIs

Use C / C++ when they are a better fit, such as for parsers or reuse of existing libraries.

## Python implementation

Python implementations serve as:

- reference implementations of behavior
- easy-to-modify fallbacks
- implementations whose logic an AI can inspect and change easily

When Python is unavailable, use the native binary.

## Shell wrappers

When a `.bat` wrapper exists, provide an equivalent `.sh` where practical.

Wrappers should only:

- select the binary for the current OS
- fall back to Python when no binary is available
- pass arguments through

Do not implement large amounts of core logic inside wrappers.

## Environment-aware adoption

Do not copy every implementation into the target repository.

```text
environment probe
  -> OS / architecture / Python / Git / optional tools
  -> choose usable implementation
  -> selected tools only
  -> unused variants are not materialized
```

When cleaning up an already materialized tool set, limit deletion to the relevant tool directory and make dry-run the default.

## Safe materialization

Treat portable-tool materialization as a **previewable deterministic plan**, not as a simple copy script.

```text
selection
  -> preview
  -> create / unchanged / conflict / overwrite
  -> explicit apply
  -> provenance manifest
```

Do not modify files by default. If an existing destination differs, stop with a conflict and replace it only when `--overwrite` is explicit.

Implementations:

```text
Python: tools/common/small/materialize-tools/script/materialize_tools.py
Native: acr-toolbox materialize
```

The native implementation can materialize the running `acr-toolbox` binary itself and an OS-specific wrapper even when Python is unavailable.

Keep the wrapper-relative layout contract as the Source of Truth.

```text
portable-tools/
├─ analyze.sh or analyze.bat
└─ bin/
   └─ acr-toolbox(.exe)
```

After a successful apply, `.acr-materialized-tools.json` records each materialized file's path / role / source path / SHA-256 and, when available, the source Git revision. Do not include timestamps; prefer a manifest that remains stable for the same source and selection.

When replacing an existing file, including on Windows, do not truncate the destination first. Write to a temporary file, and on platforms where direct replace is unavailable, move the old destination to a temporary backup and restore it if installation fails.

## Recommended native targets

High priority:

- text-search
- path-find
- tree-view
- repo-stats
- analyze-and-recommend

Medium priority:

- compact-log
- target-slice
- doc-index
- file-role-map
- context-budget

For language-specific parsers, keep Python / lightweight implementations first and add native implementations only after usage frequency and value justify them.

## Example request to the AI

```text
First check which languages the project uses and which analysis environments are already available.
If needed, run language-setup to find suitable options. Before placing a bundled helper, use materialize-tools to inspect the destination and selected files.
Do not automatically add a new development environment or tool just for this task.
```

## Helper tools

- If useful, `language-setup` checks the project's languages and available analysis environments. Use it to see which analysis environment is already available.
- If useful, `materialize-tools` places bundled helpers in a specified location. Use it when you need a helper inside the project. Check the selected files and any overwrites before placing them.
