package main

import (
    "os"
    "path/filepath"
    "strings"
    "testing"
)

func TestResponsibilityScanExactCapIsNotTruncated(t *testing.T) {
    root := t.TempDir()
    if err := os.WriteFile(filepath.Join(root, "a.py"), []byte("a"), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "b.go"), []byte("bb"), 0o644); err != nil {
        t.Fatal(err)
    }

    rows, scanned, truncated, statErrors, walkErrors, err := scanResponsibilityCandidates(root, 2)
    if err != nil || len(rows) != 2 || scanned != 2 || truncated || statErrors != 0 || walkErrors != 0 {
        t.Fatalf("unexpected exact-cap result rows=%#v scanned=%d truncated=%v stat=%d walk=%d err=%v", rows, scanned, truncated, statErrors, walkErrors, err)
    }
}

func TestResponsibilityScanTruncatesOnlyWithAdditionalCodeFile(t *testing.T) {
    root := t.TempDir()
    if err := os.WriteFile(filepath.Join(root, "a.py"), []byte("a"), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "b.go"), []byte("bb"), 0o644); err != nil {
        t.Fatal(err)
    }

    rows, scanned, truncated, _, _, err := scanResponsibilityCandidates(root, 1)
    if err != nil || len(rows) != 1 || scanned != 1 || !truncated {
        t.Fatalf("expected explicit truncation rows=%#v scanned=%d truncated=%v err=%v", rows, scanned, truncated, err)
    }
}

func TestResponsibilityScanDefaultIsUnlimitedAndIgnoresDependencies(t *testing.T) {
    root := t.TempDir()
    for _, name := range []string{"a.py", "b.go", "c.ts"} {
        if err := os.WriteFile(filepath.Join(root, name), []byte("x"), 0o644); err != nil {
            t.Fatal(err)
        }
    }
    ignored := filepath.Join(root, "node_modules")
    if err := os.MkdirAll(ignored, 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(ignored, "ignored.ts"), []byte("x"), 0o644); err != nil {
        t.Fatal(err)
    }

    rows, scanned, truncated, _, _, err := scanResponsibilityCandidates(root, 0)
    if err != nil || len(rows) != 3 || scanned != 3 || truncated {
        t.Fatalf("unexpected unlimited scan rows=%#v scanned=%d truncated=%v err=%v", rows, scanned, truncated, err)
    }
}

func TestResponsibilityMarkdownIsBoundedAndSelfExplaining(t *testing.T) {
    rows := []responsibilityCandidateRow{
        {Path: "small.py", Size: 1, SizeAvailable: true},
        {Path: "large.py", Size: 20, SizeAvailable: true},
        {Path: "unknown.py", SizeAvailable: false},
    }
    text := renderResponsibilityCandidates(rows, 1, 3, false, 1, 0)
    if !strings.Contains(text, "`large.py`") || strings.Contains(text, "`small.py`") {
        t.Fatalf("unexpected bounded table: %q", text)
    }
    if !strings.Contains(text, "output truncated: 2") || !strings.Contains(text, "stat warnings: 1") || !strings.Contains(text, "scanned code files: 3") {
        t.Fatalf("missing metadata comments: %q", text)
    }
}
