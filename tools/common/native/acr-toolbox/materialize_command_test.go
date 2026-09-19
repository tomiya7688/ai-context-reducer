package main

import (
    "encoding/json"
    "os"
    "path/filepath"
    "testing"
)

// TestNativeMaterializeSelectionPreservesWrapperLayout は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestNativeMaterializeSelectionPreservesWrapperLayout(t *testing.T) {
    source := t.TempDir()
    wrapper := filepath.Join(source, "tools", "analyze.sh")
    if err := os.MkdirAll(filepath.Dir(wrapper), 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(wrapper, []byte("#!/usr/bin/env sh\n"), 0o755); err != nil {
        t.Fatal(err)
    }
    executable := filepath.Join(source, "acr-toolbox-test")
    if err := os.WriteFile(executable, []byte("binary"), 0o755); err != nil {
        t.Fatal(err)
    }

    rows := nativeMaterializeSelection(source, executable, "linux")
    got := map[string]bool{}
    for _, row := range rows {
        got[row.Destination] = true
    }
    if !got["bin/acr-toolbox"] || !got["analyze.sh"] {
        t.Fatalf("unexpected destinations: %#v", got)
    }
}

// TestPlanNativeMaterializationProtectsDifferentDestination は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestPlanNativeMaterializationProtectsDifferentDestination(t *testing.T) {
    source := t.TempDir()
    out := t.TempDir()
    executable := filepath.Join(source, "acr-toolbox")
    if err := os.WriteFile(executable, []byte("source"), 0o755); err != nil {
        t.Fatal(err)
    }
    destination := filepath.Join(out, "bin", "acr-toolbox")
    if err := os.MkdirAll(filepath.Dir(destination), 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(destination, []byte("local"), 0o755); err != nil {
        t.Fatal(err)
    }

    selected := []materializeSelection{{
        Source:      executable,
        SourcePath:  "<current-executable>",
        Destination: "bin/acr-toolbox",
        Role:        "native_toolbox",
    }}
    actions, missing, err := planNativeMaterialization(out, selected, false)
    if err != nil {
        t.Fatal(err)
    }
    if len(missing) != 0 {
        t.Fatalf("unexpected missing sources: %#v", missing)
    }
    if actions[0].PlannedAction != "conflict" {
        t.Fatalf("expected conflict, got %#v", actions[0])
    }

    overwriteActions, _, err := planNativeMaterialization(out, selected, true)
    if err != nil {
        t.Fatal(err)
    }
    if overwriteActions[0].PlannedAction != "overwrite" {
        t.Fatalf("expected overwrite, got %#v", overwriteActions[0])
    }
}

// TestNativeMaterializeManifestMatchesPythonFormat は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestNativeMaterializeManifestMatchesPythonFormat(t *testing.T) {
    revision := "abc123"
    actions := []materializeAction{{
        SourcePath:       "<current-executable>",
        DestinationPath:  "bin/acr-toolbox",
        Role:             "native_toolbox",
        SourceSHA256:     "deadbeef",
        DestinationState: "missing",
        PlannedAction:    "create",
    }}
    manifest := nativeMaterializeManifest(&revision, actions)
    if manifest.Format != materializeManifestFormat {
        t.Fatalf("unexpected manifest format: %s", manifest.Format)
    }
    if manifest.ImplementationMode != "native" {
        t.Fatalf("unexpected mode: %s", manifest.ImplementationMode)
    }
    if len(manifest.Files) != 1 || manifest.Files[0].Path != "bin/acr-toolbox" {
        t.Fatalf("unexpected manifest files: %#v", manifest.Files)
    }
}

// TestReplaceMaterializedFileReplacesExistingDestination は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestReplaceMaterializedFileReplacesExistingDestination(t *testing.T) {
    root := t.TempDir()
    destination := filepath.Join(root, "tool.bin")
    temporary := filepath.Join(root, "replacement.tmp")
    if err := os.WriteFile(destination, []byte("old"), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(temporary, []byte("new"), 0o644); err != nil {
        t.Fatal(err)
    }

    if err := replaceMaterializedFile(temporary, destination); err != nil {
        t.Fatal(err)
    }
    data, err := os.ReadFile(destination)
    if err != nil {
        t.Fatal(err)
    }
    if string(data) != "new" {
        t.Fatalf("unexpected replacement content: %q", string(data))
    }
    if _, err := os.Stat(temporary); !os.IsNotExist(err) {
        t.Fatalf("temporary file should be consumed, stat err=%v", err)
    }
}

// TestAtomicNativeJSONReplacesExistingManifest は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestAtomicNativeJSONReplacesExistingManifest(t *testing.T) {
    path := filepath.Join(t.TempDir(), materializeManifestName)
    if err := os.WriteFile(path, []byte("old"), 0o644); err != nil {
        t.Fatal(err)
    }
    payload := map[string]any{"format": materializeManifestFormat, "files": []any{}}
    if err := atomicNativeJSON(path, payload); err != nil {
        t.Fatal(err)
    }
    data, err := os.ReadFile(path)
    if err != nil {
        t.Fatal(err)
    }
    decoded := map[string]any{}
    if err := json.Unmarshal(data, &decoded); err != nil {
        t.Fatal(err)
    }
    if decoded["format"] != materializeManifestFormat {
        t.Fatalf("unexpected manifest payload: %#v", decoded)
    }
}
