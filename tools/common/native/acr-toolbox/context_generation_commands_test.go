package main

import (
    "io"
    "os"
    "path/filepath"
    "strings"
    "testing"
)

// captureTextCommand はCLI境界をtest内で再現し、終了状態と出力を検証可能な形で取得します。
func captureTextCommand(t *testing.T, run func() int) (int, string) {
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
    return code, string(data)
}

// TestContextManifestPriorityMatchesPythonContract は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestContextManifestPriorityMatchesPythonContract(t *testing.T) {
    cases := map[string]string{
        "README.md":         "P0",
        "src/app.py":        "P1",
        "tests/test_app.py": "P2",
        "docs/guide.md":     "P3",
        "assets/logo.svg":   "P4",
    }
    for path, expected := range cases {
        if got := contextManifestPriority(path); got != expected {
            t.Fatalf("priority(%q)=%q want %q", path, got, expected)
        }
    }
}

// TestContextManifestCLIIsBoundedAndSelfDescribing は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestContextManifestCLIIsBoundedAndSelfDescribing(t *testing.T) {
    root := t.TempDir()
    files := map[string]string{
        "README.md": "readme",
        "src/app.py": "print('x')",
        "tests/test_app.py": "test",
    }
    for name, content := range files {
        path := filepath.Join(root, filepath.FromSlash(name))
        if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
            t.Fatal(err)
        }
        if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
            t.Fatal(err)
        }
    }

    code, payload := captureJSONCommand(t, func() int {
        return cmdContextManifest([]string{"--limit", "2", root})
    })
    if code != 0 {
        t.Fatalf("unexpected exit code %d payload=%#v", code, payload)
    }
    if payload["tool"] != "context-manifest" || payload["status"] != "ok" {
        t.Fatalf("unexpected contract: %#v", payload)
    }
    if payload["total_files"] != float64(3) || payload["returned_files"] != float64(2) || payload["files_truncated"] != true {
        t.Fatalf("unexpected counts: %#v", payload)
    }
    rows := payload["files"].([]any)
    first := rows[0].(map[string]any)
    if first["path"] != "README.md" || first["context_priority"] != "P0" {
        t.Fatalf("unexpected first row: %#v", first)
    }
}

// TestContextPackRenderingDistinguishesCleanAndGitFailure は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestContextPackRenderingDistinguishesCleanAndGitFailure(t *testing.T) {
    task := contextPackTask{Goal: "g"}
    clean := renderNativeContextPack(task, contextPackState{ChangedQueryOK: true, StatusQueryOK: true})
    if !strings.Contains(clean, "none detected") || !strings.Contains(clean, "- clean") {
        t.Fatalf("clean state not rendered: %q", clean)
    }

    failed := renderNativeContextPack(task, contextPackState{
        ChangedQueryOK: false,
        StatusQueryOK: false,
        ChangedErrorKind: "git_unavailable",
        StatusErrorKind: "git_query_failed",
    })
    if !strings.Contains(failed, "Git unavailable") || !strings.Contains(failed, "git status query failed") {
        t.Fatalf("failure state not explicit: %q", failed)
    }
    if strings.Contains(failed, "- clean") || strings.Contains(failed, "none detected") {
        t.Fatalf("failure must not look clean: %q", failed)
    }
}

// TestContextPackBoundedLinesNormalizeNegativeLimit は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestContextPackBoundedLinesNormalizeNegativeLimit(t *testing.T) {
    rows, truncated := boundedContextPackLines([]string{"a", "b"}, -1)
    if len(rows) != 0 || !truncated {
        t.Fatalf("negative limit should normalize to zero: rows=%#v truncated=%v", rows, truncated)
    }
    rows, truncated = boundedContextPackLines([]string{"a", "b"}, 2)
    if len(rows) != 2 || truncated {
        t.Fatalf("exact cap must not report truncation: rows=%#v truncated=%v", rows, truncated)
    }
}

// TestContextPackGitUnavailableIsExplicit は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestContextPackGitUnavailableIsExplicit(t *testing.T) {
    t.Setenv("PATH", "")
    result := contextPackGitLines(t.TempDir(), "status", "--short")
    if result.OK || result.ErrorKind != "git_unavailable" {
        t.Fatalf("unexpected result: %#v", result)
    }
}
