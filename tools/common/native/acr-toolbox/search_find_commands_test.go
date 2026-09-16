package main

import (
    "os"
    "path/filepath"
    "testing"
)

func TestSearchPortableJSONContract(t *testing.T) {
    root := t.TempDir()
    if err := os.MkdirAll(filepath.Join(root, "src"), 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "src", "a.txt"), []byte("alpha\nneedle here\nomega\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.MkdirAll(filepath.Join(root, "node_modules"), 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "node_modules", "hidden.txt"), []byte("needle hidden\n"), 0o644); err != nil {
        t.Fatal(err)
    }

    code, payload := captureJSONCommand(t, func() int {
        return cmdSearch([]string{"--backend", "portable", "needle", root})
    })
    if code != 0 {
        t.Fatalf("unexpected exit code %d: %#v", code, payload)
    }
    if payload["tool"] != "text-search" || payload["backend"] != "portable" || payload["status"] != "ok" {
        t.Fatalf("unexpected contract: %#v", payload)
    }
    matches, ok := payload["matches"].([]any)
    if !ok || len(matches) != 1 {
        t.Fatalf("expected one non-ignored match: %#v", payload)
    }
    match := matches[0].(map[string]any)
    if match["path"] != "src/a.txt" || match["line"] != float64(2) || match["text"] != "needle here" {
        t.Fatalf("unexpected match: %#v", match)
    }
}

func TestSearchTruncationContextAndInvalidRegex(t *testing.T) {
    root := t.TempDir()
    if err := os.WriteFile(filepath.Join(root, "a.txt"), []byte("before\nneedle one\nafter\nneedle two\n"), 0o644); err != nil {
        t.Fatal(err)
    }

    code, payload := captureJSONCommand(t, func() int {
        return cmdSearch([]string{"--backend", "portable", "--max-results", "1", "--context", "1", "needle", root})
    })
    if code != 0 || payload["matches_truncated"] != true {
        t.Fatalf("expected bounded search: code=%d payload=%#v", code, payload)
    }
    matches := payload["matches"].([]any)
    match := matches[0].(map[string]any)
    before := match["before"].([]any)
    after := match["after"].([]any)
    if before[0].(map[string]any)["text"] != "before" || after[0].(map[string]any)["text"] != "after" {
        t.Fatalf("unexpected context: %#v", match)
    }

    code, payload = captureJSONCommand(t, func() int {
        return cmdSearch([]string{"--backend", "portable", "(", root})
    })
    if code != 2 || payload["status"] != "invalid_pattern" {
        t.Fatalf("invalid regex must not look like empty success: code=%d payload=%#v", code, payload)
    }
}

func TestFindPortableDefaultIsDeepAndPrunesDependencies(t *testing.T) {
    root := t.TempDir()
    deep := root
    for i := 0; i < 24; i++ {
        deep = filepath.Join(deep, "d")
    }
    if err := os.MkdirAll(deep, 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(deep, "target.txt"), []byte("x"), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.MkdirAll(filepath.Join(root, "node_modules"), 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "node_modules", "target.txt"), []byte("x"), 0o644); err != nil {
        t.Fatal(err)
    }

    code, payload := captureJSONCommand(t, func() int {
        return cmdFind([]string{"--backend", "portable", "target.txt", root})
    })
    if code != 0 || payload["scan_truncated"] != false {
        t.Fatalf("unexpected find result: code=%d payload=%#v", code, payload)
    }
    results := payload["results"].([]any)
    if len(results) != 1 {
        t.Fatalf("expected one result: %#v", payload)
    }
    result := results[0].(map[string]any)
    if result["kind"] != "file" {
        t.Fatalf("expected file result: %#v", result)
    }
}

func TestFindSeparatesOutputAndScanTruncation(t *testing.T) {
    root := t.TempDir()
    for _, name := range []string{"a.txt", "b.txt", "c.txt"} {
        if err := os.WriteFile(filepath.Join(root, name), []byte("x"), 0o644); err != nil {
            t.Fatal(err)
        }
    }

    code, payload := captureJSONCommand(t, func() int {
        return cmdFind([]string{"--backend", "portable", "--max-results", "1", "*.txt", root})
    })
    if code != 0 || payload["results_truncated"] != true || payload["scan_truncated"] != false {
        t.Fatalf("output truncation contract mismatch: code=%d payload=%#v", code, payload)
    }

    code, payload = captureJSONCommand(t, func() int {
        return cmdFind([]string{"--backend", "portable", "--max-results", "0", "--max-visited", "1", "*", root})
    })
    if code != 0 || payload["scan_truncated"] != true || payload["status"] != "partial" {
        t.Fatalf("scan truncation contract mismatch: code=%d payload=%#v", code, payload)
    }
}
