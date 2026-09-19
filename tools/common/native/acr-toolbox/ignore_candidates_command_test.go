package main

import (
    "os"
    "path/filepath"
    "testing"
)

// TestNativeIgnoreCandidatesPrunesCandidateDirectory は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestNativeIgnoreCandidatesPrunesCandidateDirectory(t *testing.T) {
    root := t.TempDir()
    nested := filepath.Join(root, "node_modules", "pkg")
    if err := os.MkdirAll(nested, 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(nested, "debug.log"), []byte("x"), 0o644); err != nil {
        t.Fatal(err)
    }
    src := filepath.Join(root, "src")
    if err := os.MkdirAll(src, 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(src, "trace.log"), []byte("x"), 0o644); err != nil {
        t.Fatal(err)
    }

    candidates, errors := scanNativeIgnoreCandidates(root)
    if errors != 0 {
        t.Fatalf("unexpected walk errors: %d", errors)
    }
    if len(candidates) != 2 {
        t.Fatalf("expected two candidates, got %#v", candidates)
    }
    if candidates[0].Path != "node_modules" || candidates[0].Kind != "directory" {
        t.Fatalf("candidate directory must be returned once: %#v", candidates)
    }
    if candidates[1].Path != "src/trace.log" || candidates[1].MatchedRule != "file_extension:.log" {
        t.Fatalf("unexpected file candidate: %#v", candidates[1])
    }
}

// TestNativeIgnoreCandidatesZeroLimitIsUnlimited は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestNativeIgnoreCandidatesZeroLimitIsUnlimited(t *testing.T) {
    root := t.TempDir()
    if err := os.Mkdir(filepath.Join(root, "build"), 0o755); err != nil {
        t.Fatal(err)
    }
    if err := os.WriteFile(filepath.Join(root, "trace.log"), []byte("x"), 0o644); err != nil {
        t.Fatal(err)
    }

    code, payload := captureJSONCommand(t, func() int {
        return cmdIgnoreCandidates([]string{"--limit", "0", root})
    })
    if code != 0 {
        t.Fatalf("unexpected exit code %d: %#v", code, payload)
    }
    if payload["candidate_count_total"] != float64(2) || payload["candidates_truncated"] != false {
        t.Fatalf("unexpected limit contract: %#v", payload)
    }
    if payload["review_required_before_ignoring"] != true {
        t.Fatalf("review requirement must be explicit: %#v", payload)
    }
}

// TestNativeIgnoreCandidatesMissingRootIsError は対象機能の期待contractが将来の変更で崩れないことを検証します。
func TestNativeIgnoreCandidatesMissingRootIsError(t *testing.T) {
    root := filepath.Join(t.TempDir(), "missing")
    code, payload := captureJSONCommand(t, func() int {
        return cmdIgnoreCandidates([]string{root})
    })
    if code == 0 || payload["status"] != "input_missing" {
        t.Fatalf("missing root must fail explicitly: code=%d payload=%#v", code, payload)
    }
}
