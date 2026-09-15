package main

import (
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"
    "flag"
    "fmt"
    "io"
    "os"
    "os/exec"
    "path/filepath"
    "runtime"
    "sort"
)

const materializeManifestFormat = "acr-materialized-tools-v1"
const materializeManifestName = ".acr-materialized-tools.json"

type materializeSelection struct {
    Source      string
    SourcePath  string
    Destination string
    Role        string
}

type materializeAction struct {
    SourcePath       string `json:"source_path"`
    DestinationPath  string `json:"destination_path"`
    Role             string `json:"role"`
    SourceSHA256     string `json:"source_sha256"`
    DestinationState string `json:"destination_state"`
    PlannedAction    string `json:"planned_action"`
}

type materializeManifestFile struct {
    Path       string `json:"path"`
    Role       string `json:"role"`
    SourcePath string `json:"source_path"`
    SHA256     string `json:"sha256"`
}

type materializeManifest struct {
    Format             string                    `json:"format"`
    ImplementationMode string                    `json:"implementation_mode"`
    SourceRevision     *string                   `json:"source_revision"`
    Files              []materializeManifestFile `json:"files"`
}

func materializeSHA256(path string) (string, error) {
    data, err := os.ReadFile(path)
    if err != nil { return "", err }
    sum := sha256.Sum256(data)
    return hex.EncodeToString(sum[:]), nil
}

func materializeSourceRevision(source string) *string {
    command := exec.Command("git", "-C", source, "rev-parse", "HEAD")
    output, err := command.Output()
    if err != nil { return nil }
    value := string(output)
    for len(value) > 0 && (value[len(value)-1] == '\n' || value[len(value)-1] == '\r') {
        value = value[:len(value)-1]
    }
    if value == "" { return nil }
    return &value
}

func nativeMaterializeSelection(source, executable string, goos string) []materializeSelection {
    nativeName := "acr-toolbox"
    wrapperName := "analyze.sh"
    if goos == "windows" {
        nativeName = "acr-toolbox.exe"
        wrapperName = "analyze.bat"
    }
    selected := []materializeSelection{{
        Source: executable,
        SourcePath: "<current-executable>",
        Destination: filepath.ToSlash(filepath.Join("bin", nativeName)),
        Role: "native_toolbox",
    }}
    wrapper := filepath.Join(source, "tools", wrapperName)
    if info, err := os.Stat(wrapper); err == nil && info.Mode().IsRegular() {
        selected = append(selected, materializeSelection{
            Source: wrapper,
            SourcePath: filepath.ToSlash(filepath.Join("tools", wrapperName)),
            Destination: wrapperName,
            Role: "entry_wrapper",
        })
    }
    return selected
}

func planNativeMaterialization(out string, selected []materializeSelection, overwrite bool) ([]materializeAction, []string, error) {
    actions := make([]materializeAction, 0, len(selected))
    missing := []string{}
    for _, row := range selected {
        info, err := os.Stat(row.Source)
        if err != nil || !info.Mode().IsRegular() {
            missing = append(missing, row.SourcePath)
            continue
        }
        sourceHash, err := materializeSHA256(row.Source)
        if err != nil { return nil, nil, err }
        destination := filepath.Join(out, filepath.FromSlash(row.Destination))
        state := "missing"
        action := "create"
        if info, err := os.Stat(destination); err == nil {
            if !info.Mode().IsRegular() {
                state, action = "not_a_file", "conflict"
            } else {
                destinationHash, err := materializeSHA256(destination)
                if err != nil { return nil, nil, err }
                if destinationHash == sourceHash {
                    state, action = "identical", "unchanged"
                } else if overwrite {
                    state, action = "different", "overwrite"
                } else {
                    state, action = "different", "conflict"
                }
            }
        } else if !os.IsNotExist(err) {
            return nil, nil, err
        }
        actions = append(actions, materializeAction{
            SourcePath: row.SourcePath,
            DestinationPath: row.Destination,
            Role: row.Role,
            SourceSHA256: sourceHash,
            DestinationState: state,
            PlannedAction: action,
        })
    }
    sort.Strings(missing)
    sort.Slice(actions, func(i, j int) bool { return actions[i].DestinationPath < actions[j].DestinationPath })
    return actions, missing, nil
}

func nativeMaterializeManifest(revision *string, actions []materializeAction) materializeManifest {
    files := make([]materializeManifestFile, 0, len(actions))
    for _, row := range actions {
        files = append(files, materializeManifestFile{
            Path: row.DestinationPath,
            Role: row.Role,
            SourcePath: row.SourcePath,
            SHA256: row.SourceSHA256,
        })
    }
    return materializeManifest{
        Format: materializeManifestFormat,
        ImplementationMode: "native",
        SourceRevision: revision,
        Files: files,
    }
}

func atomicNativeCopy(source, destination string) error {
    if err := os.MkdirAll(filepath.Dir(destination), 0o755); err != nil { return err }
    sourceInfo, err := os.Stat(source)
    if err != nil { return err }
    input, err := os.Open(source)
    if err != nil { return err }
    defer input.Close()
    temporary, err := os.CreateTemp(filepath.Dir(destination), ".acr-copy-*")
    if err != nil { return err }
    temporaryName := temporary.Name()
    defer os.Remove(temporaryName)
    if _, err := io.Copy(temporary, input); err != nil { temporary.Close(); return err }
    if err := temporary.Sync(); err != nil { temporary.Close(); return err }
    if err := temporary.Close(); err != nil { return err }
    if err := os.Chmod(temporaryName, sourceInfo.Mode().Perm()); err != nil { return err }
    return os.Rename(temporaryName, destination)
}

func atomicNativeJSON(path string, payload any) error {
    if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil { return err }
    data, err := json.MarshalIndent(payload, "", "  ")
    if err != nil { return err }
    data = append(data, '\n')
    temporary, err := os.CreateTemp(filepath.Dir(path), ".acr-manifest-*")
    if err != nil { return err }
    temporaryName := temporary.Name()
    defer os.Remove(temporaryName)
    if _, err := temporary.Write(data); err != nil { temporary.Close(); return err }
    if err := temporary.Sync(); err != nil { temporary.Close(); return err }
    if err := temporary.Close(); err != nil { return err }
    return os.Rename(temporaryName, path)
}

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
    if fs.NArg() > 0 { source = fs.Arg(0) }
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
        if os.IsNotExist(err) { status = "input_missing" }
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
        "tool": "materialize-tools",
        "source_root": sourceAbs,
        "output_root": outAbs,
        "implementation_mode": "native",
        "apply_requested": *apply,
        "overwrite_requested": *overwrite,
        "source_revision": revision,
        "manifest_path": filepath.Join(outAbs, materializeManifestName),
        "applied": false,
        "actions": actions,
        "missing_source_files": missing,
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
        if action.PlannedAction == "conflict" { conflicts = append(conflicts, action.DestinationPath) }
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
    for _, row := range selected { sourceByDestination[row.Destination] = row.Source }
    for _, action := range actions {
        if action.PlannedAction != "create" && action.PlannedAction != "overwrite" { continue }
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
