package main

import (
    "flag"
    "fmt"
    "io"
    "os"
    "path/filepath"
    "runtime"
)

func cmdMaterialize(args []string) int {
    fs := flag.NewFlagSet("materialize", flag.ContinueOnError)
    fs.SetOutput(io.Discard)
    out := fs.String("out", "", "deployment directory")
    apply := fs.Bool("apply", false, "apply the plan; default is preview only")
    overwrite := fs.Bool("overwrite", false, "allow replacement of different destination files")
    if err := fs.Parse(args); err != nil {
        emitStructureJSON(map[string]any{"tool": "materialize-tools", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }

    source := "."
    if fs.NArg() > 0 {
        source = fs.Arg(0)
    }
    if *out == "" {
        emitStructureJSON(map[string]any{"tool": "materialize-tools", "status": "invalid_arguments", "error": "--out is required"})
        return 2
    }

    sourceAbs, err := filepath.Abs(source)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "materialize-tools", "status": "input_read_failed", "error": err.Error()})
        return 2
    }
    info, err := os.Stat(sourceAbs)
    if err != nil {
        status := "input_read_failed"
        if os.IsNotExist(err) {
            status = "input_missing"
        }
        emitStructureJSON(map[string]any{"tool": "materialize-tools", "status": status, "source_root": sourceAbs, "error": err.Error()})
        return 2
    }
    if !info.IsDir() {
        emitStructureJSON(map[string]any{"tool": "materialize-tools", "status": "input_not_directory", "source_root": sourceAbs})
        return 2
    }

    outAbs, err := filepath.Abs(*out)
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "materialize-tools", "status": "invalid_arguments", "error": err.Error()})
        return 2
    }
    executable, err := os.Executable()
    if err != nil {
        emitStructureJSON(map[string]any{"tool": "materialize-tools", "status": "implementation_unavailable", "error": err.Error()})
        return 2
    }
    executable, _ = filepath.EvalSymlinks(executable)

    selected := nativeMaterializeSelection(sourceAbs, executable, runtime.GOOS)
    actions, missing, err := planNativeMaterialization(outAbs, selected, *overwrite)
    revision := materializeSourceRevision(sourceAbs)
    base := map[string]any{
        "tool":                  "materialize-tools",
        "source_root":           sourceAbs,
        "output_root":           outAbs,
        "implementation_mode":   "native",
        "apply_requested":       *apply,
        "overwrite_requested":   *overwrite,
        "source_revision":       revision,
        "manifest_path":         filepath.Join(outAbs, materializeManifestName),
        "applied":               false,
        "actions":               actions,
        "missing_source_files":  missing,
    }

    if err != nil {
        base["status"] = "plan_failed"
        base["error"] = err.Error()
        emitStructureJSON(base)
        return 2
    }
    if len(missing) > 0 {
        base["status"] = "source_selection_incomplete"
        emitStructureJSON(base)
        return 2
    }

    conflicts := []string{}
    for _, action := range actions {
        if action.PlannedAction == "conflict" {
            conflicts = append(conflicts, action.DestinationPath)
        }
    }
    if len(conflicts) > 0 {
        base["status"] = "conflict"
        base["conflicting_destination_paths"] = conflicts
        emitStructureJSON(base)
        return 1
    }

    if !*apply {
        base["status"] = "ok"
        emitStructureJSON(base)
        return 0
    }

    sourceByDestination := map[string]string{}
    for _, row := range selected {
        sourceByDestination[row.Destination] = row.Source
    }
    for _, action := range actions {
        if action.PlannedAction != "create" && action.PlannedAction != "overwrite" {
            continue
        }
        destination := filepath.Join(outAbs, filepath.FromSlash(action.DestinationPath))
        if err := atomicNativeCopy(sourceByDestination[action.DestinationPath], destination); err != nil {
            base["status"] = "apply_failed"
            base["error"] = fmt.Sprintf("%s: %v", action.DestinationPath, err)
            emitStructureJSON(base)
            return 2
        }
    }

    manifest := nativeMaterializeManifest(revision, actions)
    if err := atomicNativeJSON(filepath.Join(outAbs, materializeManifestName), manifest); err != nil {
        base["status"] = "apply_failed"
        base["error"] = err.Error()
        emitStructureJSON(base)
        return 2
    }

    base["status"] = "ok"
    base["applied"] = true
    emitStructureJSON(base)
    return 0
}
