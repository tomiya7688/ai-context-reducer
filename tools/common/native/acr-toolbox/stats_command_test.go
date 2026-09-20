package main

import (
    "encoding/json"
    "os"
    "path/filepath"
    "testing"
)

// TestStatsPortableJSONContract は対象機能の契約と回帰条件が維持されることを確認します。
func TestStatsPortableJSONContract(t *testing.T) {
    root := t.TempDir()
    if err := os.MkdirAll(filepath.Join(root, "src"), 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "src", "main.py"), []byte("a = 1\nprint(a)\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.MkdirAll(filepath.Join(root, "node_modules"), 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "node_modules", "ignored.py"), []byte("print(2)\n"), 0o644); err != nil {
        t.Fatal(err)
    }

    code, payload := captureJSONCommand(t, func() int {
        return cmdStats([]string{"--backend", "portable", root})
    })
    if code != 0 {
        t.Fatalf("unexpected exit code %d: %#v", code, payload)
    }
    if payload["tool"] != "repo-stats" || payload["backend"] != "portable" || payload["status"] != "ok" {
        t.Fatalf("unexpected contract: %#v", payload)
    }
    if payload["recognized_files_seen"] != float64(1) || payload["analyzed_file_count"] != float64(1) || payload["analyzed_line_count"] != float64(2) {
        t.Fatalf("unexpected aggregate: %#v", payload)
    }
    languages := payload["languages"].(map[string]any)
    python := languages["Python"].(map[string]any)
    if python["file_count"] != float64(1) || python["line_count"] != float64(2) {
        t.Fatalf("unexpected Python metrics: %#v", python)
    }
    if python["code_count"] != nil || python["complexity"] != nil {
        t.Fatalf("portable backend should not invent unavailable metrics: %#v", python)
    }
}

// TestStatsExplicitFileLimitIsVisible は対象機能の契約と回帰条件が維持されることを確認します。
func TestStatsExplicitFileLimitIsVisible(t *testing.T) {
    root := t.TempDir()
    if err := os.WriteFile(filepath.Join(root, "big.py"), []byte("1234567890\n"), 0o644); err != nil {
        t.Fatal(err)
    }
    code, payload := captureJSONCommand(t, func() int {
        return cmdStats([]string{"--backend", "portable", "--max-file-bytes", "3", root})
    })
    if code != 0 {
        t.Fatalf("unexpected exit code %d: %#v", code, payload)
    }
    if payload["recognized_files_seen"] != float64(1) || payload["analyzed_file_count"] != float64(0) || payload["oversized_file_count"] != float64(1) {
        t.Fatalf("explicit safety cap must be visible: %#v", payload)
    }
}

// TestParseSCCStatsCompactsAggregateOnly は対象機能の契約と回帰条件が維持されることを確認します。
func TestParseSCCStatsCompactsAggregateOnly(t *testing.T) {
    raw := []byte(`[
        {"Name":"Go","Count":2,"Lines":100,"Bytes":5000,"Code":70,"Comment":20,"Blank":10,"Complexity":9,"Files":[{"Location":"do-not-forward.go"}]},
        {"Name":"Python","Count":1,"Lines":20,"Bytes":800,"Code":15,"Comment":2,"Blank":3,"Complexity":1}
    ]`)
    languages, files, lines, err := parseSCCStats(raw)
    if err != nil {
        t.Fatal(err)
    }
    if files != 3 || lines != 120 {
        t.Fatalf("unexpected totals files=%d lines=%d", files, lines)
    }
    goRow := languages["Go"]
    if goRow.FileCount != 2 || goRow.LineCount != 100 || goRow.CodeCount == nil || *goRow.CodeCount != 70 || goRow.Complexity == nil || *goRow.Complexity != 9 {
        t.Fatalf("unexpected Go row: %#v", goRow)
    }
    encoded, err := json.Marshal(languages)
    if err != nil {
        t.Fatal(err)
    }
    if string(encoded) == "" || containsString(string(encoded), "do-not-forward") {
        t.Fatalf("per-file scc payload must not be forwarded: %s", encoded)
    }
}

// containsString はtest setupや検証を局所化し、各testの意図を読みやすく保ちます。
func containsString(value, needle string) bool {
    for i := 0; i+len(needle) <= len(value); i++ {
        if value[i:i+len(needle)] == needle {
            return true
        }
    }
    return false
}
