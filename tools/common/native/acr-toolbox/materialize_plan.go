package main

import (
    "crypto/sha256"
    "encoding/hex"
    "os"
    "os/exec"
    "path/filepath"
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
    if err != nil {
        return "", err
    }
    sum := sha256.Sum256(data)
    return hex.EncodeToString(sum[:]), nil
}

func materializeSourceRevision(source string) *string {
    command := exec.Command("git", "-C", source, "rev-parse", "HEAD")
    output, err := command.Output()
    if err != nil {
        return nil
    }
    value := string(output)
    for len(value) > 0 && (value[len(value)-1] == '\n' || value[len(value)-1] == '\r') {
        value = value[:len(value)-1]
    }
    if value == "" {
        return nil
    }
    return &value
}

func nativeMaterializeSelection(source, executable, goos string) []materializeSelection {
    nativeName := "acr-toolbox"
    wrapperName := "analyze.sh"
    if goos == "windows" {
        nativeName = "acr-toolbox.exe"
        wrapperName = "analyze.bat"
    }

    selected := []materializeSelection{{
        Source:      executable,
        SourcePath:  "<current-executable>",
        Destination: filepath.ToSlash(filepath.Join("bin", nativeName)),
        Role:        "native_toolbox",
    }}

    wrapper := filepath.Join(source, "tools", wrapperName)
    if info, err := os.Stat(wrapper); err == nil && info.Mode().IsRegular() {
        selected = append(selected, materializeSelection{
            Source:      wrapper,
            SourcePath:  filepath.ToSlash(filepath.Join("tools", wrapperName)),
            Destination: wrapperName,
            Role:        "entry_wrapper",
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
        if err != nil {
            return nil, nil, err
        }

        destination := filepath.Join(out, filepath.FromSlash(row.Destination))
        state := "missing"
        action := "create"
        if info, err := os.Stat(destination); err == nil {
            if !info.Mode().IsRegular() {
                state, action = "not_a_file", "conflict"
            } else {
                destinationHash, err := materializeSHA256(destination)
                if err != nil {
                    return nil, nil, err
                }
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
            SourcePath:       row.SourcePath,
            DestinationPath:  row.Destination,
            Role:             row.Role,
            SourceSHA256:     sourceHash,
            DestinationState: state,
            PlannedAction:    action,
        })
    }

    sort.Strings(missing)
    sort.Slice(actions, func(i, j int) bool {
        return actions[i].DestinationPath < actions[j].DestinationPath
    })
    return actions, missing, nil
}

func nativeMaterializeManifest(revision *string, actions []materializeAction) materializeManifest {
    files := make([]materializeManifestFile, 0, len(actions))
    for _, row := range actions {
        files = append(files, materializeManifestFile{
            Path:       row.DestinationPath,
            Role:       row.Role,
            SourcePath: row.SourcePath,
            SHA256:     row.SourceSHA256,
        })
    }
    return materializeManifest{
        Format:             materializeManifestFormat,
        ImplementationMode: "native",
        SourceRevision:     revision,
        Files:              files,
    }
}
