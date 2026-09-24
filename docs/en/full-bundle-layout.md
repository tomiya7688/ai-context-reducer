# Full Bundle Distribution Design

> Japanese Source of Truth: [Full Bundleの配布構成](../jp/Full%20Bundleの配布構成.md)

This document defines the distribution contract for the Full Bundle added in v1.1.0.

The Full Bundle does not replace the normal bundle. The normal bundle remains a lightweight CLI distribution. The Full Bundle is a superset that preserves the normal contents and adds the GUI Hub, Python fallbacks, language-specific tools, setup scripts, profiles, templates, and user-facing documentation.

The machine-readable Source of Truth for its contents is `release/FULL_BUNDLE_MANIFEST.json`.

## 1. Relationship with the normal bundle

`release/RELEASE_MANIFEST.json` remains the Source of Truth for the normal bundle.

The Full Bundle root keeps the same normal-bundle files with the same names:

~~~text
acr-toolbox(.exe)
go-symbols(.exe)
go-import-map(.exe)
go-package-graph(.exe)
affected-tests(.exe)
README.md
TOOLS_README.md
LICENSE
RELEASE_MANIFEST.json
~~~

Therefore, CLI commands that work in the normal bundle work the same way from the Full Bundle. Windows executable files use the `.exe` suffix.

Full-Bundle-specific information lives in `FULL_BUNDLE_MANIFEST.json`; do not mix GUI/fallback inventory into the normal-bundle manifest.

## 2. Directory layout

The target v1.1.0 Full Bundle layout is:

~~~text
ai-context-reducer-full-v1.1.0-<platform>/
├─ acr-toolbox(.exe)
├─ go-symbols(.exe)
├─ go-import-map(.exe)
├─ go-package-graph(.exe)
├─ affected-tests(.exe)
├─ README.md
├─ TOOLS_README.md
├─ LICENSE
├─ RELEASE_MANIFEST.json
├─ FULL_BUNDLE_MANIFEST.json
├─ setup.sh
├─ setup.bat
├─ analyze.sh
├─ analyze.bat
├─ gui/
│  └─ acr-hub(.exe)
├─ fallback/
│  └─ python/
│     ├─ common/
│     └─ languages/
│        ├─ python/
│        ├─ c/
│        ├─ cpp/
│        ├─ csharp/
│        └─ gdscript/
├─ profiles/
├─ templates/
└─ docs/
   ├─ jp/
   └─ en/
~~~

Internal GUI asset layout may be decided by the GUI implementation, but the platform-specific entry point exposed to users is `gui/acr-hub(.exe)`, distributed without requiring an additional runtime.

## 3. Go tools

Go tools in the Full Bundle are distributed only as binaries built for the target platform:

- `acr-toolbox`
- `go-symbols`
- `go-import-map`
- `go-package-graph`
- `affected-tests`

Do not include `*.go`, `go.mod`, `go.sum`, build scripts, Go unit-test source, or the Go build cache.

Users must not be required to run `go build`. A release condition is that the CLI and GUI included for the platform can be used even when no Go toolchain is installed.

## 4. Python fallback

Python implementations are bundled as fallbacks / reference implementations.

~~~text
tools/common/...   -> fallback/python/common/...
tools/python/...   -> fallback/python/languages/python/...
tools/c/...        -> fallback/python/languages/c/...
tools/cpp/...      -> fallback/python/languages/cpp/...
tools/csharp/...   -> fallback/python/languages/csharp/...
tools/gdscript/... -> fallback/python/languages/gdscript/...
~~~

Include runtime-relevant `script/*.py`, compatibility entry points, and required configuration only. Do not distribute tests, caches, or development build files as fallback content.

Python must not be required for normal Full Bundle use. The GUI and native CLI work without Python. Only users who explicitly use a Python fallback rely on an already-installed Python runtime; the Full Bundle does not install Python or packages itself.

## 5. setup / analyze entry points

Place `setup.sh`, `setup.bat`, `analyze.sh`, and `analyze.bat` at the Full Bundle root. They prefer the prebuilt `acr-toolbox` included in the bundle.

Wrappers only resolve the native binary, pass arguments through, and optionally use a Python fallback when native execution is genuinely unavailable. They do not duplicate analysis logic.

## 6. GUI Hub

The GUI Hub is a frontend to existing CLI commands.

~~~text
GUI action
  -> existing CLI
  -> existing JSON contract
  -> GUI presentation
~~~

Do not add GUI-specific analysis logic to the Full Bundle contract. CLI standalone use, stdout / stderr / exit codes, and the existing JSON contract remain authoritative.

The GUI also does not automatically run Large / heavy analysis or install SDKs / runtimes / external tools. The backend lives in `tools/gui/acr-hub/backend` and directly invokes the existing CLI from the bundle root. It preserves stdout JSON and separately classifies only GUI execution state.

The screen and one-click analysis flow live in the same `tools/gui/acr-hub` module.

## 7. profiles / templates

`profiles/` contains optional input such as project-type or architecture-routing profiles. Profiles are not mandatory.

`templates/` contains canonical templates such as the AI entry point and Context Pack.

When a new profile or template becomes part of the distribution, update the Full Bundle manifest in the same change set.

## 8. Documentation

User-facing documentation is distributed under:

~~~text
docs/jp/
docs/en/
~~~

`docs/jp/` is the Japanese Source of Truth and `docs/en/` contains translations.

Do not unconditionally bundle internal release-validation records or test fixtures.

## 9. External runtimes / SDKs / tools

"Full Bundle" does not mean bundling every external dependency.

Do not automatically install the Go toolchain, Python runtime, dotnet SDK, C/C++ compiler, Godot, SCIP indexer, Universal Ctags, ast-grep, rg / fd / scc, or similar tools.

When an external backend already exists, it may be used for higher-precision analysis. Otherwise, return to a portable native path or an available fallback.

## 10. Automatic-execution boundary

Being included in the Full Bundle does not imply a tool may run automatically.

Only existing cheap / shallow paths may run automatically.

~~~text
project facts
  -> recommendation
  -> user selects Run
~~~

Medium / Large / heavy analysis, external compiler / SDK work, and operations that write files retain their existing safety boundaries. GUI Analyze is not a "run every tool" action.

## 11. Role of the manifest

`release/FULL_BUNDLE_MANIFEST.json` defines:

- supported platforms
- compatibility relationship with the normal bundle
- prebuilt native binaries
- GUI entry point
- setup wrappers
- Python fallback source -> bundle paths
- profiles / templates
- documentation trees
- excluded distribution content
- runtime / auto-install / heavy-execution policy

Tree inclusion rules are expanded during bundle construction, and release CI compares the final archive contents against the resolved manifest.

## 12. Compatibility rules

Adding the Full Bundle must not break the existing CLI.

- preserve the five root binary names
- preserve subcommands / arguments / exit codes
- preserve `tools/JSON_CONTRACT.md` for machine output
- do not make the Full-Bundle GUI the Source of Truth for CLI behavior
- continue distributing the normal bundle separately
- do not make Full-Bundle-only helper files mandatory for the normal bundle

If v1.1.0 requires a CLI contract change, handle it in an explicit separate Issue rather than as an incidental effect of the Full Bundle.
