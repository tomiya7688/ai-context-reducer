package main

import (
    "encoding/json"
    "io"
    "os"
    "path/filepath"
    "testing"
)

// captureJSONCommand はCLI境界をtest内で再現し、終了状態と出力を検証可能な形で取得します。
func captureJSONCommand(t *testing.T, run func() int) (int, map[string]any) {
    t.Helper()
    previous := os.Stdout
    reader, writer, err := os.Pipe()
    if err != nil {
        t.Fatal(err)
    }
    os.Stdout = writer
    code := run()
    if err := writer.Close(); err != nil {
        t.Fatal(err)
    }
    os.Stdout = previous
    data, err := io.ReadAll(reader)
    if err != nil {
        t.Fatal(err)
    }
    if err := reader.Close(); err != nil {
        t.Fatal(err)
    }
    payload := map[string]any{}
    if err := json.Unmarshal(data, &payload); err != nil {
        t.Fatalf("invalid JSON output %q: %v", string(data), err)
    }
    return code, payload
}

// TestContextEstimateAccurateReadsTextButRemainsApproximate は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestContextEstimateAccurateReadsTextButRemainsApproximate(t *testing.T) {
    root := t.TempDir()
    path := filepath.Join(root, "sample.py")
    if err := os.WriteFile(path, []byte("日本語abc"), 0o644); err != nil {
        t.Fatal(err)
    }
    info, err := os.Stat(path)
    if err != nil {
        t.Fatal(err)
    }
    file := fileInfo{Path: path, Size: info.Size()}

    fast, ok := contextEstimate(file, "fast")
    if !ok {
        t.Fatal("fast estimate unexpectedly failed")
    }
    accurate, ok := contextEstimate(file, "accurate")
    if !ok {
        t.Fatal("accurate estimate unexpectedly failed")
    }
    if fast.EstimatedTokens <= accurate.EstimatedTokens {
        t.Fatalf("expected byte-based fast estimate to exceed rune-based accurate-mode estimate: fast=%d accurate=%d", fast.EstimatedTokens, accurate.EstimatedTokens)
    }
}

// TestContextBudgetCLIReportsApproximationAndExactTruncation は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestContextBudgetCLIReportsApproximationAndExactTruncation(t *testing.T) {
    root := t.TempDir()
    for _, name := range []string{"a.py", "b.py"} {
        if err := os.WriteFile(filepath.Join(root, name), []byte("abcdefgh"), 0o644); err != nil {
            t.Fatal(err)
        }
    }

    code, payload := captureJSONCommand(t, func() int {
        return cmdContextBudget([]string{"--mode", "accurate", "--max-files", "2", root})
    })
    if code != 0 {
        t.Fatalf("unexpected exit code: %d payload=%#v", code, payload)
    }
    if payload["scan_truncated"] != false {
        t.Fatalf("exact-cap scan must not be marked truncated: %#v", payload)
    }
    estimate, ok := payload["token_estimate"].(map[string]any)
    if !ok || estimate["approximate"] != true || estimate["reads_file_contents"] != true {
        t.Fatalf("unexpected token estimate contract: %#v", payload["token_estimate"])
    }

    _, limited := captureJSONCommand(t, func() int {
        return cmdContextBudget([]string{"--max-files", "1", root})
    })
    if limited["scan_truncated"] != true {
        t.Fatalf("scan with additional candidates must be marked truncated: %#v", limited)
    }
}

// TestHotspotScanLimitOnlyMarksRealTruncation は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestHotspotScanLimitOnlyMarksRealTruncation(t *testing.T) {
    root := t.TempDir()
    if err := os.WriteFile(filepath.Join(root, "a.txt"), []byte("a"), 0o644); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "b.txt"), []byte("bb"), 0o644); err != nil {
        t.Fatal(err)
    }
    ignored := filepath.Join(root, "node_modules")
    if err := os.MkdirAll(ignored, 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(ignored, "large.js"), []byte("ignored"), 0o644); err != nil {
        t.Fatal(err)
    }

    rows, statErrors, walkErrors, truncated, err := scanHotspots(root, 2)
    if err != nil {
        t.Fatal(err)
    }
    if len(rows) != 2 || statErrors != 0 || walkErrors != 0 || truncated {
        t.Fatalf("unexpected exact-cap result: rows=%#v stat=%d walk=%d truncated=%v", rows, statErrors, walkErrors, truncated)
    }

    rows, _, _, truncated, err = scanHotspots(root, 1)
    if err != nil {
        t.Fatal(err)
    }
    if len(rows) != 1 || !truncated {
        t.Fatalf("expected real truncation at one file: rows=%#v truncated=%v", rows, truncated)
    }
}
