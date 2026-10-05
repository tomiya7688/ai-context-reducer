# Full Bundle Distribution Design

> Japanese Source of Truth: [Full Bundleの配布構成](../jp/Full%20Bundleの配布構成.md)

This document explains how the normal bundle differs from the Full Bundle and what the Full Bundle contains. It defines the included files and runtime boundaries so users do not have to assemble the required environment themselves when obtaining or updating the distribution.

## Example: use the CLI or the graphical interface

The lightweight normal bundle is enough for someone who uses `acr-toolbox` from a command line. The Full Bundle is for someone who also wants the GUI Hub, language-specific helper tools, and templates in the same download. It preserves the normal bundle's functions and adds the other files to the same distribution.

The tools in the Full Bundle do not all run automatically. The GUI inspects basic project information and suggests available functions. Long-running analysis and actions that write files run only after the user chooses to start them. This prevents opening the bundle from immediately starting expensive work or changing the environment.

## Difference from the normal bundle

| Distribution | Main contents | Suitable use |
|---|---|---|
| Normal bundle | `acr-toolbox` and common helper CLIs | Use needed functions from the command line |
| Full Bundle | The same normal CLI, plus the GUI Hub, language tools, Python implementations as alternatives, setup scripts, profiles, templates, and user documentation | Use the GUI or several helper functions from one package |

The Full Bundle root keeps these CLI files and documents under the same names as the normal bundle. Commands and machine-readable output that worked in the normal bundle work the same way in the Full Bundle.

```text
acr-toolbox(.exe)
go-symbols(.exe)
go-import-map(.exe)
go-package-graph(.exe)
affected-tests(.exe)
README.md
TOOLS_README.md
LICENSE
RELEASE_MANIFEST.json
```

The [`FULL_BUNDLE_MANIFEST.json`](../../release/FULL_BUNDLE_MANIFEST.json) tracks the Full-Bundle-only contents. Keeping the GUI and alternative implementations out of the normal bundle's inventory avoids adding requirements for people who use only the normal bundle.

## What the Full Bundle contains

- **Built CLI tools:** Each supported operating system receives executable files. Users do not need a Go development environment or have to build from source.
- **GUI Hub:** Calls existing CLI commands and presents their results. It does not have a separate GUI-only analysis implementation; the CLI output and behavior remain the common source.
- **Python implementations as alternatives:** Included for explicit use, such as when a native tool cannot be used. Normal GUI and CLI use does not require Python. Only running an alternative implementation uses Python already present in the environment.
- **Setup and analysis scripts:** `setup.sh` / `setup.bat` and `analyze.sh` / `analyze.bat` live at the root. They prefer the included CLI and do not duplicate the analysis logic.
- **Profiles and templates:** Optional material for project types and templates for AI entry guides. Profiles are not required.
- **User documentation:** Japanese source documents live in `docs/jp/` and English translations in `docs/en/`. Internal release records and test files are not included.

The package uses this layout:

```text
ai-context-reducer-full-v1.1.0-<platform>/
├─ acr-toolbox(.exe) and common CLIs
├─ README.md / TOOLS_README.md / LICENSE
├─ RELEASE_MANIFEST.json
├─ FULL_BUNDLE_MANIFEST.json
├─ setup.sh / setup.bat / analyze.sh / analyze.bat
├─ gui/acr-hub(.exe)
├─ fallback/python/
│  ├─ common/
│  └─ languages/ (python / c / cpp / csharp / gdscript)
├─ profiles/
├─ templates/
└─ docs/ (jp / en)
```

## Additional installation and automatic execution

The Full Bundle does not automatically install Go, Python, .NET, C/C++ development tools, or external tools. It may use an external analyzer that is already available. If none is available, it returns to an included CLI or another available option.

Included functions are used in stages:

```text
inspect basic project information
  -> show available functions
  -> user chooses what to run
```

Opening the GUI does not start long-running analysis, use an external SDK or compiler, or write files. The GUI's Analyze action does not run every tool at once.

## Compatibility and distribution checks

Adding the Full Bundle preserves the normal CLI names, subcommands, arguments, exit codes, and machine-readable output. The normal bundle remains a separate distribution, and helper files found only in the Full Bundle are not required by it.

The distribution file list is expanded from the manifest and compared with the completed archive. This verifies that the delivered files match the declared package. Execution checks for each operating system are described in [Releasing](releasing.md).
