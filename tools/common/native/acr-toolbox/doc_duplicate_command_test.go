package main

import (
    "os"
    "path/filepath"
    "testing"
)

// TestNativeDocDuplicateDetectionIsDeterministic は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestNativeDocDuplicateDetectionIsDeterministic(t *testing.T) {
    text := "This line is deliberately long enough to be considered duplicate content."
    groups := collectNativeDocumentDuplicates([]docDuplicateDocument{
        {Path: "b.md", Lines: []string{text}},
        {Path: "a.md", Lines: []string{text}},
    }, 20)
    if len(groups) != 1 {
        t.Fatalf("expected one duplicate group, got %#v", groups)
    }
    if len(groups[0].Occurrences) != 2 || groups[0].Occurrences[0].Path != "a.md" || groups[0].Occurrences[1].Path != "b.md" {
        t.Fatalf("unexpected deterministic ordering: %#v", groups[0].Occurrences)
    }
}

// TestNativeDocDuplicateCLIZeroLimitsAreUnlimited は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestNativeDocDuplicateCLIZeroLimitsAreUnlimited(t *testing.T) {
    root := t.TempDir()
    text := "This repeated documentation line is intentionally longer than fifty characters.\n"
    if err := os.WriteFile(filepath.Join(root, "a.md"), []byte(text), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "b.md"), []byte(text), 0o644); err != nil {
        t.Fatal(err)
    }
    ignored := filepath.Join(root, "node_modules")
    if err := os.MkdirAll(ignored, 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(ignored, "README.md"), []byte(text), 0o644); err != nil {
        t.Fatal(err)
    }

    code, payload := captureJSONCommand(t, func() int {
        return cmdDocDuplicateHints([]string{"--max-groups", "0", "--max-occurrences-per-group", "0", root})
    })
    if code != 0 {
        t.Fatalf("unexpected exit code %d: %#v", code, payload)
    }
    if payload["discovered_documents"] != float64(2) {
        t.Fatalf("dependency docs should be excluded: %#v", payload)
    }
    if payload["duplicate_group_count_total"] != float64(1) || payload["duplicate_groups_truncated"] != false {
        t.Fatalf("unexpected duplicate group contract: %#v", payload)
    }
    groups, ok := payload["duplicate_groups"].([]any)
    if !ok || len(groups) != 1 {
        t.Fatalf("unexpected groups: %#v", payload["duplicate_groups"])
    }
    group := groups[0].(map[string]any)
    if group["occurrences_truncated"] != false || group["occurrence_count_total"] != float64(2) {
        t.Fatalf("unexpected occurrence contract: %#v", group)
    }
}

// TestNativeDocDuplicateMissingRootIsError は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestNativeDocDuplicateMissingRootIsError(t *testing.T) {
    root := filepath.Join(t.TempDir(), "missing")
    code, payload := captureJSONCommand(t, func() int {
        return cmdDocDuplicateHints([]string{root})
    })
    if code == 0 || payload["status"] != "input_missing" {
        t.Fatalf("missing root must be explicit failure: code=%d payload=%#v", code, payload)
    }
}
