# Language Tool Setup

> Japanese Source of Truth: [言語別ツールの選び方](../jp/言語別ツールの選び方.md)

Language-specific tools should prefer the standard environments already used by the target project and should not assume additional installation.

## Setup entry points

```text
Windows: tools/setup.bat <project-root>
Linux/macOS: tools/setup.sh <project-root>
```

The entry point prefers native `acr-toolbox` and falls back to Python when the native binary is unavailable. `setup.bat/.sh` also runs `language-setup` to narrow candidates based on the repository's actual languages, size, and available runtimes/compilers.

## Automatic detection

| Language | Existing environment signal | Tool policy |
|---|---|---|
| Python | `python3` / `python` | Python-specific tools available |
| C# | `dotnet` | csproj / project-map tools available |
| Go | `go` | package / import analysis available |
| C | `gcc` / `clang` / `cc` | include / compile-context analysis available |
| C++ | `g++` / `clang++` / `c++` | include / project analysis available |
| GDScript | `godot4` / `godot` | Godot scene/resource analysis available |

Small shallow-symbol analysis can use the fallback built into `acr-toolbox`, so it remains available without the language runtime/compiler. Medium/Large dependency, project, and graph analysis is proposed only when the existing runtime/compiler is available.

Setup must not invoke a package manager or automatically install a runtime or SDK.

## Selection principle

```text
languages used by the repository
  -> Small symbol analyzer: acr-toolbox native fallback
  -> is Medium/Large needed?
  -> yes: propose it only if the matching runtime/compiler already exists
  -> no: operate with Small + Common tools
```

The same applies to external tools. Reuse `rg` / `fd` / `ctags` / `ast-grep` when they already exist; otherwise use the bundled fallback.

## Combine with repository size

- Small: prioritize symbols / shallow structure only
- Medium: add import/include/project dependencies
- Large: add bounded graph / source structure index only when needed

Do not automatically introduce Large analysis into a Small repository merely because a language environment exists.

## Distribution policy

Common functionality is distributed as prebuilt `acr-toolbox` for Windows / Linux / macOS. The separately implemented Go tools `affected-tests` / `go-symbols` / `go-import-map` / `go-package-graph` are included in the same platform bundles.

For other language-specific analysis, prefer using runtimes/compilers that already exist rather than adding a mandatory SDK or parser dependency.

## language-setup

```text
acr-toolbox language-setup <project-root>
python tools/common/small/language-setup/script/language_setup.py <project-root>
```

The output contains `enabled_tools` / `skipped_languages` / `runtime_commands`. It chooses a Small / Medium / Large stage from repository size, but it does not unconditionally execute Medium/Large analysis during setup.

`--run-small` is a routing flag that explicitly proposes a low-cost Small analysis as the next action.

## language-run

After selection, `setup.bat/.sh` automatically runs only the Small analyzer.

```text
acr-toolbox language-run <project-root>
python tools/common/small/language-run/script/language_run.py --acr-root /path/to/ai-context-reducer <project-root>
```

By default, full analyzer JSON is stored under `<project-root>/.acr/language/`. Stdout contains only status / backend / output path / skip reason. Medium/Large tools do not run automatically.

The native `acr-toolbox` has built-in Small symbol fallbacks for Python / C# / Go / C / C++ / GDScript. These are approximate routing analyses, not complete parser replacements. Use existing SDK/compiler/parser backends only when Medium/Large precision is needed.

## Medium portable fallback

```text
acr-toolbox language-medium-run <project-root>
```

This extracts Python imports, C# ProjectReference, Go imports, C/C++ includes, and GDScript load/preload/extends using portable native fallbacks. Full output is stored under `<project-root>/.acr/language-medium/`, while stdout stays compact.

Medium results are approximate routing information. Proceed to existing SDK/compiler/parser backends only when type resolution, compile conditions, MSBuild evaluation, Godot runtime semantics, or similar precision is needed.

## Large high-precision routing

```text
acr-toolbox language-large-plan <project-root>
acr-toolbox language-large-run --allow-heavy <project-root>
```

`language-large-plan` does not run heavy analysis. It reports availability and recommended paths for existing SCIP indexes, Universal Ctags, dotnet, Go, C/C++ compilers, Godot, and similar backends.

`language-large-run` requires `--allow-heavy`. At present it imports an existing SCIP index or Universal Ctags data into Source Structure Index. If no high-precision backend is available, stop at the Medium fallback.
